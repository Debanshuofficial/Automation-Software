import logging
from typing import Callable, Optional

class AppLogger:
    def __init__(self):
        self.logger = logging.getLogger("udise_new_student")
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        self.ui_callback: Optional[Callable[[str], None]] = None

    def set_ui_callback(self, callback: Callable[[str], None]):
        self.ui_callback = callback

    def _log(self, level, msg):
        if level == logging.INFO:
            self.logger.info(msg)
        elif level == logging.WARNING:
            self.logger.warning(msg)
        elif level == logging.ERROR:
            self.logger.error(msg)
            
        if self.ui_callback:
            self.ui_callback(f"{msg}\n")

    def info(self, msg: str):
        self._log(logging.INFO, msg)

    def warning(self, msg: str):
        self._log(logging.WARNING, msg)

    def error(self, msg: str):
        self._log(logging.ERROR, msg)
