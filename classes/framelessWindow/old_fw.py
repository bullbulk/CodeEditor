from typing import Tuple

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QPushButton

from ui import Ui_MainWindow


class FramelessWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, min_size: Tuple[int, int], window_icon: str, close_icon: str):
        """
        :param min_size: minimum window size (width, height)
        :param window_icon: window icon filename
        :param close_icon: window close button filename
        """
        super(FramelessWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setMinimumSize(*min_size)

        self.title_bar = QHBoxLayout(self)
        self.window_icon = QLabel(self)
        self.window_icon.setPixmap(QPixmap(window_icon))
        self.window_icon.setStyleSheet('margin-left: 8px')
        self.title_bar.addWidget(self.window_icon)

        self.close_button = QPushButton(self)
        self.close_button.setFixedSize(QSize(50, self.window_icon.size().height()))
        self.close_button.setStyleSheet('QPushButton {border-style: outset}'
                                        'QPushButton::hover { background-color: red }')
        close_icon = QIcon(close_icon)
        self.close_button.setIcon(close_icon)
        self.close_button.setIconSize(self.close_button.size())
        self.close_button.clicked.connect(self.close)

        self.move_label = QLabel(self)
        self.move_label.move(self.window_icon.size().width(), 0)
        self.move_label.setMinimumSize(
            self.width() - self.close_button.size().width() - self.window_icon.size().width(),
            self.window_icon.size().height())
        self.title_bar.addWidget(self.move_label)
        self.title_bar.addWidget(self.close_button)

        self.in_resize = False
        self.on_move = False

        self.mouse_press_pos = None
        self.mouse_move_pos = None

    def resizeEvent(self, event):
        self.in_resize = True
        self.close_button.move(self.size().width() - 50, 0)
        self.move_label.setFixedSize(self.width() - self.close_button.size().width() - self.window_icon.size().width(),
                                     self.window_icon.size().height())

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse_press_pos = None
        self.mouse_move_pos = None
        if self.mouse_move_state(event):
            self.on_move = True

        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.mouse_move_pos = event.globalPos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.in_resize:
            super(FramelessWindow, self).mouseMoveEvent(event)
            self.in_resize = False
            return

        if self.mouse_move_pos and self.mouse_press_pos:
            if self.mouse_move_state(event) or self.on_move:
                if event.buttons() == QtCore.Qt.LeftButton:
                    current_pos = self.mapToGlobal(self.pos())
                    global_pos = event.globalPos()
                    diff = global_pos - self.mouse_move_pos
                    self.move(self.mapFromGlobal(current_pos + diff))
                    self.mouse_move_pos = global_pos

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.on_move = False
        super(FramelessWindow, self).mouseReleaseEvent(event)

    def mouse_move_state(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if x in range(self.move_label.size().width() + self.window_icon.size().width() + 1) and \
                y in range(self.move_label.size().height() + 1):
            return True
