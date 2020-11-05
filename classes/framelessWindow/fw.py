from typing import Tuple

import screeninfo
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent, QImage, QFont
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QPushButton, QMenu, QAction


class Button(QPushButton):
    def __init__(self, win, menu, name):
        super().__init__(win)

        self.setMenu(menu)
        self.setText(name)
        self.setObjectName('Button')
        self.setFixedSize(win.icons_w, win.icons_h)
        self.setFont(QFont('Calibri', pointSize=11))
        self.setStyleSheet('QPushButton {'
                                'background-color: #3c3f41;'
                                'border-style: outset;'
                                'color: #a9b7c6;'
                            '}'
                            
                            'QPushButton:pressed {'
                                'background-color: #4B6EAF;'
                            '}')


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(762, 600)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


class FramelessWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, size: Tuple[int, int] = (1000, 500),
                 max_size: Tuple[int, int] = None,
                 min_size: Tuple[int, int] = None,
                 *, window_icon: str, close_icon: str,
                 maximize_icon: str, restore_icon: str, minimize_icon: str):
        """
        :param min_size: minimum window size (width, height)
        :param window_icon: window icon filename
        :param close_icon: window close button filename
        """
        self.buttons_width = 0

        self.minimized = False
        self.close_icon = close_icon
        self.maximize_icon = maximize_icon
        self.restore_icon = restore_icon
        self.minimize_icon = minimize_icon
        self.window_icon_im = window_icon

        display = screeninfo.get_monitors()[0]
        self.display_w, self.display_h = display.width, display.height
        self.icons_w = int(self.display_w / 1600 * 50)
        self.icons_h = int(self.display_h / 900 * 25)

        for var, icon in self.check_icons().items():
            raise FileNotFoundError(f'Icon for {var} in {icon} not found. Please, fill the settings.py correctly')

        super(FramelessWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.setGeometry(0, 0, *size)
        if min_size:
            self.setMinimumSize(*min_size)
        if max_size:
            self.setMaximumSize(*max_size)

        self.title_bar = QHBoxLayout(self)
        self.window_icon = QLabel(self)
        icon = Image.open(window_icon).resize([int(self.display_h / 900 * 16)] * 2)
        icon_pxmap = QPixmap.fromImage(
            QImage(
                icon.tobytes(),
                icon.size[0], icon.size[1],
                QImage.Format_ARGB32
            )
        )
        self.window_icon.setPixmap(icon_pxmap)
        self.window_icon.setStyleSheet(f'margin-left: 8px')
        self.window_icon.resize(self.icons_h, self.icons_h)
        self.title_bar.addWidget(self.window_icon)

        self.setup_title_buttons()

        self.move_label = QLabel(self)
        self.move_label.move(self.window_icon.width() + self.buttons_width, 0)
        self.move_label.setMinimumSize(
            self.width() - self.icons_w * 3 - self.window_icon.size().width(),
            self.window_icon.size().height())
        self.title_bar.addWidget(self.move_label)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.in_resize = False
        self.on_move = False

        self.mouse_press_pos = None
        self.mouse_move_pos = None

        self.before_resize = None

    def setup_menu(self):
        file_menu = QMenu(self)
        self.file_menu_b = Button(self, file_menu, 'File')
        self.file_menu_b.move(self.window_icon.width() + 8 + self.buttons_width, 0)
        self.buttons_width += self.file_menu_b.width()
        self.open_action = QAction(file_menu)
        self.open_action.setText('Open')
        self.new_action = QAction(file_menu)
        self.new_action.setText('New')
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        self.title_bar.addWidget(self.file_menu_b)

        settings_menu = QMenu(self)
        self.tools_menu_b = Button(self, settings_menu, 'Tools')
        self.tools_menu_b.move(self.window_icon.width() + 8 + self.buttons_width, 0)
        self.buttons_width += self.tools_menu_b.width()
        self.settings_action = QAction(settings_menu)
        self.settings_action.setText('Preferences')
        settings_menu.addAction(self.settings_action)
        self.title_bar.addWidget(settings_menu)

    def resizeEvent(self, event):
        self.in_resize = True
        self.close_button.move(self.size().width() - self.icons_w, 0)
        self.maximize_button.move(self.size().width() - self.icons_w * 2, 0)
        self.restore_button.move(self.size().width() - self.icons_w * 2, 0)
        self.minimize_button.move(self.size().width() - self.icons_w * 3, 0)
        self.move_label.setFixedSize(
            self.width() - self.icons_w * 3 - self.window_icon.size().width() - self.buttons_width,
            self.window_icon.size().height()
        )
        super(FramelessWindow, self).resizeEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse_press_pos = None
        self.mouse_move_pos = None
        if self.mouse_on_title(event):
            self.on_move = True

        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.mouse_move_pos = event.globalPos()

        super().mousePressEvent(event)

    #
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.in_resize:
            super(FramelessWindow, self).mouseMoveEvent(event)
            self.in_resize = False
            return

        if self.mouse_move_pos and self.mouse_press_pos:
            if self.mouse_on_title(event) or self.on_move:
                if event.buttons() == QtCore.Qt.LeftButton:
                    if self.isMaximized():
                        self.restore()
                    current_pos = self.mapToGlobal(self.pos())
                    global_pos = event.globalPos()
                    diff = global_pos - self.mouse_move_pos
                    self.move(self.mapFromGlobal(current_pos + diff))
                    self.mouse_move_pos = global_pos

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.on_move = False
        super(FramelessWindow, self).mouseReleaseEvent(event)

    def mouse_on_title(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if x in range(self.move_label.size().width() + self.window_icon.size().width() +
                      self.buttons_width + 1) and y in range(self.move_label.size().height() + 1):
            return True

    def mouseDoubleClickEvent(self, event):
        if self.mouse_on_title(event):
            if self.windowState() == Qt.WindowMaximized:
                self.restore()
            else:
                self.maximize()

    def maximize(self):
        self.maximize_button.setVisible(False)
        self.restore_button.setVisible(True)
        self.before_resize = self.geometry()
        self.setWindowState(Qt.WindowMaximized)

    def minimize(self):
        self.minimized = True
        self.setWindowState(Qt.WindowMinimized)

    def restore(self):
        self.restore_button.setVisible(False)
        self.maximize_button.setVisible(True)
        self.before_resize = None
        self.setWindowState(Qt.WindowNoState)

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if a0.type() == QtCore.QEvent.WindowStateChange:
            if self.minimized and not self.isMinimized():
                self.minimized = False
                if self.restore_button.isVisible():
                    self.maximize()

    def check_icons(self):
        errors = {}
        try:
            open(self.close_icon, 'r')
        except FileNotFoundError:
            errors['close_icon'] = self.close_icon
        try:
            open(self.maximize_icon, 'r')
        except FileNotFoundError:
            errors['maximize_icon'] = self.maximize_icon
        try:
            open(self.restore_icon, 'r')
        except FileNotFoundError:
            errors['restore_icon'] = self.restore_icon
        try:
            open(self.minimize_icon, 'r')
        except FileNotFoundError:
            errors['minimize_icon'] = self.minimize_icon

        return errors

    def setup_title_buttons(self):
        self.close_button = QPushButton(self)
        self.close_button.setFixedSize(QSize(self.icons_w, self.window_icon.size().height()))
        self.close_button.setStyleSheet('QPushButton { border-style: outset }'
                                        'QPushButton::hover { background-color: red }')
        self.minimize_button = QPushButton(self)
        self.minimize_button.setFixedSize(QSize(self.icons_w, self.window_icon.size().height()))
        self.minimize_button.setStyleSheet('QPushButton { border-style: outset }'
                                           'QPushButton::hover { background-color: grey }')
        self.maximize_button = QPushButton(self)
        self.maximize_button.setFixedSize(QSize(self.icons_w, self.window_icon.size().height()))
        self.maximize_button.setStyleSheet('QPushButton { border-style: outset }'
                                           'QPushButton::hover { background-color: grey }')
        self.restore_button = QPushButton(self)
        self.restore_button.setFixedSize(QSize(self.icons_w, self.window_icon.size().height()))
        self.restore_button.setStyleSheet('QPushButton { border-style: outset}'
                                          'QPushButton::hover { background-color: grey }')

        close_icon = QIcon(self.get_pixmap(self.close_icon, self.icons_w, self.icons_h))
        self.close_button.setIcon(close_icon)
        self.close_button.setIconSize(self.close_button.size())
        self.close_button.clicked.connect(self.close)

        maximize_icon = QIcon(self.get_pixmap(self.maximize_icon, self.icons_w, self.icons_h))
        self.maximize_button.setIcon(maximize_icon)
        self.maximize_button.setIconSize(self.maximize_button.size())
        self.maximize_button.clicked.connect(self.maximize)

        restore_icon = QIcon(self.get_pixmap(self.restore_icon, self.icons_w, self.icons_h))
        self.restore_button.setIcon(restore_icon)
        self.restore_button.setIconSize(self.restore_button.size())
        self.restore_button.clicked.connect(self.restore)
        self.restore_button.setVisible(False)

        minimize_icon = QIcon(self.get_pixmap(self.minimize_icon, self.icons_w, self.icons_h))
        self.minimize_button.setIcon(minimize_icon)
        self.minimize_button.setIconSize(self.minimize_button.size())
        self.minimize_button.clicked.connect(self.minimize)

        self.setup_menu()

        self.title_bar.addWidget(self.close_button)
        self.title_bar.addWidget(self.maximize_button)
        self.title_bar.addWidget(self.minimize_button)
        self.title_bar.addWidget(self.minimize_button)

    def get_pixmap(self, im, w, h):
        icon = Image.open(im).resize((w, h))
        return QPixmap.fromImage(
            QImage(
                icon.tobytes(),
                icon.size[0], icon.size[1],
                QImage.Format_ARGB32
            )
        )
