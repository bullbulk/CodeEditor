import sys
from subprocess import Popen

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QFrame, QFileDialog, QMessageBox

from classes.highlighter import PythonHighlighter

PAIR_SYMBOLS = {'(': ')', "'": "'", '"': '"', '{': '}', '[': ']'}


class CodeEditor(QWidget):
    def __init__(self, widget):
        super(CodeEditor, self).__init__(widget)

        self.field = QPlainTextEdit(self)
        self.field.setFrameStyle(QFrame.NoFrame)
        self.field.setFont(QFont('Consolas', pointSize=14))
        self.field.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.field.setStyleSheet('border-style: solid; border-width: 2px; border-color: #515151')

        self.field.setVisible(False)
        self.highlighter = PythonHighlighter(self.field.document())
        self.enable_help()

        self.code = ''
        self.changed = False
        self.tabs = 0

        self.filename = None
        self.file = None

        self.kwargs = {}

    def enable_help(self):
        self.field.textChanged.connect(self.code_change)

    def disable_help(self):
        self.field.textChanged.connect(self.code_change_help_disabled)

    def pass_f(self):
        pass

    def enable_highlighter(self):
        self.highlighter.enable()
        self.rehighlight()

    def disable_highlighter(self):
        self.highlighter.disable()
        self.rehighlight()

    def rehighlight(self):
        self.highlighter.rehighlight()
        self.field.setPlainText(self.field.toPlainText() + '.')
        self.field.setPlainText(self.field.toPlainText()[:-1])

    def code_change(self):
        if self.changed:
            self.changed = False
            return
        text = list(self.field.toPlainText())

        cursor = self.field.textCursor()
        cur_pos = cursor.position()

        if len(text) < len(self.code):
            _diff = self.code[-1] if self.code else ''
            if _diff == '\t':
                self.tabs = self.tabs - 1 if self.tabs > 0 else 0

            self.code = self.code[:-1]
            return

        cur_new_pos = None

        diff = text[cur_pos - 1] if text else ''
        if diff == ':':
            self.tabs += 1
            self.code = ''.join(text)

        try:

            if diff == '\n' and self.tabs:
                text.append('\t' * self.tabs)
                cur_new_pos = -1

            elif diff in PAIR_SYMBOLS:
                text.insert(cur_pos, PAIR_SYMBOLS[diff])
                cur_new_pos = cur_pos

            elif diff == '\t' and text[cur_pos] in PAIR_SYMBOLS.values():
                cur_new_pos = cur_pos
                del text[len(text) - text[::-1].index('\t') - 1]

        except IndexError:
            pass

        self.changed = True
        text = ''.join(text)
        self.field.setPlainText(text)

        if cur_new_pos:
            cur_pos = cur_new_pos

        cursor.setPosition(cur_pos)

        self.field.setTextCursor(cursor)
        self.code = text

    def code_change_help_disabled(self):
        if self.changed:
            self.changed = False
            return
        self.changed = True
        text = self.field.toPlainText()
        self.code = text

    def run_script(self):
        self.generate_bat()
        Popen(['start', 'cmd', '/c', r'data\run.bat'], shell=True)

    def generate_bat(self):
        with open('data/run.bat', 'w') as f:
            f.write('@echo off\n')
            f.write(f'echo {sys.executable} {self.filename}\n')
            f.write('echo.\n')
            f.write(f'{sys.executable} {self.filename}\n')
            f.write('echo.\n')
            f.write('pause\n')
            f.write('exit')

    def save(self, agreed=False):
        if not agreed:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle('Save before run or check')
            msg.setText('Source must be saved\nOK to save')
            y = msg.addButton('OK', QMessageBox.YesRole)
            msg.addButton('Cancel', QMessageBox.RejectRole)
            msg.exec()
            if msg.clickedButton() == y:
                save = True
            else:
                return
        else:
            save = True
        if save:
            with open(self.filename, 'w') as f:
                f.write(self.code.replace('\t', ' ' * 4))
        return save

    def open_file(self, name=None):
        reply = self.close_file()
        if not reply:
            return
        if not name:
            filename = QFileDialog.getOpenFileName(
                self, 'Select file...', '',
                'All files (*)'
            )[0]
            if not filename:
                return
        else:
            filename = name
        try:
            self.file = open(filename, 'r', encoding='utf-8')
        except FileNotFoundError:
            return
        self.filename = filename
        self.field.setPlainText(self.file.read().replace(' ' * 4, '\t'))
        self.field.setVisible(True)

    def new_file(self):
        reply = self.close_file()
        if not reply:
            return
        filename = QFileDialog.getSaveFileName(
            self, 'Save to...', '',
            'All files (*)'
        )[0]
        if not filename:
            return

        open(filename, 'w').close()
        self.open_file(filename)

    def close_file(self):
        if not self.filename:
            return True
        if self.code == open(self.filename, 'r', encoding='utf-8') \
                .read().replace(' ' * 4, '\t'):
            return True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Save on close')
        msg.setText('Do you want to save this document before closing?')
        y = msg.addButton('Yes', QMessageBox.YesRole)
        n = msg.addButton('No', QMessageBox.NoRole)
        c = msg.addButton('Cancel', QMessageBox.RejectRole)
        msg.exec()

        if msg.clickedButton() == y:
            self.save(agreed=True)
            return True
        if msg.clickedButton() == n:
            return True
        if msg.clickedButton() == c:
            return False
