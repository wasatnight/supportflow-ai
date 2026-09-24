from PySide6.QtCore import QThread, Slot
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.statistics_summary import (
    StatisticsSummary,
)
from app.repositories.api_statistics_repository import (
    ApiStatisticsRepository,
)
from app.workers.statistics_loader_worker import (
    StatisticsLoaderWorker,
)


class StatisticsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._thread: QThread | None = None
        self._worker: StatisticsLoaderWorker | None = None

        self._metric_values: dict[str, QLabel] = {}
        self._priority_bars: dict[str, QProgressBar] = {}

        self._build_ui()
        self._apply_styles()
        self._start_loading()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 45, 50, 45)
        main_layout.setSpacing(22)

        title = QLabel("Estadísticas")
        title.setObjectName("pageTitle")

        description = QLabel("Resumen actualizado de las solicitudes.")
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
            self._create_metric_card(
                "total",
                "Total de solicitudes",
            ),
            0,
            0,
        )
        cards_layout.addWidget(
            self._create_metric_card(
                "new",
                "Nuevas",
            ),
            0,
            1,
        )
        cards_layout.addWidget(
            self._create_metric_card(
                "progress",
                "En proceso",
            ),
            0,
            2,
        )
        cards_layout.addWidget(
            self._create_metric_card(
                "resolved",
                "Resueltas",
            ),
            1,
            0,
        )
        cards_layout.addWidget(
            self._create_metric_card(
                "percentage",
                "Porcentaje resuelto",
            ),
            1,
            1,
        )

        priority_panel = QFrame()
        priority_panel.setObjectName("panel")

        priority_layout = QVBoxLayout(priority_panel)
        priority_layout.setContentsMargins(
            22,
            20,
            22,
            20,
        )
        priority_layout.setSpacing(14)

        priority_title = QLabel("Solicitudes por prioridad")
        priority_title.setObjectName("sectionTitle")

        priority_layout.addWidget(priority_title)

        for priority in ("Alta", "Media", "Baja"):
            label = QLabel(priority)
            label.setObjectName("priorityLabel")

            progress = QProgressBar()
            progress.setRange(0, 1)
            progress.setValue(0)
            progress.setFormat("0")

            self._priority_bars[priority] = progress

            priority_layout.addWidget(label)
            priority_layout.addWidget(progress)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(description)
        main_layout.addLayout(cards_layout)
        main_layout.addWidget(priority_panel)
        main_layout.addStretch()

    def _create_metric_card(
        self,
        key: str,
        title: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("metricCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)

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
        worker = StatisticsLoaderWorker(ApiStatisticsRepository())

        self._thread = thread
        self._worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._on_statistics_loaded)
        worker.failed.connect(self._on_statistics_failed)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_worker_references)

        thread.start()

    @Slot(object)
    def _on_statistics_loaded(
        self,
        summary: StatisticsSummary,
    ) -> None:
        self._metric_values["total"].setText(str(summary.total_requests))
        self._metric_values["new"].setText(str(summary.status_counts.get("Nueva", 0)))
        self._metric_values["progress"].setText(
            str(
                summary.status_counts.get(
                    "En proceso",
                    0,
                )
            )
        )
        self._metric_values["resolved"].setText(
            str(
                summary.status_counts.get(
                    "Resuelta",
                    0,
                )
            )
        )
        self._metric_values["percentage"].setText(
            f"{summary.resolution_percentage:.0f}%"
        )

        maximum = max(summary.total_requests, 1)

        for priority, progress in self._priority_bars.items():
            count = summary.priority_counts.get(
                priority,
                0,
            )

            percentage = (count / maximum) * 100

            progress.setRange(0, maximum)
            progress.setValue(count)
            progress.setFormat(f"{count} ({percentage:.0f}%)")

    @Slot(str)
    def _on_statistics_failed(
        self,
        message: str,
    ) -> None:
        QMessageBox.warning(
            self,
            "Estadísticas no disponibles",
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
            #panel {
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
                font-size: 28px;
                font-weight: 700;
            }

            #sectionTitle {
                color: #344054;
                font-size: 15px;
                font-weight: 700;
            }

            #priorityLabel {
                color: #344054;
                font-size: 13px;
                font-weight: 600;
            }

            QProgressBar {
                background-color: #eaecf0;
                color: #344054;
                border: none;
                border-radius: 6px;
                min-height: 22px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #526df5;
                border-radius: 6px;
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
        """)
