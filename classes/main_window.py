import json

from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from classes.code_editor import CodeEditor
from classes.framelessWindow.fw import FramelessWindow
from utils import utils


class MainWindow(FramelessWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = kwargs

        self.arg_size = kwargs['size']

        with open('data/style.css') as f:
            self.setStyleSheet(f.read())

        self.code_widget = CodeEditor(self)
        self.code_widget.setObjectName('codeWidget')
        self.code_widget.move(8, self.window_icon.height())

        self.open_action.triggered.connect(self.code_widget.open_file)
        self.new_action.triggered.connect(self.code_widget.new_file)
        self.settings_action.triggered.connect(self.code_widget.settings)

        self.config = utils.get_config()
        self.restore_state()

    def restore_state(self):
        maximized = self.config.get('maximized', True)
        last_geometry = self.config.get('geometry', (0, 0, *self.arg_size))
        self.setGeometry(*last_geometry)
        if maximized:
            self.setWindowState(Qt.WindowMaximized)
            self.restore_button.setVisible(True)
            self.maximize_button.setVisible(False)

        recent_file = self.config.get('recent_filename', None)
        if recent_file:
            self.code_widget.open_file(recent_file)

    def save_config(self):
        g = self.before_resize if self.before_resize else self.geometry()
        self.config['geometry'] = g.x(), g.y(), g.width(), g.height()
        self.config['maximized'] = self.isMaximized()
        self.config['recent_filename'] = self.code_widget.filename
        json.dump(self.config, open('data/config.json', 'w'))

        utils.clean_data()

    def close(self):
        self.save_config()
        self.code_widget.save()
        super(MainWindow, self).close()

    def resizeEvent(self, event):
        self.code_widget.resize(self.size().width() - 16,
                                self.size().height() - self.window_icon.size().height() - 8)
        self.code_widget.field.resize(self.code_widget.size())
        super(MainWindow, self).resizeEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if int(event.modifiers()) == Qt.ShiftModifier:
            if event.key() == Qt.Key_F10:
                self.code_widget.run_script()
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_O:
                self.code_widget.open_file()
            if event.key() == Qt.Key_N:
                self.code_widget.new_file()
