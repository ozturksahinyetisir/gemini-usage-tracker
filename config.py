import os
import sys
import json
import time

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    # Quota State
    "limit_remaining": 100.0,
    "limit_used": 0.0,
    "reset_time_epoch": 0.0,
    "weekly_remaining": 100.0,
    "weekly_reset_epoch": 0.0,
    "plan_tier": "Google AI Pro",
    "last_sync_time": 0.0,
    "sync_source": "Offline",
    
    # UI Appearance
    "position_mode": "center",  # "center", "left", "right", "custom"
    "custom_x": -1,
    "custom_y": -1,
    "always_on_top": True,
    "opacity": 0.95,
    "compact_mode": False,
    "dark_theme": True,
    "accent_color": "#1A73E8",
    
    # Notification & Audio
    "toast_notifications": True,
    "sound_notifications": True,
    "low_quota_alert": True,
    "low_quota_threshold": 20,
    "reset_alert": True,
    
    # Network & System
    "server_port": 38281,
    "auto_start": False,
}

class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"[Config] Error loading config: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value, auto_save=True):
        self.data[key] = value
        if auto_save:
            self.save()

    def update_quota(self, remaining, used, reset_epoch, weekly_remaining=None, weekly_reset=None, plan=None, source="Live Extension"):
        self.data["limit_remaining"] = float(remaining)
        self.data["limit_used"] = float(used)
        self.data["reset_time_epoch"] = float(reset_epoch)
        if weekly_remaining is not None:
            self.data["weekly_remaining"] = float(weekly_remaining)
        if weekly_reset is not None:
            self.data["weekly_reset_epoch"] = float(weekly_reset)
        if plan:
            self.data["plan_tier"] = str(plan)
        self.data["last_sync_time"] = time.time()
        self.data["sync_source"] = str(source)
        self.save()
        self._append_history(remaining, used, reset_epoch)

    def _append_history(self, remaining, used, reset_epoch):
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append({
            "timestamp": time.time(),
            "remaining": remaining,
            "used": used,
            "reset_epoch": reset_epoch
        })
        # Keep last 200 events
        if len(history) > 200:
            history = history[-200:]
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"[Config] History write error: {e}")

config = AppConfig()
