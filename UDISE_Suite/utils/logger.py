import logging
import os
from datetime import datetime
from typing import Callable, Optional

class AppLogger:
    def __init__(self, log_dir: str = "logs"):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        self.log_file = os.path.join(log_dir, "session.log")
        
        self.logger = logging.getLogger("UdiseAutoFiller")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)
            
        self.ui_callback: Optional[Callable[[str], None]] = None
        
    def set_ui_callback(self, callback: Callable[[str], None]):
        self.ui_callback = callback
        
    def _log_and_emit(self, level: int, message: str):
        self.logger.log(level, message)
        if self.ui_callback:
            # Only send simple message format to UI
            time_str = datetime.now().strftime('%H:%M:%S')
            self.ui_callback(f"{time_str}\n{message}\n")
            
    def info(self, message: str):
        self._log_and_emit(logging.INFO, message)
        
    def warning(self, message: str):
        self._log_and_emit(logging.WARNING, message)
        
    def error(self, message: str):
        self._log_and_emit(logging.ERROR, message)
