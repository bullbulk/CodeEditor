from classes.framelessWindow.fw import FramelessWindow


class SettingsWindow(FramelessWindow):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs, subwindow=True)

        self.setFixedSize(600, 300)
        geom = self.geometry()
        geom.moveCenter(parent.geometry().center())
        self.setGeometry(geom)

        self.add_settings()

    def add_settings(self):
        ...