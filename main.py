import sys
from PyQt5.QtWidgets import QApplication
from src.ui.app import MiAplicacion
from src.config import GREEN_TONIC_STYLE

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GREEN_TONIC_STYLE)
    window = MiAplicacion()
    window.show()
    sys.exit(app.exec_())