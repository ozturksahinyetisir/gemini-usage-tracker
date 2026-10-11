import os
import sys
import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QSlider, QSpinBox, QTabWidget,
    QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QUrl
from PyQt6.QtGui import QColor, QDesktopServices
from tracker_engine import tracker_engine
from config import config, BASE_DIR
from ui.styles import FLYOUT_PANEL_STYLE, get_progress_chunk_style

class FlyoutPanel(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(460)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Outer background frame
        self.frame = QFrame()
        self.frame.setObjectName("FlyoutFrame")
        self.frame.setStyleSheet(FLYOUT_PANEL_STYLE)

        # Soft drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.frame.setGraphicsEffect(shadow)

        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(18, 16, 18, 18)
        frame_layout.setSpacing(12)

        # --- Top Header ---
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title_label = QLabel("✨ Gemini Usage & Quota Tracker")
        title_label.setObjectName("SectionHeader")
        title_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #8AB4F8;")

        self.sync_source_label = QLabel("🟢 Canlı Senkronizasyon: Hazır")
        self.sync_source_label.setStyleSheet("font-size: 11px; color: #81C995;")
        title_box.addWidget(title_label)
        title_box.addWidget(self.sync_source_label)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.plan_badge = QLabel("AI Pro")
        self.plan_badge.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A73E8, stop:1 #9334E6);
            color: white; font-weight: 700; font-size: 11px; padding: 3px 8px; border-radius: 8px;
        """)
        header_layout.addWidget(self.plan_badge)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 26)
        close_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.08); border: none; border-radius: 13px; color: #9AA0A6; font-weight: bold; }
            QPushButton:hover { background: rgba(255,255,255,0.2); color: white; }
        """)
        close_btn.clicked.connect(self.hide)
        header_layout.addWidget(close_btn)

        frame_layout.addLayout(header_layout)

        # --- Tab Widget ---
        self.tabs = QTabWidget()
        
        # Tab 1: Quota Status
        tab_status = QWidget()
        self.setup_status_tab(tab_status)
        self.tabs.addTab(tab_status, "Limit Durumu")

        # Tab 2: Browser Sync / Extension
        tab_sync = QWidget()
        self.setup_sync_tab(tab_sync)
        self.tabs.addTab(tab_sync, "Otomatik Senkron")

        # Tab 3: Settings
        tab_settings = QWidget()
        self.setup_settings_tab(tab_settings)
        self.tabs.addTab(tab_settings, "Ayarlar")

        frame_layout.addWidget(self.tabs)
        main_layout.addWidget(self.frame)

    def setup_status_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(4, 10, 4, 4)
        layout.setSpacing(10)

        # 5-Hour Limit Card
        card_5h = QFrame()
        card_5h.setProperty("class", "Card")
        card_5h_layout = QVBoxLayout(card_5h)
        card_5h_layout.setSpacing(6)

        c5h_top = QHBoxLayout()
        lbl_5h_title = QLabel("⏳ 5 SAATLİK YUVARLANAN LİMİT")
        lbl_5h_title.setProperty("class", "CardTitle")
        self.lbl_5h_remaining = QLabel("100% Kalan")
        self.lbl_5h_remaining.setStyleSheet("font-size: 13px; font-weight: 700; color: #00E676;")
        c5h_top.addWidget(lbl_5h_title)
        c5h_top.addStretch()
        c5h_top.addWidget(self.lbl_5h_remaining)
        card_5h_layout.addLayout(c5h_top)

        # Progress bar
        self.pb_5h = QProgressBar()
        self.pb_5h.setFixedHeight(10)
        self.pb_5h.setValue(100)
        self.pb_5h.setTextVisible(False)
        self.pb_5h.setStyleSheet("QProgressBar { background: rgba(255,255,255,0.1); border-radius: 5px; } QProgressBar::chunk { background: #00E676; border-radius: 5px; }")
        card_5h_layout.addWidget(self.pb_5h)

        # Countdown & reset target
        c5h_bottom = QHBoxLayout()
        self.lbl_countdown = QLabel("Kalan Süre: 00:00:00")
        self.lbl_countdown.setStyleSheet("font-size: 12px; font-weight: 600; color: #E8EAED;")
        self.lbl_reset_at = QLabel("Tam Dolum: --:--:--")
        self.lbl_reset_at.setStyleSheet("font-size: 11px; color: #9AA0A6;")
        c5h_bottom.addWidget(self.lbl_countdown)
        c5h_bottom.addStretch()
        c5h_bottom.addWidget(self.lbl_reset_at)
        card_5h_layout.addLayout(c5h_bottom)

        layout.addWidget(card_5h)

        # Weekly Limit Card
        card_week = QFrame()
        card_week.setProperty("class", "Card")
        card_week_layout = QVBoxLayout(card_week)
        card_week_layout.setSpacing(6)

        cw_top = QHBoxLayout()
        lbl_w_title = QLabel("📅 HAFTALIK TOPLAM KOTA")
        lbl_w_title.setProperty("class", "CardTitle")
        self.lbl_week_pct = QLabel("100% Kalan")
        self.lbl_week_pct.setStyleSheet("font-size: 12px; font-weight: 600; color: #8AB4F8;")
        cw_top.addWidget(lbl_w_title)
        cw_top.addStretch()
        cw_top.addWidget(self.lbl_week_pct)
        card_week_layout.addLayout(cw_top)

        self.pb_week = QProgressBar()
        self.pb_week.setFixedHeight(6)
        self.pb_week.setValue(100)
        self.pb_week.setTextVisible(False)
        self.pb_week.setStyleSheet("QProgressBar { background: rgba(255,255,255,0.1); border-radius: 3px; } QProgressBar::chunk { background: #1A73E8; border-radius: 3px; }")
        card_week_layout.addWidget(self.pb_week)

        layout.addWidget(card_week)

        # Quick Actions & Manual Prompt Logging
        quick_box = QVBoxLayout()
        quick_box.setSpacing(6)
        lbl_sim = QLabel("Hızlı İstek Simülasyonu / Manuel Kayıt:")
        lbl_sim.setStyleSheet("font-size: 11px; color: #9AA0A6; font-weight: 600;")
        quick_box.addWidget(lbl_sim)

        btn_row = QHBoxLayout()
        btn_prompt_std = QPushButton("+1 Normal Soru (~2%)")
        btn_prompt_std.setProperty("class", "LogPromptBtn")
        btn_prompt_std.clicked.connect(lambda: tracker_engine.log_prompt("standard"))

        btn_prompt_code = QPushButton("+1 Kod / Pro (~6%)")
        btn_prompt_code.setProperty("class", "LogPromptBtn")
        btn_prompt_code.clicked.connect(lambda: tracker_engine.log_prompt("heavy"))

        btn_prompt_think = QPushButton("+1 Thinking (~12%)")
        btn_prompt_think.setProperty("class", "LogPromptBtn")
        btn_prompt_think.clicked.connect(lambda: tracker_engine.log_prompt("thinking"))

        btn_row.addWidget(btn_prompt_std)
        btn_row.addWidget(btn_prompt_code)
        btn_row.addWidget(btn_prompt_think)
        quick_box.addLayout(btn_row)
        layout.addLayout(quick_box)

        # Links
        links_row = QHBoxLayout()
        btn_open_gemini = QPushButton("🌐 Gemini'yi Aç")
        btn_open_gemini.setProperty("class", "ActionBtn")
        btn_open_gemini.clicked.connect(lambda: webbrowser.open("https://gemini.google.com"))

        btn_open_usage = QPushButton("📊 Kullanım Limitleri")
        btn_open_usage.setProperty("class", "SecondaryBtn")
        btn_open_usage.clicked.connect(lambda: webbrowser.open("https://gemini.google.com/usage"))

        links_row.addWidget(btn_open_gemini)
        links_row.addWidget(btn_open_usage)
        layout.addLayout(links_row)

    def setup_sync_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(6, 12, 6, 6)
        layout.setSpacing(12)

        info_box = QLabel(
            "Gemini kullanım verilerinizi <b>gemini.google.com</b> üzerinden otomatik olarak "
            "bu üst menü çubuğuna aktarabilirsiniz. İki kolay yöntem bulunmaktadır:"
        )
        info_box.setWordWrap(True)
        info_box.setStyleSheet("font-size: 11px; color: #BDC1C6; line-height: 1.4;")
        layout.addWidget(info_box)

        # Option 1: Chrome/Edge Unpacked Extension
        opt1_frame = QFrame()
        opt1_frame.setProperty("class", "Card")
        opt1_layout = QVBoxLayout(opt1_frame)
        
        lbl_opt1_title = QLabel("Yöntem 1: Chrome / Edge Eklentisi (Önerilen)")
        lbl_opt1_title.setStyleSheet("font-weight: 700; color: #8AB4F8; font-size: 12px;")
        opt1_desc = QLabel("1. Aşağıdaki butona basarak eklenti klasörünü açın.\n2. Tarayıcınızda 'chrome://extensions' açın ve 'Geliştirici Modu'nu aktif edin.\n3. 'Paketlenmemiş öge yükle' diyerek açılan klasörü seçin.")
        opt1_desc.setStyleSheet("font-size: 11px; color: #9AA0A6;")
        
        btn_open_ext_dir = QPushButton("📂 Eklenti Klasörünü Aç")
        btn_open_ext_dir.setProperty("class", "SecondaryBtn")
        btn_open_ext_dir.clicked.connect(self.open_extension_directory)

        opt1_layout.addWidget(lbl_opt1_title)
        opt1_layout.addWidget(opt1_desc)
        opt1_layout.addWidget(btn_open_ext_dir)
        layout.addWidget(opt1_frame)

        # Option 2: Tampermonkey Userscript
        opt2_frame = QFrame()
        opt2_frame.setProperty("class", "Card")
        opt2_layout = QVBoxLayout(opt2_frame)
        
        lbl_opt2_title = QLabel("Yöntem 2: Tampermonkey / Violentmonkey Userscript")
        lbl_opt2_title.setStyleSheet("font-weight: 700; color: #8AB4F8; font-size: 12px;")
        opt2_desc = QLabel("Eğer Tampermonkey eklentisi kullanıyorsanız, tek tıkla userscript kodunu kopyalayabilir veya script dosyasını açabilirsiniz.")
        opt2_desc.setStyleSheet("font-size: 11px; color: #9AA0A6;")
        
        btn_open_script = QPushButton("📄 Userscript Dosyasını Aç")
        btn_open_script.setProperty("class", "SecondaryBtn")
        btn_open_script.clicked.connect(self.open_userscript_file)

        opt2_layout.addWidget(lbl_opt2_title)
        opt2_layout.addWidget(opt2_desc)
        opt2_layout.addWidget(btn_open_script)
        layout.addWidget(opt2_frame)

        # Manual Calibration Box
        calib_frame = QFrame()
        calib_frame.setProperty("class", "Card")
        calib_layout = QVBoxLayout(calib_frame)
        
        lbl_calib = QLabel("Hızlı Manuel Ayar (Eklentisiz Kullanım):")
        lbl_calib.setStyleSheet("font-weight: 600; color: #E8EAED; font-size: 11px;")
        
        calib_inputs = QHBoxLayout()
        calib_inputs.addWidget(QLabel("Kalan %:"))
        self.spin_pct = QSpinBox()
        self.spin_pct.setRange(0, 100)
        self.spin_pct.setValue(int(config.get("limit_remaining", 100)))
        calib_inputs.addWidget(self.spin_pct)

        calib_inputs.addWidget(QLabel("Saat:"))
        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(0, 5)
        self.spin_hours.setValue(4)
        calib_inputs.addWidget(self.spin_hours)

        calib_inputs.addWidget(QLabel("Dk:"))
        self.spin_mins = QSpinBox()
        self.spin_mins.setRange(0, 59)
        self.spin_mins.setValue(30)
        calib_inputs.addWidget(self.spin_mins)

        btn_apply_manual = QPushButton("Uygula")
        btn_apply_manual.setProperty("class", "ActionBtn")
        btn_apply_manual.clicked.connect(self.apply_manual_settings)
        calib_inputs.addWidget(btn_apply_manual)

        calib_layout.addWidget(lbl_calib)
        calib_layout.addLayout(calib_inputs)
        layout.addWidget(calib_frame)

    def setup_settings_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(6, 12, 6, 6)
        layout.setSpacing(12)

        # Opacity Slider
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Pencere Saydamlığı:"))
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(50, 100)
        self.slider_opacity.setValue(int(config.get("opacity", 0.95) * 100))
        self.slider_opacity.valueChanged.connect(self.on_opacity_slider_changed)
        self.lbl_opacity_val = QLabel(f"%{self.slider_opacity.value()}")
        op_layout.addWidget(self.slider_opacity)
        op_layout.addWidget(self.lbl_opacity_val)
        layout.addLayout(op_layout)

        # Low Quota Threshold
        th_layout = QHBoxLayout()
        th_layout.addWidget(QLabel("Düşük Limit Uyarı Eşiği (%):"))
        self.spin_threshold = QSpinBox()
        self.spin_threshold.setRange(5, 50)
        self.spin_threshold.setValue(config.get("low_quota_threshold", 20))
        self.spin_threshold.valueChanged.connect(lambda v: config.set("low_quota_threshold", v))
        th_layout.addWidget(self.spin_threshold)
        layout.addLayout(th_layout)

        # Plan Selection
        plan_layout = QHBoxLayout()
        plan_layout.addWidget(QLabel("Gemini Planı:"))
        from PyQt6.QtWidgets import QComboBox
        self.combo_plan = QComboBox()
        self.combo_plan.addItems(["Google AI Pro", "Google AI Ultra", "Google AI Plus", "Gemini Free"])
        current_plan = config.get("plan_tier", "Google AI Pro")
        idx = self.combo_plan.findText(current_plan)
        if idx >= 0:
            self.combo_plan.setCurrentIndex(idx)
        self.combo_plan.currentTextChanged.connect(self.on_plan_changed)
        plan_layout.addWidget(self.combo_plan)
        layout.addLayout(plan_layout)

        # Checkboxes
        from PyQt6.QtWidgets import QCheckBox
        self.cb_sound = QCheckBox("Sesli Uyarıları Çal")
        self.cb_sound.setChecked(config.get("sound_notifications", True))
        self.cb_sound.stateChanged.connect(lambda s: config.set("sound_notifications", s == 2))
        layout.addWidget(self.cb_sound)

        self.cb_toast = QCheckBox("Windows Bildirimleri Göster")
        self.cb_toast.setChecked(config.get("toast_notifications", True))
        self.cb_toast.stateChanged.connect(lambda s: config.set("toast_notifications", s == 2))
        layout.addWidget(self.cb_toast)

        self.cb_autostart = QCheckBox("Windows Başlangıcında Çalıştır")
        self.cb_autostart.setChecked(config.get("auto_start", False))
        self.cb_autostart.stateChanged.connect(self.on_autostart_toggle)
        layout.addWidget(self.cb_autostart)

        layout.addStretch()

    def update_data(self, state):
        remaining = state.get("remaining", 100.0)
        seconds_left = state.get("seconds_left", 0)
        countdown_str = state.get("countdown_str", "00:00:00")
        reset_target_str = state.get("reset_target_str", "")
        plan = state.get("plan", "Google AI Pro")
        source = state.get("source", "Offline")
        weekly_remaining = state.get("weekly_remaining", 100.0)

        # Update 5h limit labels
        self.lbl_5h_remaining.setText(f"%{remaining:.1f} Kalan")
        self.pb_5h.setValue(int(remaining))
        
        # Color coding progress chunk
        color_chunk = get_progress_chunk_style(remaining)
        self.pb_5h.setStyleSheet(f"QProgressBar {{ background: rgba(255,255,255,0.1); border-radius: 5px; }} QProgressBar::chunk {{ background: {color_chunk} border-radius: 5px; }}")

        if remaining > 50:
            self.lbl_5h_remaining.setStyleSheet("font-size: 13px; font-weight: 700; color: #00E676;")
        elif remaining > 20:
            self.lbl_5h_remaining.setStyleSheet("font-size: 13px; font-weight: 700; color: #FFB300;")
        else:
            self.lbl_5h_remaining.setStyleSheet("font-size: 13px; font-weight: 700; color: #FF5252;")

        self.lbl_countdown.setText(f"Kalan Süre: {countdown_str}")
        if reset_target_str:
            self.lbl_reset_at.setText(f"Sıfırlanma: {reset_target_str}")
        else:
            self.lbl_reset_at.setText("Sıfırlanma: Tam Hazır")

        # Update Weekly
        self.lbl_week_pct.setText(f"%{weekly_remaining:.1f} Kalan")
        self.pb_week.setValue(int(weekly_remaining))

        # Update plan & source
        self.plan_badge.setText(plan.replace("Google ", ""))
        self.sync_source_label.setText(f"🟢 Kaynak: {source}")

    def on_opacity_slider_changed(self, val):
        self.lbl_opacity_val.setText(f"%{val}")
        config.set("opacity", val / 100.0)
        self.settings_changed.emit()

    def on_plan_changed(self, text):
        config.set("plan_tier", text)
        self.plan_badge.setText(text.replace("Google ", ""))
        self.settings_changed.emit()

    def on_autostart_toggle(self, state):
        is_checked = (state == 2)
        config.set("auto_start", is_checked)
        self._set_windows_autostart(is_checked)

    def _set_windows_autostart(self, enable):
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "GeminiUsageTracker"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enable:
                script_path = os.path.join(BASE_DIR, "run.bat")
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{script_path}"')
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"[Autostart] Registry error: {e}")

    def apply_manual_settings(self):
        pct = self.spin_pct.value()
        hrs = self.spin_hours.value()
        mins = self.spin_mins.value()
        tracker_engine.set_manual(pct, hrs, mins)

    def open_extension_directory(self):
        ext_dir = os.path.join(BASE_DIR, "extension")
        os.startfile(ext_dir)

    def open_userscript_file(self):
        script_path = os.path.join(BASE_DIR, "userscript", "gemini_usage_sync.user.js")
        if os.path.exists(script_path):
            os.startfile(os.path.dirname(script_path))
