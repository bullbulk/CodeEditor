from PyQt5.QtWidgets import QFileDialog


class Toolbar:
    def open_file(self, name=None):
        if not name:
            filename = QFileDialog.getOpenFileName(
                self, 'Select file...', '',
                'All files (*)'
            )[0]
            if not filename:
                return
        else:
            filename = name
        self.filename = filename
        self.file = open(filename, 'r', encoding='utf-8')
        self.field.setPlainText(self.file.read().replace(' ' * 4, '\t'))
        self.field.setVisible(True)

    def new_file(self):
        filename = QFileDialog.getSaveFileName(
            self, 'Save to...', '',
            'All files (*)'
        )[0]
        if not filename:
            return

        open(filename, 'w').close()
        self.open_file(filename)
