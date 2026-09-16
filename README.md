# MapleStory Janus Reminder

A small desktop reminder that watches for the summon key and displays a notification after the configured delay.

## Prerequisites

- Windows 10 or later
- Python 3.10 or later
- A working Python installation available as `python`
- Permission to monitor keyboard input globally

## Dependencies

- `PyQt6` - desktop notification window and animations
- `pynput` - global keyboard monitoring

```powershell
python -m pip install PyQt6 pynput
```

## Run

With the virtual environment activated:

```powershell
python app.py
```

The application monitors the `Q` key by default. Pressing `Q` starts or resets the reminder timer. After the configured delay, a notification appears on the secondary monitor when one is available.

Press `Ctrl+C` in the terminal to stop the application.

## Configuration

Edit the constants near the top of `app.py` to change the behavior:

- `SUMMON_KEY` - key that starts the timer
- `DELAY_SECONDS` - delay before the reminder appears
- `BANNER_DWELL_MS` - intended banner display duration
- `MARGIN_RIGHT` and `MARGIN_BOTTOM` - notification position offsets

## Notes

- Keep the terminal window open while the reminder is running.
- The keyboard listener may require additional Windows permissions depending on system security settings.
- The current implementation expects a secondary display when available and otherwise uses the primary display.
