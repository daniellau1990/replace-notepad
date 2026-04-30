import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from src.app import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("LiteNotepad")
    app.setOrganizationName("LiteNotepad")

    # Ensure default Notes directory exists
    default_dir = os.path.join(os.path.expanduser("~"), "Documents", "Notes")
    os.makedirs(default_dir, exist_ok=True)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
