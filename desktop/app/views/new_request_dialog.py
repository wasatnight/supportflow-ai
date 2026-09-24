from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from app.models.support_request import SupportRequest


class NewRequestDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Nueva solicitud")
        self.setMinimumWidth(460)
        self.setStyleSheet("""
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
        """)

        self.request_id_input = QLineEdit()
        self.request_id_input.setPlaceholderText("Ejemplo: SOL-006")

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Describe brevemente el problema")

        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Nombre del cliente")

        self.status_input = QComboBox()
        self.status_input.addItems(["Nueva", "En proceso", "Resuelta"])

        self.priority_input = QComboBox()
        self.priority_input.addItems(["Alta", "Media", "Baja"])

        form_layout = QFormLayout()
        form_layout.addRow("Identificador:", self.request_id_input)
        form_layout.addRow("Asunto:", self.subject_input)
        form_layout.addRow("Cliente:", self.customer_input)
        form_layout.addRow("Estado:", self.status_input)
        form_layout.addRow("Prioridad:", self.priority_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(buttons)

        save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)

        if save_button is not None:
            save_button.setText("Guardar")

        if cancel_button is not None:
            cancel_button.setText("Cancelar")

    def _validate_and_accept(self) -> None:
        request_id = self.request_id_input.text().strip()
        subject = self.subject_input.text().strip()
        customer = self.customer_input.text().strip()

        if not request_id or len(subject) < 3 or len(customer) < 2:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                ("Completa el identificador, el asunto " "y el nombre del cliente."),
            )
            return

        self.accept()

    def get_request(self) -> SupportRequest:
        return SupportRequest(
            request_id=self.request_id_input.text().strip(),
            subject=self.subject_input.text().strip(),
            customer=self.customer_input.text().strip(),
            status=self.status_input.currentText(),
            priority=self.priority_input.currentText(),
        )
