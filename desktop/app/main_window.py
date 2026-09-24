from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.views.requests_page import RequestsPage
from app.views.statistics_page import StatisticsPage
from app.views.dashboard_page import DashboardPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("SupportFlow AI")
        self.resize(1100, 700)
        self.setMinimumSize(850, 550)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._create_sidebar()
        self.pages = self._create_pages()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages, 1)

        self.setCentralWidget(central_widget)
        self._apply_styles()

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 28, 20, 28)
        layout.setSpacing(12)

        brand = QLabel("SupportFlow AI")
        brand.setObjectName("brand")

        subtitle = QLabel("Centro de solicitudes")
        subtitle.setObjectName("sidebarSubtitle")

        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addSpacing(25)

        options = [
            ("Panel principal", 0),
            ("Solicitudes", 1),
            ("Estadísticas", 2),
        ]

        for text, page_index in options:
            button = QPushButton(text)
            button.setCursor(Qt.CursorShape.PointingHandCursor)

            button.clicked.connect(
                lambda checked=False, index=page_index: self.pages.setCurrentIndex(
                    index
                )
            )

            layout.addWidget(button)

        layout.addStretch()

        user_label = QLabel("Empleado conectado")
        user_label.setObjectName("userLabel")
        layout.addWidget(user_label)

        return sidebar

    def _create_pages(self) -> QStackedWidget:
        pages = QStackedWidget()

        dashboard_page = DashboardPage()
        dashboard_page.open_requests_requested.connect(
            lambda: pages.setCurrentIndex(1)
        )
        dashboard_page.open_statistics_requested.connect(
            lambda: pages.setCurrentIndex(2)
        )

        pages.addWidget(dashboard_page)

        pages.addWidget(RequestsPage())

        pages.addWidget(StatisticsPage())

        return pages

    def _create_placeholder_page(
        self,
        title: str,
        description: str,
    ) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 45, 50, 45)

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")

        description_label = QLabel(description)
        description_label.setObjectName("pageDescription")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()

        return page

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f6fa;
            }

            #sidebar {
                background-color: #172033;
            }

            #brand {
                color: #ffffff;
                font-size: 21px;
                font-weight: 700;
            }

            #sidebarSubtitle {
                color: #8f9bb3;
                font-size: 12px;
            }

            #sidebar QPushButton {
                background-color: transparent;
                color: #d8deea;
                border: none;
                border-radius: 7px;
                padding: 11px 13px;
                text-align: left;
                font-size: 14px;
            }

            #sidebar QPushButton:hover {
                background-color: #27344d;
                color: #ffffff;
            }

            #userLabel {
                color: #8f9bb3;
                font-size: 12px;
            }

            #pageTitle {
                color: #172033;
                font-size: 28px;
                font-weight: 700;
            }

            #pageDescription {
                color: #667085;
                font-size: 15px;
            }
            """)
