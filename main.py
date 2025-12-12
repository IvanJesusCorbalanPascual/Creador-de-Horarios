import sys, os
from PyQt5.QtWidgets import QApplication
from src.views.main_window import MiAplicacion
from src.config import GREEN_TONIC_STYLE

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GREEN_TONIC_STYLE)
    window = MiAplicacion()
    window.show()
    app.exec_()