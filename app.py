import sys
import os
import signal
import threading
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal, QObject, QEasingCurve
from PyQt6.QtGui import QGuiApplication, QFont, QColor
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from pynput import keyboard

# ================= CONFIGURATION =================
SUMMON_KEY = keyboard.KeyCode.from_char('q')  # Your summon key
DELAY_SECONDS = 56.0                          # Reminder delay
BANNER_DWELL_MS = 4000                        # Milliseconds to stay visible (e.g., 4000 = 4 seconds)

# Sizing & Position
POPUP_WIDTH = 580                             # Wider banner
POPUP_HEIGHT = 230                            # Taller banner
MARGIN_RIGHT = 50                             # Distance from right edge
MARGIN_BOTTOM = 680                           # Higher up from bottom edge (adjust as needed)
# =================================================


class Bridge(QObject):
    trigger_popup = pyqtSignal()


class FadePopup(QWidget):
    def __init__(self):
        super().__init__()

        # Non-intrusive window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow |
            Qt.WindowType.WindowDoesNotAcceptFocus |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        layout = QVBoxLayout()
        self.label = QLabel("⚠️ REFRESH SUMMONS ⚠️")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(20, 20, 24, 240);
                color: #FFB830;
                border: 3px solid #FF5C5C;
                border-radius: 16px;
                padding: 16px;
                letter-spacing: 1px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 220))
        shadow.setOffset(0, 6)
        self.label.setGraphicsEffect(shadow)

        layout.addWidget(self.label)
        self.setLayout(layout)
        self.resize(POPUP_WIDTH, POPUP_HEIGHT)

        # Animation setup
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # CONNECT ONLY ONCE: Check if opacity reached 0 before hiding
        self.anim.finished.connect(self._on_animation_finished)

        # Dedicated dwell timer to prevent orphaned timers
        self.dwell_timer = QTimer(self)
        self.dwell_timer.setSingleShot(True)
        self.dwell_timer.timeout.connect(self._fade_out)

    def _on_animation_finished(self):
        # Only hide when it has faded out to 0
        if self.windowOpacity() <= 0.05:
            self.hide()

    def position_on_secondary_screen(self):
        screens = QGuiApplication.screens()
        primary = QGuiApplication.primaryScreen()

        target_screen = screens[1] if len(screens) > 1 and screens[0] == primary else screens[0]
        if len(screens) > 1 and screens[1] == primary:
            target_screen = screens[0]

        geom = target_screen.geometry()
        x = geom.x() + geom.width() - self.width() - MARGIN_RIGHT
        y = geom.y() + geom.height() - self.height() - MARGIN_BOTTOM
        self.move(x, y)

    def show_alert(self):
        # Cancel any pending dwell or fade-out
        self.dwell_timer.stop()
        self.anim.stop()

        self.position_on_secondary_screen()
        self.setWindowOpacity(0.0)
        self.show()

        # Fade In (250ms)
        self.anim.setDuration(250)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

        # Start dwell countdown (e.g. 3500ms)
        self.dwell_timer.start(3500)

    def _fade_out(self):
        self.anim.stop()
        self.anim.setDuration(700)
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(0.0)
        self.anim.start()


class SummonWatcher:
    def __init__(self, bridge):
        self.bridge = bridge
        self.timer = None

    def _on_timeout(self):
        self.bridge.trigger_popup.emit()

    def on_press(self, key):
        if key == SUMMON_KEY:
            if self.timer and self.timer.is_alive():
                self.timer.cancel()
            self.timer = threading.Timer(DELAY_SECONDS, self._on_timeout)
            self.timer.daemon = True
            self.timer.start()

    def start(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.daemon = True
        listener.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Allow Python to catch SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, lambda *args: os._exit(0))

    # Heartbeat timer yields control to Python runtime every 300ms
    sigint_timer = QTimer()
    sigint_timer.timeout.connect(lambda: None)
    sigint_timer.start(300)

    bridge = Bridge()
    popup = FadePopup()
    bridge.trigger_popup.connect(popup.show_alert)

    watcher = SummonWatcher(bridge)
    watcher.start()

    print(f"Tracking summon key '{SUMMON_KEY}'. Press Ctrl+C in terminal to stop.")
    sys.exit(app.exec())