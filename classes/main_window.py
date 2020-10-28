import json
import os
import sys
from subprocess import Popen

from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from classes.framelessWindow.fw import FramelessWindow
from classes.code_editor import CodeEditor
from utils import utils


class MainWindow(FramelessWindow):
    def __init__(self, size, max_size, min_size, window_icon, close_icon, maximize_icon, restore_icon,
                 minimize_icon):
        super().__init__(size=size, max_size=max_size, min_size=min_size, window_icon=window_icon,
                         close_icon=close_icon,
                         maximize_icon=maximize_icon, restore_icon=restore_icon, minimize_icon=minimize_icon)

        self.arg_size = size

        self.config = utils.get_config()
        self.restore_state()

        self.setStyleSheet(
            "QMainWindow { background-color: #3c3f41 }\n"
            "QMenuBar  { background-color: #3c3f41 }\n"
            "QWidget#MainWindow { background-color: #3c3f41 }\n"
            "QWidget#codeWidget { background-color: #2b2b2b }\n"
            "QPlainTextEdit { color: #a9b7c6; background-color: #2b2b2b }\n"
        )

        self.code_widget = CodeEditor(self)
        self.code_widget.setObjectName('codeWidget')
        self.code_widget.move(8, self.window_icon.height())

        self.code_widget.code_field.verticalScrollBar().setStyleSheet(
            'border: 0px;'
            'background: solid #3c3f41;'
            'width: 15px;'
            'margin: 0px 0px 0px 0px'
        )

    def restore_state(self):
        maximized = self.config.get('maximized', True)
        last_geometry = self.config.get('geometry', (0, 0, *self.arg_size))
        if maximized:
            self.setWindowState(Qt.WindowMaximized)
            self.restore_button.setVisible(True)
            self.maximize_button.setVisible(False)
        self.setGeometry(*last_geometry)

    def save_config(self):
        g = self.geometry()
        self.config['geometry'] = g.x(), g.y(), g.width(), g.height()
        self.config['maximized'] = self.isMaximized()
        json.dump(self.config, open('data/config.json', 'w'))
        if 'code.py' in os.listdir('data'):
            os.remove('data/code.py')
        if 'stdin' in os.listdir('data'):
            os.remove('data/stdin')

    def close(self):
        self.save_config()
        super(MainWindow, self).close()

    def resizeEvent(self, event):
        self.code_widget.resize(self.size().width() - 16,
                                self.size().height() - self.window_icon.size().height() - 8)
        self.code_widget.code_field.resize(self.code_widget.size())
        super(MainWindow, self).resizeEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if int(event.modifiers()) == int(Qt.ControlModifier + Qt.ShiftModifier):
            if event.key() == Qt.Key_F10:
                with open('data/code.py', 'w', encoding='utf-8') as f:
                    code = self.code_widget.code_field.toPlainText()
                    f.write(code)
                    stdin = open('data/stdin', 'w', encoding='utf-8')
                    stdin.write('2342')
                    proc = Popen([sys.executable, 'data/code.py'], stdin=stdin, stdout=sys.stdout)
