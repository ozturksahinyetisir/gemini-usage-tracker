"""
Stylesheets and color palettes for Gemini Usage Tracker Top Bar
"""

DARK_THEME_TOP_BAR = """
QWidget#TopBarContainer {
    background-color: rgba(20, 22, 28, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 18px;
}

QWidget#TopBarContainer:hover {
    border: 1px solid rgba(26, 115, 232, 0.5);
    background-color: rgba(22, 25, 32, 0.96);
}

QLabel {
    color: #F1F3F4;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

QLabel#TitleLabel {
    font-size: 12px;
    font-weight: 600;
    color: #8AB4F8;
    letter-spacing: 0.3px;
}

QLabel#PercentLabel {
    font-size: 13px;
    font-weight: 700;
    color: #FFFFFF;
}

QLabel#TimerLabel {
    font-size: 12px;
    font-weight: 600;
    color: #E8EAED;
    padding: 2px 6px;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 10px;
}

QLabel#PlanBadge {
    font-size: 10px;
    font-weight: 600;
    color: #D2E3FC;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A73E8, stop:1 #9334E6);
    border-radius: 8px;
    padding: 2px 7px;
}

QProgressBar#QuotaBar {
    border: none;
    border-radius: 5px;
    background-color: rgba(255, 255, 255, 0.12);
    text-align: center;
    height: 8px;
}

QProgressBar#QuotaBar::chunk {
    border-radius: 5px;
}

/* Push buttons on top bar */
QPushButton.BarBtn {
    background-color: transparent;
    border: none;
    border-radius: 12px;
    color: #9AA0A6;
    font-size: 12px;
    padding: 3px 6px;
}

QPushButton.BarBtn:hover {
    background-color: rgba(255, 255, 255, 0.15);
    color: #FFFFFF;
}

QPushButton.BarBtn:pressed {
    background-color: rgba(255, 255, 255, 0.25);
}

QPushButton.PinActive {
    color: #8AB4F8;
    background-color: rgba(138, 180, 248, 0.18);
}
"""

FLYOUT_PANEL_STYLE = """
QFrame#FlyoutFrame {
    background-color: rgba(20, 22, 30, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
}

QLabel {
    color: #E8EAED;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

QLabel.SectionHeader {
    font-size: 13px;
    font-weight: 700;
    color: #8AB4F8;
    margin-bottom: 4px;
}

QLabel.CardTitle {
    font-size: 11px;
    font-weight: 600;
    color: #9AA0A6;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel.BigNumber {
    font-size: 26px;
    font-weight: 700;
    color: #FFFFFF;
}

QLabel.Subtitle {
    font-size: 11px;
    color: #9AA0A6;
}

QFrame.Card {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 10px;
}

QFrame.Card:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
}

QPushButton.ActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A73E8, stop:1 #4285F4);
    color: #FFFFFF;
    font-weight: 600;
    font-size: 12px;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
}

QPushButton.ActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1b66ca, stop:1 #3367d6);
}

QPushButton.SecondaryBtn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #E8EAED;
    font-weight: 600;
    font-size: 11px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 6px 12px;
}

QPushButton.SecondaryBtn:hover {
    background-color: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.25);
    color: #FFFFFF;
}

QPushButton.LogPromptBtn {
    background-color: rgba(26, 115, 232, 0.12);
    color: #8AB4F8;
    font-weight: 600;
    font-size: 11px;
    border: 1px solid rgba(138, 180, 248, 0.25);
    border-radius: 6px;
    padding: 5px 8px;
}

QPushButton.LogPromptBtn:hover {
    background-color: rgba(26, 115, 232, 0.25);
    color: #FFFFFF;
}

QTabWidget::pane {
    border: none;
    background: transparent;
}

QTabBar::tab {
    background: transparent;
    color: #9AA0A6;
    font-weight: 600;
    font-size: 11px;
    padding: 6px 12px;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    color: #8AB4F8;
    border-bottom: 2px solid #8AB4F8;
}

QTabBar::tab:hover {
    color: #E8EAED;
}
"""

SETTINGS_DIALOG_STYLE = """
QDialog {
    background-color: #1A1C23;
    color: #E8EAED;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

QLabel {
    color: #E8EAED;
    font-size: 12px;
}

QGroupBox {
    color: #8AB4F8;
    font-weight: 600;
    font-size: 12px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}

QCheckBox {
    color: #E8EAED;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #5F6368;
    background-color: #2D3139;
}

QCheckBox::indicator:checked {
    background-color: #1A73E8;
    border-color: #1A73E8;
}

QComboBox, QSpinBox, QSlider {
    background-color: #242731;
    border: 1px solid #3C4043;
    border-radius: 6px;
    color: #FFFFFF;
    padding: 4px 8px;
}

QComboBox::drop-down {
    border: none;
}

QPushButton {
    background-color: #1A73E8;
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
}

QPushButton:hover {
    background-color: #185ABC;
}
"""

def get_progress_chunk_style(remaining_pct):
    if remaining_pct > 50:
        # Green / Cyan gradient
        return "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00E676, stop:1 #00B0FF);"
    elif remaining_pct > 20:
        # Amber / Orange gradient
        return "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD600, stop:1 #FF9100);"
    else:
        # Crimson / Coral alert gradient
        return "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5252, stop:1 #FF1744);"
