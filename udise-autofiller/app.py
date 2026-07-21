import os
import sys

# Add project root to sys.path to allow running from anywhere
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.main_window import MainWindow

def main():
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
