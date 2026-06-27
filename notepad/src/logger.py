"""Runtime logging to logs/runtime.log with 10MB rotation."""

import os
import sys
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "runtime.log")
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


def _rotate():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_SIZE:
        bak = LOG_FILE + ".1"
        if os.path.exists(bak):
            os.remove(bak)
        os.rename(LOG_FILE, bak)


def log(level: str, message: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    _rotate()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def log_exception():
    import traceback
    log("ERROR", "".join(traceback.format_exception(*sys.exc_info())).rstrip())


def setup_excepthook():
    """Redirect unhandled Python exceptions to runtime.log."""
    def handler(exc_type, exc_value, exc_tb):
        import traceback
        os.makedirs(LOG_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] [FATAL] {''.join(tb_lines).rstrip()}\n")
        sys.__excepthook__(exc_type, exc_value, exc_tb)
    sys.excepthook = handler
