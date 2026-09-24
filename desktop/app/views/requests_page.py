from PySide6.QtCore import QThread, Qt, Slot
from app.repositories.in_memory_request_repository import (
    InMemoryRequestRepository,
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QDialog,
)

from app.views.request_detail_dialog import RequestDetailDialog

from app.views.new_request_dialog import NewRequestDialog

from app.repositories.api_request_repository import (
    ApiRequestRepository,
)

from app.models.support_request import SupportRequest
from app.workers.request_loader_worker import RequestLoaderWorker
from app.workers.request_create_worker import RequestCreateWorker
from app.workers.request_update_worker import RequestUpdateWorker
from app.workers.request_delete_worker import RequestDeleteWorker


class RequestsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._requests: list[SupportRequest] = []

        self._thread: QThread | None = None
        self._worker: RequestLoaderWorker | None = None
        self._create_thread: QThread | None = None
        self._create_worker: RequestCreateWorker | None = None
        self._update_thread: QThread | None = None
        self._update_worker: RequestUpdateWorker | None = None
        self._delete_thread: QThread | None = None
        self._delete_worker: RequestDeleteWorker | None = None

        self._build_ui()
        self._load_requests()
        self._apply_styles()
        self._start_loading()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 45, 50, 45)
        layout.setSpacing(20)

        title = QLabel("Solicitudes")
        title.setObjectName("pageTitle")

        description = QLabel("Revisa, busca y filtra las solicitudes de los clientes.")
        description.setObjectName("pageDescription")

        self.new_request_button = QPushButton("Nueva solicitud")
        self.new_request_button.setObjectName("primaryButton")
        self.new_request_button.clicked.connect(self._open_new_request_dialog)

        title_layout = QHBoxLayout()
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.new_request_button)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Buscar por asunto, cliente o identificador..."
        )
        self.search_input.setClearButtonEnabled(True)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            [
                "Todos los estados",
                "Nueva",
                "En proceso",
                "Resuelta",
            ]
        )

        self.assignee_filter = QComboBox()
        self.assignee_filter.addItem("Todos los responsables")

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(12)
        filters_layout.addWidget(self.search_input, 1)
        filters_layout.addWidget(self.status_filter)
        filters_layout.addWidget(self.assignee_filter)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Solicitud",
                "Cliente",
                "Responsable",
                "Estado",
                "Prioridad",
            ]
        )

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        self.table.setToolTip("Haz doble clic en una solicitud para ver sus detalles.")

        self.table.cellDoubleClicked.connect(self._open_request_detail)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        layout.addLayout(title_layout)
        layout.addWidget(description)
        layout.addLayout(filters_layout)
        layout.addWidget(self.table, 1)

        self.search_input.textChanged.connect(self._apply_filters)
        self.status_filter.currentTextChanged.connect(self._apply_filters)
        self.assignee_filter.currentTextChanged.connect(self._apply_filters)

    @Slot()
    def _open_new_request_dialog(self) -> None:
        dialog = NewRequestDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._start_creating(dialog.get_request())

    def _start_creating(
        self,
        request: SupportRequest,
    ) -> None:
        self.new_request_button.setDisabled(True)

        thread = QThread(self)
        worker = RequestCreateWorker(
            ApiRequestRepository(),
            request,
        )

        self._create_thread = thread
        self._create_worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_request_created)
        worker.failed.connect(self._on_request_creation_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_create_references)

        thread.start()

    @Slot(object)
    def _on_request_created(
        self,
        request: SupportRequest,
    ) -> None:
        self._requests.append(request)
        self._refresh_assignee_filter()
        self._load_requests()
        self._apply_filters()

        QMessageBox.information(
            self,
            "Solicitud creada",
            f"La solicitud {request.request_id} fue creada correctamente.",
        )

    @Slot(str)
    def _on_request_creation_failed(
        self,
        message: str,
    ) -> None:
        QMessageBox.warning(
            self,
            "No fue posible crear la solicitud",
            message,
        )

    @Slot()
    def _clear_create_references(self) -> None:
        self._create_worker = None
        self._create_thread = None
        self.new_request_button.setEnabled(True)

    def _start_loading(self) -> None:
        self._set_loading_state(True)

        thread = QThread(self)
        worker = RequestLoaderWorker(ApiRequestRepository())

        self._thread = thread
        self._worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_requests_loaded)
        worker.failed.connect(self._on_requests_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_loader_references)

        thread.start()

    @Slot(list)
    def _on_requests_loaded(
        self,
        requests: list[SupportRequest],
    ) -> None:
        self._requests = requests
        self._refresh_assignee_filter()
        self._load_requests()
        self._set_loading_state(False)

    @Slot(str)
    def _on_requests_failed(
        self,
        message: str,
    ) -> None:
        repository = InMemoryRequestRepository()

        self._requests = repository.list_all()
        self._refresh_assignee_filter()
        self._load_requests()
        self._set_loading_state(False)

        QMessageBox.warning(
            self,
            "Servidor no disponible",
            (f"{message}\n\n" "Se mostrarán datos locales temporalmente."),
        )

    @Slot()
    def _clear_loader_references(self) -> None:
        self._worker = None
        self._thread = None

    def _set_loading_state(
        self,
        is_loading: bool,
    ) -> None:
        self.table.setDisabled(is_loading)
        self.search_input.setDisabled(is_loading)
        self.status_filter.setDisabled(is_loading)
        self.assignee_filter.setDisabled(is_loading)

        if is_loading:
            self.table.setRowCount(0)

    def _load_requests(self) -> None:
        self.table.setRowCount(len(self._requests))

        for row, request in enumerate(self._requests):
            values = [
                request.request_id,
                request.subject,
                request.customer,
                request.assignee or "Sin asignar",
                request.status,
                request.priority,
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                if column == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.table.setItem(row, column, item)

            priority_item = self.table.item(row, 5)
            self._apply_priority_color(
                priority_item,
                request.priority,
            )

    def _refresh_assignee_filter(self) -> None:
        current_value = self.assignee_filter.currentText()
        assignees = sorted(
            {
                request.assignee
                for request in self._requests
                if request.assignee
            }
        )

        self.assignee_filter.blockSignals(True)
        self.assignee_filter.clear()
        self.assignee_filter.addItems(
            [
                "Todos los responsables",
                "Sin asignar",
                *assignees,
            ]
        )

        restored_index = self.assignee_filter.findText(current_value)
        self.assignee_filter.setCurrentIndex(
            restored_index if restored_index >= 0 else 0
        )
        self.assignee_filter.blockSignals(False)

    def _apply_priority_color(
        self,
        item: QTableWidgetItem,
        priority: str,
    ) -> None:
        colors = {
            "Alta": ("#fee2e2", "#991b1b"),
            "Media": ("#fef3c7", "#92400e"),
            "Baja": ("#dcfce7", "#166534"),
        }

        background, foreground = colors[priority]

        item.setBackground(QColor(background))
        item.setForeground(QColor(foreground))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def _apply_filters(self, *_: object) -> None:
        search_text = self.search_input.text().strip().casefold()
        selected_status = self.status_filter.currentText()
        selected_assignee = self.assignee_filter.currentText()

        for row, request in enumerate(self._requests):
            searchable_text = " ".join(
                [
                    request.request_id,
                    request.subject,
                    request.customer,
                    request.assignee or "Sin asignar",
                ]
            ).casefold()

            matches_search = search_text in searchable_text

            matches_status = (
                selected_status == "Todos los estados"
                or request.status == selected_status
            )

            request_assignee = request.assignee or "Sin asignar"
            matches_assignee = (
                selected_assignee == "Todos los responsables"
                or request_assignee == selected_assignee
            )

            self.table.setRowHidden(
                row,
                not (
                    matches_search
                    and matches_status
                    and matches_assignee
                ),
            )

    def _open_request_detail(
        self,
        row: int,
        _: int,
    ) -> None:
        request = self._requests[row]

        dialog = RequestDetailDialog(
            request_id=request.request_id,
            subject=request.subject,
            customer=request.customer,
            status=request.status,
            priority=request.priority,
            assignee=request.assignee,
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        if dialog.should_delete():
            self._start_deleting(request.request_id)
            return

        new_status = dialog.get_status()
        new_priority = dialog.get_priority()
        new_assignee = dialog.get_assignee()

        if (
            new_status == request.status
            and new_priority == request.priority
            and new_assignee == request.assignee
        ):
            return

        self._start_updating(
            request_id=request.request_id,
            status=new_status,
            priority=new_priority,
            assignee=new_assignee,
        )

    def _start_updating(
        self,
        request_id: str,
        status: str,
        priority: str,
        assignee: str | None,
    ) -> None:
        self.table.setDisabled(True)
        self.new_request_button.setDisabled(True)

        thread = QThread(self)
        worker = RequestUpdateWorker(
            repository=ApiRequestRepository(),
            request_id=request_id,
            status=status,
            priority=priority,
            assignee=assignee,
        )

        self._update_thread = thread
        self._update_worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_request_updated)
        worker.failed.connect(self._on_request_update_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_update_references)

        thread.start()

    @Slot(object)
    def _on_request_updated(
        self,
        updated_request: SupportRequest,
    ) -> None:
        for index, request in enumerate(self._requests):
            if request.request_id == updated_request.request_id:
                self._requests[index] = updated_request
                break

        self._load_requests()
        self._refresh_assignee_filter()
        self._apply_filters()

        QMessageBox.information(
            self,
            "Solicitud actualizada",
            (
                f"La solicitud "
                f"{updated_request.request_id} "
                "fue actualizada correctamente."
            ),
        )

    @Slot(str)
    def _on_request_update_failed(
        self,
        message: str,
    ) -> None:
        QMessageBox.warning(
            self,
            "No fue posible actualizar",
            message,
        )

    @Slot()
    def _clear_update_references(self) -> None:
        self._update_worker = None
        self._update_thread = None

        self.table.setEnabled(True)
        self.new_request_button.setEnabled(True)

    def _start_deleting(
        self,
        request_id: str,
    ) -> None:
        self.table.setDisabled(True)
        self.new_request_button.setDisabled(True)

        thread = QThread(self)
        worker = RequestDeleteWorker(
            repository=ApiRequestRepository(),
            request_id=request_id,
        )

        self._delete_thread = thread
        self._delete_worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_request_deleted)
        worker.failed.connect(self._on_request_delete_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_delete_references)

        thread.start()

    @Slot(str)
    def _on_request_deleted(
        self,
        request_id: str,
    ) -> None:
        self._requests = [
            request for request in self._requests if request.request_id != request_id
        ]

        self._refresh_assignee_filter()
        self._load_requests()
        self._apply_filters()

        QMessageBox.information(
            self,
            "Solicitud eliminada",
            (f"La solicitud {request_id} " "fue eliminada correctamente."),
        )

    @Slot(str)
    def _on_request_delete_failed(
        self,
        message: str,
    ) -> None:
        QMessageBox.warning(
            self,
            "No fue posible eliminar",
            message,
        )

    @Slot()
    def _clear_delete_references(self) -> None:
        self._delete_worker = None
        self._delete_thread = None

        self.table.setEnabled(True)
        self.new_request_button.setEnabled(True)

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QLineEdit,
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #d0d5dd;
                border-radius: 7px;
                padding: 9px 12px;
                color: #172033;
                font-size: 13px;
            }

            QLineEdit:focus,
            QComboBox:focus {
                border: 1px solid #526df5;
            }

            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #172033;
                selection-background-color: #dbe5ff;
                selection-color: #172033;
                border: 1px solid #d0d5dd;
                outline: none;
            }

            QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 4px 10px;
                color: #172033;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #eef2ff;
                color: #172033;
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #526df5;
                color: #ffffff;
            }

            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8fafc;
                border: 1px solid #e4e7ec;
                border-radius: 8px;
                gridline-color: #eaecf0;
                color: #344054;
                font-size: 13px;
                outline: none;
                selection-background-color: #dbe5ff;
                selection-color: #172033;
            }

            QTableWidget::item {
                padding: 8px;
                border: none;
            }

            QTableWidget::item:hover {
                background-color: #eef2ff;
                color: #172033;
            }

            QTableWidget::item:selected,
            QTableWidget::item:selected:hover {
                background-color: #dbe5ff;
                color: #172033;
            }

            QTableWidget::item:focus {
                border: none;
                outline: none;
            }

            QHeaderView::section {
                background-color: #f8fafc;
                color: #475467;
                border: none;
                border-bottom: 1px solid #e4e7ec;
                padding: 10px;
                font-weight: 600;
            }
                        QPushButton#primaryButton {
                background-color: #526df5;
                color: #ffffff;
                border: none;
                border-radius: 7px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#primaryButton:hover {
                background-color: #4058d6;
            }

            QPushButton#primaryButton:pressed {
                background-color: #3448b8;
            }

            QPushButton#primaryButton:disabled {
                background-color: #aab4e8;
                color: #ffffff;
            }
            """)
