from datetime import datetime

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QMessageBox,
    QListWidgetItem,
)

from PySide6.QtCore import QSize, QThread, Qt, Slot
from app.models.support_message import SupportMessage
from app.repositories.api_message_repository import (
    ApiMessageRepository,
)
from app.repositories.api_ai_repository import (
    ApiAiRepository,
)
from app.workers.message_loader_worker import (
    MessageLoaderWorker,
)
from app.workers.message_create_worker import (
    MessageCreateWorker,
)
from app.workers.ai_suggestion_worker import (
    AiSuggestionWorker,
)


class RequestDetailDialog(QDialog):
    def __init__(
        self,
        request_id: str,
        subject: str,
        customer: str,
        status: str,
        priority: str,
        assignee: str | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.request_id = request_id
        self.subject = subject
        self.customer = customer
        self.status = status
        self.priority = priority
        self.assignee = assignee

        self._message_load_thread: QThread | None = None
        self._message_load_worker: MessageLoaderWorker | None = None
        self._message_create_thread: QThread | None = None
        self._message_create_worker: MessageCreateWorker | None = None
        self._ai_thread: QThread | None = None
        self._ai_worker: AiSuggestionWorker | None = None

        self.setWindowTitle(f"{request_id} - Detalle")
        self.resize(760, 700)
        self.setMinimumSize(680, 620)
        self.setModal(True)

        self._build_ui()
        self._apply_styles()
        self._delete_requested = False
        self._start_loading_messages()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 28, 30, 28)
        main_layout.setSpacing(18)

        request_label = QLabel(
            f"{self.request_id} · {self.status} · Prioridad {self.priority}"
        )
        request_label.setObjectName("requestLabel")

        title_label = QLabel(self.subject)
        title_label.setObjectName("dialogTitle")
        title_label.setWordWrap(True)

        self.status_input = QComboBox()
        self.status_input.addItems(["Nueva", "En proceso", "Resuelta"])
        self.status_input.setCurrentText(self.status)

        self.priority_input = QComboBox()
        self.priority_input.addItems(["Alta", "Media", "Baja"])
        self.priority_input.setCurrentText(self.priority)

        self.assignee_input = QComboBox()
        self.assignee_input.setEditable(True)
        self.assignee_input.addItems(
            [
                "Sin asignar",
                "Empleado conectado",
            ]
        )
        self.assignee_input.setCurrentText(
            self.assignee or "Sin asignar"
        )

        information_layout = QFormLayout()
        information_layout.setSpacing(10)

        information_layout.addRow(
            "Cliente:",
            QLabel(self.customer),
        )
        information_layout.addRow(
            "Estado:",
            self.status_input,
        )
        information_layout.addRow(
            "Prioridad:",
            self.priority_input,
        )

        information_layout.addRow(
            "Responsable:",
            self.assignee_input,
        )

        conversation_title = QLabel("Conversación")
        conversation_title.setObjectName("sectionTitle")

        self.conversation = QListWidget()
        self.conversation.setWordWrap(True)
        self.conversation.setUniformItemSizes(False)
        self.conversation.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.conversation.setMinimumHeight(170)
        self.conversation.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.conversation.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._append_message(
            sender="Cliente",
            content=self.subject,
        )

        response_title = QLabel("Responder al cliente")
        response_title.setObjectName("sectionTitle")

        self.ai_button = QPushButton("Sugerir con IA")
        self.ai_button.setObjectName("aiButton")
        self.ai_button.clicked.connect(self._start_ai_suggestion)

        response_header = QHBoxLayout()
        response_header.addWidget(response_title)
        response_header.addStretch()
        response_header.addWidget(self.ai_button)

        self.response_input = QTextEdit()
        self.response_input.setPlaceholderText("Escribe una respuesta...")
        self.response_input.setFixedHeight(100)

        self.send_button = QPushButton("Enviar respuesta")
        self.send_button.setObjectName("primaryButton")
        self.send_button.clicked.connect(self._add_response)

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Guardar cambios")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self.accept)

        delete_button = QPushButton("Eliminar solicitud")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self._confirm_delete)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(self.send_button)
        buttons_layout.addWidget(save_button)
        main_layout.addWidget(request_label)
        main_layout.addWidget(title_label)
        main_layout.addLayout(information_layout)
        main_layout.addWidget(conversation_title)
        main_layout.addWidget(self.conversation, 1)
        main_layout.addLayout(response_header)
        main_layout.addWidget(self.response_input)
        main_layout.addLayout(buttons_layout)

    def _append_message(
        self,
        sender: str,
        content: str,
        created_at: str = "",
    ) -> None:
        timestamp = self._format_message_time(created_at)

        header = sender

        if timestamp:
            header = f"{sender} · {timestamp}"

        item = QListWidgetItem(f"{header}\n{content}")

        estimated_lines = max(
            1,
            (len(content) + 54) // 55,
        )

        item_height = 52 + (estimated_lines * 22)

        item.setSizeHint(QSize(0, item_height))

        colors = {
            "Cliente": ("#eef2ff", "#344054"),
            "Empleado": ("#dcfae6", "#067647"),
            "IA": ("#f4ebff", "#6941c6"),
        }

        background, foreground = colors.get(
            sender,
            ("#f2f4f7", "#344054"),
        )

        item.setBackground(QColor(background))
        item.setForeground(QColor(foreground))

        if sender == "Empleado":
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
        else:
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )

        self.conversation.addItem(item)

    @staticmethod
    def _format_message_time(
        created_at: str,
    ) -> str:
        if not created_at:
            return ""

        try:
            value = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            return created_at

        return value.astimezone().strftime("%d/%m/%Y %H:%M")

    def _start_ai_suggestion(self) -> None:
        if self._ai_thread is not None:
            return

        current_text = self.response_input.toPlainText().strip()

        if current_text:
            answer = QMessageBox.question(
                self,
                "Reemplazar respuesta",
                (
                    "La sugerencia de IA reemplazará el "
                    "texto actual.\n\n¿Deseas continuar?"
                ),
                (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
                QMessageBox.StandardButton.No,
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

        self.ai_button.setDisabled(True)
        self.ai_button.setText("Generando...")
        self.response_input.setDisabled(True)

        thread = QThread(self)
        worker = AiSuggestionWorker(
            ApiAiRepository(),
            self.request_id,
        )

        self._ai_thread = thread
        self._ai_worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_ai_suggestion_generated)
        worker.failed.connect(self._on_ai_suggestion_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_ai_references)

        thread.start()

    @Slot(str)
    def _on_ai_suggestion_generated(
        self,
        suggestion: str,
    ) -> None:
        self.response_input.setPlainText(suggestion)
        self.response_input.setFocus()

    @Slot(str)
    def _on_ai_suggestion_failed(
        self,
        message: str,
    ) -> None:
        QMessageBox.warning(
            self,
            "IA no disponible",
            message,
        )

    @Slot()
    def _clear_ai_references(self) -> None:
        self._ai_worker = None
        self._ai_thread = None

        self.ai_button.setDisabled(False)
        self.ai_button.setText("Sugerir con IA")
        self.response_input.setDisabled(False)
        self.response_input.setFocus()

    def _add_response(self) -> None:
        content = self.response_input.toPlainText().strip()

        if not content:
            self.response_input.setFocus()
            return

        if self._message_create_thread is not None:
            return

        self.send_button.setDisabled(True)
        self.response_input.setDisabled(True)

        thread = QThread(self)
        worker = MessageCreateWorker(
            ApiMessageRepository(),
            self.request_id,
            content,
        )

        self._message_create_thread = thread
        self._message_create_worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_message_created)
        worker.failed.connect(self._on_message_creation_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_message_creator_references)

        thread.start()

    @Slot(object)
    def _on_message_created(
        self,
        message: SupportMessage,
    ) -> None:
        self._append_message(
            sender=message.sender,
            content=message.content,
            created_at=message.created_at,
        )

        self.response_input.clear()
        self.conversation.scrollToBottom()

    @Slot(str)
    def _on_message_creation_failed(
        self,
        message: str,
    ) -> None:
        QMessageBox.warning(
            self,
            "No se pudo enviar",
            message,
        )

    @Slot()
    def _clear_message_creator_references(self) -> None:
        self._message_create_worker = None
        self._message_create_thread = None

        self.send_button.setDisabled(False)
        self.response_input.setDisabled(False)
        self.response_input.setFocus()

    def _start_loading_messages(self) -> None:
        self.conversation.setDisabled(True)

        thread = QThread(self)
        worker = MessageLoaderWorker(
            ApiMessageRepository(),
            self.request_id,
        )

        self._message_load_thread = thread
        self._message_load_worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_messages_loaded)
        worker.failed.connect(self._on_messages_load_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_message_loader_references)

        thread.start()

    @Slot(list)
    def _on_messages_loaded(
        self,
        messages: list[SupportMessage],
    ) -> None:
        for message in messages:
            self._append_message(
                sender=message.sender,
                content=message.content,
                created_at=message.created_at,
            )

        self.conversation.setDisabled(False)
        self.conversation.scrollToBottom()

    @Slot(str)
    def _on_messages_load_failed(
        self,
        message: str,
    ) -> None:
        self.conversation.setDisabled(False)

        QMessageBox.warning(
            self,
            "Conversación no disponible",
            message,
        )

    @Slot()
    def _clear_message_loader_references(self) -> None:
        self._message_load_worker = None
        self._message_load_thread = None

    def _confirm_delete(self) -> None:
        answer = QMessageBox.question(
            self,
            "Eliminar solicitud",
            (
                f"¿Seguro que deseas eliminar "
                f"{self.request_id}?\n\n"
                "Esta acción no se puede deshacer."
            ),
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self._delete_requested = True
        self.accept()

    def should_delete(self) -> bool:
        return self._delete_requested

    def get_status(self) -> str:
        return self.status_input.currentText()

    def get_priority(self) -> str:
        return self.priority_input.currentText()

    def get_assignee(self) -> str | None:
        assignee = self.assignee_input.currentText().strip()

        if not assignee or assignee == "Sin asignar":
            return None

        return assignee

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QDialog {
                background-color: #f4f6fa;
            }

            QLabel {
                color: #344054;
            }

            #requestLabel {
                color: #667085;
                font-size: 12px;
                font-weight: 600;
            }

            #dialogTitle {
                color: #172033;
                font-size: 23px;
                font-weight: 700;
            }

            #sectionTitle {
                color: #344054;
                font-size: 14px;
                font-weight: 700;
            }

            QListWidget,
            QTextEdit {
                background-color: #ffffff;
                color: #344054;
                border: 1px solid #d0d5dd;
                border-radius: 8px;
                padding: 8px;
            }

            QListWidget::item {
                border: none;
                border-radius: 7px;
                margin: 4px;
                padding: 10px;
            }

            QPushButton {
                background-color: #ffffff;
                color: #344054;
                border: 1px solid #d0d5dd;
                border-radius: 7px;
                padding: 9px 15px;
            }

            QPushButton:hover {
                background-color: #f2f4f7;
            }

            #primaryButton {
                background-color: #526df5;
                color: #ffffff;
                border: none;
            }

            #primaryButton:hover {
                background-color: #4058d8;
            }
            QComboBox {
                background-color: #ffffff;
                color: #172033;
                border: 1px solid #d0d5dd;
                border-radius: 7px;
                padding: 7px 10px;
                min-width: 150px;
            }

            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #172033;
                selection-background-color: #526df5;
                selection-color: #ffffff;
                outline: none;
            }

            #aiButton {
                background-color: #f4ebff;
                color: #6941c6;
                border: 1px solid #d6bbfb;
            }

            #aiButton:hover {
                background-color: #e9d7fe;
                border-color: #b692f6;
            }

            #dangerButton {
                background-color: #ffffff;
                color: #b42318;
                border: 1px solid #fda29b;
            }

            #dangerButton:hover {
                background-color: #fee4e2;
                border-color: #f97066;
            }
            """)
