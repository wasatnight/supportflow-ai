from PySide6.QtCore import QThread, Qt, Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.dashboard_data import DashboardData
from app.repositories.api_request_repository import ApiRequestRepository
from app.repositories.api_statistics_repository import ApiStatisticsRepository
from app.workers.dashboard_loader_worker import DashboardLoaderWorker


class DashboardPage(QWidget):
    open_requests_requested = Signal()
    open_statistics_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._thread: QThread | None = None
        self._worker: DashboardLoaderWorker | None = None
        self._metric_values: dict[str, QLabel] = {}

        self._build_ui()
        self._apply_styles()
        self._start_loading()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 45, 50, 45)
        main_layout.setSpacing(20)

        title = QLabel("Panel principal")
        title.setObjectName("pageTitle")

        description = QLabel(
            "Vista general del estado actual de las solicitudes."
        )
        description.setObjectName("pageDescription")

        self.refresh_button = QPushButton("Actualizar")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self._start_loading)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(14)

        cards_layout.addWidget(
            self._create_metric_card("total", "Total de solicitudes"),
            0,
            0,
        )
        cards_layout.addWidget(
            self._create_metric_card("new", "Nuevas"),
            0,
            1,
        )
        cards_layout.addWidget(
            self._create_metric_card("progress", "En proceso"),
            0,
            2,
        )
        cards_layout.addWidget(
            self._create_metric_card("resolved", "Resueltas"),
            0,
            3,
        )

        requests_panel = QFrame()
        requests_panel.setObjectName("dashboardPanel")

        requests_layout = QVBoxLayout(requests_panel)
        requests_layout.setContentsMargins(22, 20, 22, 20)
        requests_layout.setSpacing(14)

        requests_title = QLabel("Solicitudes recientes")
        requests_title.setObjectName("sectionTitle")

        view_requests_button = QPushButton("Ver todas")
        view_requests_button.setObjectName("secondaryButton")
        view_requests_button.clicked.connect(self.open_requests_requested.emit)

        requests_header = QHBoxLayout()
        requests_header.addWidget(requests_title)
        requests_header.addStretch()
        requests_header.addWidget(view_requests_button)

        self.requests_table = QTableWidget(0, 6)
        self.requests_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Solicitud",
                "Cliente",
                "Responsable",
                "Estado",
                "Prioridad",
            ]
        )
        self.requests_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.requests_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.requests_table.setAlternatingRowColors(True)
        self.requests_table.verticalHeader().setVisible(False)
        self.requests_table.setMinimumHeight(225)

        table_header = self.requests_table.horizontalHeader()
        table_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        table_header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        for column in (2, 3, 4, 5):
            table_header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        requests_layout.addLayout(requests_header)
        requests_layout.addWidget(self.requests_table)

        actions_panel = QFrame()
        actions_panel.setObjectName("dashboardPanel")

        actions_layout = QHBoxLayout(actions_panel)
        actions_layout.setContentsMargins(22, 16, 22, 16)
        actions_layout.setSpacing(12)

        actions_text = QLabel(
            "Consulta el detalle completo y la distribución por prioridad."
        )
        actions_text.setObjectName("actionText")

        statistics_button = QPushButton("Ver estadísticas")
        statistics_button.setObjectName("secondaryButton")
        statistics_button.clicked.connect(self.open_statistics_requested.emit)

        actions_layout.addWidget(actions_text)
        actions_layout.addStretch()
        actions_layout.addWidget(statistics_button)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(description)
        main_layout.addLayout(cards_layout)
        main_layout.addWidget(requests_panel, 1)
        main_layout.addWidget(actions_panel)

    def _create_metric_card(
        self,
        key: str,
        title: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("metricCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)

        title_label = QLabel(title)
        title_label.setObjectName("metricTitle")

        value_label = QLabel("—")
        value_label.setObjectName("metricValue")

        self._metric_values[key] = value_label

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return card

    @Slot()
    def _start_loading(self) -> None:
        if self._thread is not None:
            return

        self.refresh_button.setDisabled(True)
        self.refresh_button.setText("Actualizando...")

        thread = QThread(self)
        worker = DashboardLoaderWorker(
            ApiStatisticsRepository(),
            ApiRequestRepository(),
        )

        self._thread = thread
        self._worker = worker

        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_dashboard_loaded)
        worker.failed.connect(self._on_dashboard_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_worker_references)

        thread.start()

    @Slot(object)
    def _on_dashboard_loaded(
        self,
        data: DashboardData,
    ) -> None:
        statistics = data.statistics

        self._metric_values["total"].setText(str(statistics.total_requests))
        self._metric_values["new"].setText(
            str(statistics.status_counts.get("Nueva", 0))
        )
        self._metric_values["progress"].setText(
            str(statistics.status_counts.get("En proceso", 0))
        )
        self._metric_values["resolved"].setText(
            str(statistics.status_counts.get("Resuelta", 0))
        )

        self.requests_table.setRowCount(len(data.recent_requests))

        status_colors = {
            "Nueva": QColor("#2563eb"),
            "En proceso": QColor("#b45309"),
            "Resuelta": QColor("#047857"),
        }
        priority_colors = {
            "Alta": QColor("#dc2626"),
            "Media": QColor("#b45309"),
            "Baja": QColor("#047857"),
        }

        for row, request in enumerate(data.recent_requests):
            values = (
                request.request_id,
                request.subject,
                request.customer,
                request.assignee or "Sin asignar",
                request.status,
                request.priority,
            )

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setForeground(QColor("#344054"))

                if column == 4:
                    item.setForeground(
                        status_colors.get(value, QColor("#344054"))
                    )
                elif column == 5:
                    item.setForeground(
                        priority_colors.get(value, QColor("#344054"))
                    )

                if column in (4, 5):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.requests_table.setItem(row, column, item)

    @Slot(str)
    def _on_dashboard_failed(self, message: str) -> None:
        QMessageBox.warning(
            self,
            "Panel no disponible",
            message,
        )

    @Slot()
    def _clear_worker_references(self) -> None:
        self._worker = None
        self._thread = None

        self.refresh_button.setDisabled(False)
        self.refresh_button.setText("Actualizar")

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            #metricCard,
            #dashboardPanel {
                background-color: #ffffff;
                border: 1px solid #e4e7ec;
                border-radius: 10px;
            }

            #metricTitle {
                color: #667085;
                font-size: 13px;
            }

            #metricValue {
                color: #172033;
                font-size: 26px;
                font-weight: 700;
            }

            #sectionTitle {
                color: #344054;
                font-size: 15px;
                font-weight: 700;
            }

            #actionText {
                color: #667085;
                font-size: 13px;
            }

            #primaryButton {
                background-color: #526df5;
                color: #ffffff;
                border: none;
                border-radius: 7px;
                padding: 9px 15px;
            }

            #primaryButton:hover {
                background-color: #4058d8;
            }

            #secondaryButton {
                background-color: #ffffff;
                color: #526df5;
                border: 1px solid #c7d0ff;
                border-radius: 7px;
                padding: 8px 13px;
            }

            #secondaryButton:hover {
                background-color: #f2f4ff;
            }

            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8f9fc;
                color: #344054;
                selection-background-color: #e8ecff;
                selection-color: #172033;
                border: 1px solid #e4e7ec;
                border-radius: 7px;
                gridline-color: #eaecf0;
                outline: none;
            }

            QTableWidget::item:selected {
                background-color: #e8ecff;
                color: #172033;
            }

            QHeaderView::section {
                background-color: #f8f9fc;
                color: #475467;
                border: none;
                border-bottom: 1px solid #e4e7ec;
                padding: 8px;
                font-weight: 600;
            }
        """)
