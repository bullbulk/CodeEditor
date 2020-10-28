import sys

from PyQt5.QtWidgets import QApplication

import settings
from classes.main_window import MainWindow
from utils import utils

if __name__ == '__main__':
    app = QApplication(sys.argv)
    utils.setup_excepthook()
    win = MainWindow(*settings.get_settings().values())
    win.show()
    sys.exit(app.exec_())
