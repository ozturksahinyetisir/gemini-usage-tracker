import time
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal
from config import config

class QuotaTrackerEngine(QObject):
    # Signals for UI and notification updates
    quota_updated = pyqtSignal(dict)
    low_quota_alert_signal = pyqtSignal(float)
    reset_replenished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._alerted_low = False
        self._last_notified_reset_epoch = 0.0

    def get_state(self):
        now = time.time()
        reset_epoch = config.get("reset_time_epoch", 0.0)
        remaining = config.get("limit_remaining", 100.0)
        used = config.get("limit_used", 0.0)
        weekly_remaining = config.get("weekly_remaining", 100.0)
        weekly_reset = config.get("weekly_reset_epoch", 0.0)
        plan = config.get("plan_tier", "Google AI Pro")
        source = config.get("sync_source", "Offline")
        last_sync = config.get("last_sync_time", 0.0)

        # Check if reset epoch was reached
        seconds_left = max(0, int(reset_epoch - now)) if reset_epoch > 0 else 0

        # Auto-replenish if reset timer expired and we were not at 100%
        if reset_epoch > 0 and now >= reset_epoch and remaining < 100.0:
            remaining = 100.0
            used = 0.0
            reset_epoch = 0.0
            seconds_left = 0
            config.set("limit_remaining", 100.0, auto_save=False)
            config.set("limit_used", 0.0, auto_save=False)
            config.set("reset_time_epoch", 0.0, auto_save=True)
            self._alerted_low = False
            self.reset_replenished_signal.emit()

        # Format countdown
        if seconds_left > 0:
            hours = seconds_left // 3600
            mins = (seconds_left % 3600) // 60
            secs = seconds_left % 60
            countdown_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            countdown_short = f"{hours}s {mins}d" if hours > 0 else f"{mins}d {secs}s"
        else:
            countdown_str = "00:00:00"
            countdown_short = "Hazır (100%)"

        # Check low quota threshold
        threshold = config.get("low_quota_threshold", 20)
        if remaining <= threshold and not self._alerted_low and remaining > 0:
            self._alerted_low = True
            self.low_quota_alert_signal.emit(remaining)
        elif remaining > threshold:
            self._alerted_low = False

        # Format reset target time
        reset_target_str = ""
        if reset_epoch > 0 and seconds_left > 0:
            reset_dt = datetime.fromtimestamp(reset_epoch)
            reset_target_str = reset_dt.strftime("%H:%M:%S")

        return {
            "remaining": remaining,
            "used": used,
            "seconds_left": seconds_left,
            "countdown_str": countdown_str,
            "countdown_short": countdown_short,
            "reset_target_str": reset_target_str,
            "reset_epoch": reset_epoch,
            "weekly_remaining": weekly_remaining,
            "weekly_reset": weekly_reset,
            "plan": plan,
            "source": source,
            "last_sync": last_sync,
            "is_active_countdown": seconds_left > 0
        }

    def process_live_sync(self, payload):
        """Called when Chrome/Edge extension or userscript posts new usage data."""
        now = time.time()
        
        # Payload may contain:
        # remaining: float (e.g. 75.0) or used: float
        # reset_seconds: int or reset_time_str: str (e.g. "3h 20m")
        # weekly_remaining: float
        # plan: str
        
        remaining = payload.get("remaining")
        used = payload.get("used")
        
        if remaining is None and used is not None:
            remaining = max(0.0, min(100.0, 100.0 - float(used)))
        elif remaining is not None:
            remaining = max(0.0, min(100.0, float(remaining)))
            used = 100.0 - remaining
        else:
            remaining = config.get("limit_remaining", 100.0)
            used = 100.0 - remaining

        reset_seconds = payload.get("reset_seconds")
        if reset_seconds is not None:
            reset_seconds = int(reset_seconds)
            reset_epoch = now + reset_seconds if reset_seconds > 0 else 0.0
        else:
            # Maybe a string like "2h 45m" or "165 mins"
            time_str = str(payload.get("reset_time_str", ""))
            parsed_secs = self._parse_time_str(time_str)
            if parsed_secs > 0:
                reset_epoch = now + parsed_secs
            else:
                reset_epoch = config.get("reset_time_epoch", 0.0)

        weekly_remaining = payload.get("weekly_remaining")
        weekly_reset = payload.get("weekly_reset_epoch")
        plan = payload.get("plan")
        source = payload.get("source", "Chrome Extension")

        config.update_quota(
            remaining=remaining,
            used=used,
            reset_epoch=reset_epoch,
            weekly_remaining=weekly_remaining,
            weekly_reset=weekly_reset,
            plan=plan,
            source=source
        )

        state = self.get_state()
        self.quota_updated.emit(state)
        return state

    def set_manual(self, remaining_pct, reset_hours, reset_minutes, plan=None):
        now = time.time()
        remaining = max(0.0, min(100.0, float(remaining_pct)))
        used = 100.0 - remaining
        total_seconds = int(reset_hours) * 3600 + int(reset_minutes) * 60
        reset_epoch = now + total_seconds if total_seconds > 0 else 0.0

        config.update_quota(
            remaining=remaining,
            used=used,
            reset_epoch=reset_epoch,
            plan=plan or config.get("plan_tier", "Google AI Pro"),
            source="Manual Set"
        )
        state = self.get_state()
        self.quota_updated.emit(state)
        return state

    def log_prompt(self, prompt_type="standard"):
        """Deducts compute points and starts/advances 5h rolling window."""
        now = time.time()
        remaining = config.get("limit_remaining", 100.0)
        reset_epoch = config.get("reset_time_epoch", 0.0)
        plan = config.get("plan_tier", "Google AI Pro")

        # Multiplier depends on plan
        cost_map = {
            "standard": 2.5,     # ~40 standard prompts per 5h
            "heavy": 6.0,        # ~16 code/heavy prompts
            "thinking": 12.0     # ~8 deep reasoning prompts
        }
        cost = cost_map.get(prompt_type, 3.0)
        if "Ultra" in plan:
            cost *= 0.4
        elif "Plus" in plan:
            cost *= 0.8
        elif "Free" in plan:
            cost *= 1.5

        new_remaining = max(0.0, remaining - cost)
        new_used = 100.0 - new_remaining

        # If no active reset window, start 5 hour (18000s) rolling window
        if reset_epoch <= now:
            reset_epoch = now + 5 * 3600

        config.update_quota(
            remaining=new_remaining,
            used=new_used,
            reset_epoch=reset_epoch,
            source="Manual Prompt Log"
        )
        state = self.get_state()
        self.quota_updated.emit(state)
        return state

    def _parse_time_str(self, s):
        if not s:
            return 0
        s = s.lower().strip()
        import re
        total_sec = 0
        # hours: 3 hr, 3h, 3 saat
        h_match = re.search(r'(\d+)\s*(?:h|hr|hours?|saat)', s)
        if h_match:
            total_sec += int(h_match.group(1)) * 3600
        # minutes: 45 min, 45m, 45 dakika
        m_match = re.search(r'(\d+)\s*(?:m|min|mins|minutes?|dakika|dk)', s)
        if m_match:
            total_sec += int(m_match.group(1)) * 60
        # seconds: 30 sec, 30s, 30 saniye
        s_match = re.search(r'(\d+)\s*(?:s|sec|secs|seconds?|saniye)', s)
        if s_match:
            total_sec += int(s_match.group(1))
        # HH:MM format
        colon_match = re.search(r'(\d{1,2}):(\d{2})', s)
        if colon_match and total_sec == 0:
            total_sec = int(colon_match.group(1)) * 3600 + int(colon_match.group(2)) * 60
        return total_sec

tracker_engine = QuotaTrackerEngine()
