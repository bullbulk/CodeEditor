import json
from typing import Dict, Union

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QCheckBox

from classes.framelessWindow.fw import FramelessWindow


class CheckBox(QCheckBox):
    def __init__(self, parent: QWidget, text: str, func):
        super().__init__(parent)
        self.setText(text)
        self.setFont(QFont('Calibri', pointSize=14))
        self.clicked.connect(func)


class SettingsWindow(FramelessWindow):
    def __init__(self, parent: Union[QWidget, None], settings: dict, **kwargs):
        super().__init__(parent, **kwargs, subwindow=True)
        self.parent = parent
        self.settings_json = settings

        self.setFixedSize(600, 300)
        geom = self.geometry()
        geom.moveCenter(parent.geometry().center())
        self.setGeometry(geom)

        self.settings_w = QWidget(self)
        self.layout = QVBoxLayout(self.settings_w)
        self.settings_w.setLayout(self.layout)
        self.settings_w.move(self.parent.window_icon.width(), self.parent.icons_h)
        self.settings_w.setFixedSize(self.size().width() - self.parent.window_icon.width() * 2,
                                     self.size().height() - self.parent.icons_h * 2)

        self.settings: Dict[str, CheckBox] = {}

        self.add_settings()

    def add_settings(self) -> None:
        self.settings['highlighting'] = CheckBox(self.settings_w, 'Syntax highlighting',
                                                 self.highlighting)
        self.settings['input_help'] = CheckBox(self.settings_w,
                                               'Enable undo/redo (Disables input help)',
                                               self.input_help)
        for i in self.settings.values():
            self.layout.addWidget(i)

    def highlighting(self) -> None:
        if self.settings['highlighting'].isChecked():
            self.parent.code_widget.enable_highlighter()
        else:
            self.parent.code_widget.disable_highlighter()
        self.save_settings()

    def input_help(self) -> None:
        if self.settings['input_help'].isChecked():
            self.parent.code_widget.disable_help()
        else:
            self.parent.code_widget.enable_help()
        self.save_settings()

    def save_settings(self) -> None:
        self.settings_json['highlighting'] = self.settings['highlighting'].isChecked()
        self.settings_json['input_help'] = self.settings['input_help'].isChecked()
        json.dump(self.settings_json, open('data/settings.json', 'w'))

