import sys
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QApplication, QMenu, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QAction, QFont
from config import config
from tracker_engine import tracker_engine
from ui.styles import DARK_THEME_TOP_BAR, get_progress_chunk_style
from ui.flyout_panel import FlyoutPanel

class TopMenuBar(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # State
        self.drag_position = QPoint()
        self.is_dragging = False
        self.flyout = FlyoutPanel()
        self.flyout.settings_changed.connect(self.apply_settings)

        self.init_ui()
        self.apply_settings()
        self.position_window()

        # Connect engine signals
        tracker_engine.quota_updated.connect(self.on_quota_updated)

        # 1-second timer to update countdown smoothly
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.on_second_tick)
        self.tick_timer.start(1000)

        # Initial data update
        self.on_second_tick()

    def init_ui(self):
        self.setFixedHeight(46)
        self.setFixedWidth(560)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 4, 6, 6)

        # Container Widget
        self.container = QWidget()
        self.container.setObjectName("TopBarContainer")
        self.container.setStyleSheet(DARK_THEME_TOP_BAR)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.setSpacing(8)

        # 1. Gemini Icon / Brand
        self.icon_label = QLabel("✦")
        self.icon_label.setStyleSheet("color: #8AB4F8; font-size: 16px; font-weight: bold;")
        self.title_label = QLabel("Gemini")
        self.title_label.setObjectName("TitleLabel")

        brand_box = QHBoxLayout()
        brand_box.setSpacing(4)
        brand_box.addWidget(self.icon_label)
        brand_box.addWidget(self.title_label)
        layout.addLayout(brand_box)

        # 2. Progress Bar & Percent
        quota_box = QHBoxLayout()
        quota_box.setSpacing(6)

        self.quota_bar = QProgressBar()
        self.quota_bar.setObjectName("QuotaBar")
        self.quota_bar.setFixedWidth(130)
        self.quota_bar.setFixedHeight(8)
        self.quota_bar.setValue(100)
        self.quota_bar.setTextVisible(False)
        quota_box.addWidget(self.quota_bar)

        self.percent_label = QLabel("100%")
        self.percent_label.setObjectName("PercentLabel")
        quota_box.addWidget(self.percent_label)
        layout.addLayout(quota_box)

        # 3. Countdown Timer Label
        self.timer_label = QLabel("⏳ 00:00:00")
        self.timer_label.setObjectName("TimerLabel")
        layout.addWidget(self.timer_label)

        # 4. Plan Badge
        self.plan_badge = QLabel("Pro")
        self.plan_badge.setObjectName("PlanBadge")
        layout.addWidget(self.plan_badge)

        layout.addStretch()

        # 5. Buttons
        # Expand/Flyout Toggle Button
        self.btn_expand = QPushButton("▾")
        self.btn_expand.setProperty("class", "BarBtn")
        self.btn_expand.setToolTip("Detayları Göster / Gizle")
        self.btn_expand.setFixedSize(24, 24)
        self.btn_expand.clicked.connect(self.toggle_flyout)
        layout.addWidget(self.btn_expand)

        # Pin / Always on top button
        self.btn_pin = QPushButton("📌")
        self.btn_pin.setProperty("class", "BarBtn")
        self.btn_pin.setToolTip("Her Zaman Üstte")
        self.btn_pin.setFixedSize(24, 24)
        self.btn_pin.clicked.connect(self.toggle_pin)
        layout.addWidget(self.btn_pin)

        # Minimize / Hide button
        self.btn_min = QPushButton("✕")
        self.btn_min.setProperty("class", "BarBtn")
        self.btn_min.setToolTip("Gizle (Sistem Tepsisine Küçült)")
        self.btn_min.setFixedSize(24, 24)
        self.btn_min.clicked.connect(self.hide)
        layout.addWidget(self.btn_min)

        main_layout.addWidget(self.container)

    def apply_settings(self):
        # Always on top
        is_on_top = config.get("always_on_top", True)
        if is_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.btn_pin.setStyleSheet("color: #8AB4F8; background: rgba(138, 180, 248, 0.2);")
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self.btn_pin.setStyleSheet("")
        
        # Opacity
        opacity = config.get("opacity", 0.95)
        self.setWindowOpacity(opacity)
        self.flyout.setWindowOpacity(opacity)

        # Plan badge
        plan = config.get("plan_tier", "Google AI Pro")
        self.plan_badge.setText(plan.replace("Google AI ", "").replace("Gemini ", ""))

        self.show()

    def position_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        pos_mode = config.get("position_mode", "center")
        custom_x = config.get("custom_x", -1)
        custom_y = config.get("custom_y", -1)

        if pos_mode == "custom" and custom_x >= 0 and custom_y >= 0:
            self.move(custom_x, custom_y)
        elif pos_mode == "left":
            self.move(screen.x() + 20, screen.y() + 6)
        elif pos_mode == "right":
            self.move(screen.x() + screen.width() - self.width() - 20, screen.y() + 6)
        else:
            # Centered at top (Dynamic Island style)
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + 6
            self.move(x, y)

    def toggle_flyout(self):
        if self.flyout.isVisible():
            self.flyout.hide()
            self.btn_expand.setText("▾")
        else:
            # Position flyout centered right below top bar
            bar_geo = self.geometry()
            fx = bar_geo.x() + (bar_geo.width() - self.flyout.width()) // 2
            fy = bar_geo.y() + bar_geo.height() + 4
            self.flyout.move(fx, fy)
            self.flyout.show()
            self.flyout.raise_()
            self.btn_expand.setText("▴")

    def toggle_pin(self):
        curr = config.get("always_on_top", True)
        config.set("always_on_top", not curr)
        self.apply_settings()

    def on_second_tick(self):
        state = tracker_engine.get_state()
        self.update_ui_state(state)

    def on_quota_updated(self, state):
        self.update_ui_state(state)

    def update_ui_state(self, state):
        remaining = state.get("remaining", 100.0)
        seconds_left = state.get("seconds_left", 0)
        countdown_str = state.get("countdown_str", "00:00:00")
        countdown_short = state.get("countdown_short", "")
        plan = state.get("plan", "Google AI Pro")

        # Update percentage text
        self.percent_label.setText(f"%{remaining:.0f}")

        # Update progress bar value
        self.quota_bar.setValue(int(remaining))

        # Dynamic color gradient chunk
        color_chunk = get_progress_chunk_style(remaining)
        self.quota_bar.setStyleSheet(
            f"QProgressBar#QuotaBar {{ border: none; border-radius: 4px; background-color: rgba(255, 255, 255, 0.12); }}"
            f"QProgressBar#QuotaBar::chunk {{ border-radius: 4px; background: {color_chunk} }}"
        )

        # Update timer label
        if seconds_left > 0:
            self.timer_label.setText(f"⏳ {countdown_str}")
            self.timer_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #E8EAED; padding: 2px 6px; background-color: rgba(255, 255, 255, 0.08); border-radius: 8px;")
        else:
            self.timer_label.setText("⚡ 100% Dolu")
            self.timer_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #81C995; padding: 2px 6px; background-color: rgba(129, 201, 149, 0.12); border-radius: 8px;")

        # Update plan
        self.plan_badge.setText(plan.replace("Google AI ", "").replace("Gemini ", ""))

        # Update flyout if open
        if self.flyout.isVisible():
            self.flyout.update_data(state)

    # --- Mouse Drag Support ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            # Prevent dragging off screen
            new_pos.setY(max(0, new_pos.y()))
            self.move(new_pos)
            if self.flyout.isVisible():
                self.flyout.move(new_pos.x() + (self.width() - self.flyout.width()) // 2, new_pos.y() + self.height() + 4)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.is_dragging:
            self.is_dragging = False
            config.set("position_mode", "custom", auto_save=False)
            config.set("custom_x", self.x(), auto_save=False)
            config.set("custom_y", self.y(), auto_save=True)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        self.toggle_flyout()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #20232B; color: #E8EAED; border: 1px solid #3C4043; border-radius: 8px; padding: 4px; }
            QMenu::item { padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background-color: #1A73E8; color: white; }
        """)

        act_details = menu.addAction("📊 Detaylı Paneli Aç / Kapat")
        act_details.triggered.connect(self.toggle_flyout)

        menu.addSeparator()

        act_center = menu.addAction("🎯 Ekranın Üst Ortasına Hizala")
        act_center.triggered.connect(self.center_window)

        act_pin = menu.addAction("📌 Her Zaman Üstte Tut")
        act_pin.setCheckable(True)
        act_pin.setChecked(config.get("always_on_top", True))
        act_pin.triggered.connect(self.toggle_pin)

        menu.addSeparator()

        act_open_gemini = menu.addAction("🌐 Gemini Web Sayfasını Aç")
        import webbrowser
        act_open_gemini.triggered.connect(lambda: webbrowser.open("https://gemini.google.com"))

        act_hide = menu.addAction("➖ Simge Durumuna Küçült")
        act_hide.triggered.connect(self.hide)

        act_exit = menu.addAction("✕ Çıkış")
        act_exit.triggered.connect(QApplication.instance().quit)

        menu.exec(event.globalPos())

    def center_window(self):
        config.set("position_mode", "center")
        self.position_window()
        if self.flyout.isVisible():
            self.toggle_flyout()
