import os
import sys
import ctypes
import winsound
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer
from config import config, BASE_DIR
from tracker_engine import tracker_engine
from local_server import local_bridge_server
from ui.top_bar import TopMenuBar

# Windows AppID for notification grouping
try:
    myappid = "Google.Gemini.UsageTracker.v1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

class GeminiUsageApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Icon
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, "assets", "icon.ico")
        else:
            icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
            
        self.app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self.app.setWindowIcon(self.app_icon)

        # Start background HTTP bridge server
        local_bridge_server.start()

        # Create Top Menu Bar
        self.top_bar = TopMenuBar()

        # Create System Tray Icon
        self.setup_tray()

        # Connect alerts
        tracker_engine.low_quota_alert_signal.connect(self.on_low_quota_alert)
        tracker_engine.reset_replenished_signal.connect(self.on_reset_replenished)

        # Show top bar
        self.top_bar.show()

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self.app_icon, self.app)
        self.tray.setToolTip("Gemini Usage Tracker")

        # Tray Context Menu
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #20232B; color: #E8EAED; border: 1px solid #3C4043; border-radius: 8px; padding: 4px; }
            QMenu::item { padding: 6px 18px; border-radius: 4px; }
            QMenu::item:selected { background-color: #1A73E8; color: white; }
        """)

        act_toggle = menu.addAction("👁️ Üst Menü Çubuğunu Göster / Gizle")
        act_toggle.triggered.connect(self.toggle_top_bar)

        act_flyout = menu.addAction("📊 Detaylı Limit Panelini Aç")
        act_flyout.triggered.connect(self.top_bar.toggle_flyout)

        act_center = menu.addAction("🎯 Ekranın Üst Ortasına Hizala")
        act_center.triggered.connect(self.top_bar.center_window)

        menu.addSeparator()

        act_open_gemini = menu.addAction("🌐 Gemini'yi Aç (gemini.google.com)")
        import webbrowser
        act_open_gemini.triggered.connect(lambda: webbrowser.open("https://gemini.google.com"))

        menu.addSeparator()

        act_exit = menu.addAction("✕ Çıkış")
        act_exit.triggered.connect(self.quit_app)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

        # Update tray tooltip with current status
        self.tray_timer = QTimer()
        self.tray_timer.timeout.connect(self.update_tray_tooltip)
        self.tray_timer.start(2000)

    def update_tray_tooltip(self):
        state = tracker_engine.get_state()
        rem = state.get("remaining", 100.0)
        c_str = state.get("countdown_str", "00:00:00")
        plan = state.get("plan", "Google AI Pro")
        self.tray.setToolTip(f"Gemini {plan}\n5 Saatlik Limit: %{rem:.0f}\nSıfırlanma: {c_str}")

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_top_bar()

    def toggle_top_bar(self):
        if self.top_bar.isVisible():
            self.top_bar.hide()
            if self.top_bar.flyout.isVisible():
                self.top_bar.flyout.hide()
        else:
            self.top_bar.show()
            self.top_bar.raise_()

    def on_low_quota_alert(self, remaining):
        if config.get("sound_notifications", True):
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass

        if config.get("toast_notifications", True):
            self.tray.showMessage(
                "⚠️ Gemini Limit Uyarısı",
                f"5 saatlik kalan kullanım limitiniz %{remaining:.0f} seviyesine indi! Yoğun görevlerde limit dolabilir.",
                QSystemTrayIcon.MessageIcon.Warning,
                5000
            )

    def on_reset_replenished(self):
        if config.get("sound_notifications", True):
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

        if config.get("toast_notifications", True):
            self.tray.showMessage(
                "⚡ Gemini Limiti Yenilendi",
                "5 saatlik kullanım süreniz doldu ve kotanız %100 seviyesine sıfırlandı!",
                QSystemTrayIcon.MessageIcon.Information,
                5000
            )

    def quit_app(self):
        local_bridge_server.stop()
        self.app.quit()

    def run(self):
        return self.app.exec()

if __name__ == "__main__":
    app_instance = GeminiUsageApp()
    sys.exit(app_instance.run())
