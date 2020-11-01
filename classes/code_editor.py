import sys
from subprocess import Popen
import threading

from PyQt5 import QtGui
from PyQt5.QtGui import QFont, QKeySequence, QTextCursor
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QFrame, QUndoStack, QFileDialog, QDialog, QMessageBox

PAIR_SYMBOLS = {'(': ')', "'": "'", '"': '"', '{': '}', '[': ']'}


class Writer(threading.Thread):
    def __init__(self, filename, text):
        super().__init__()
        self.filename = filename
        self.text = text

    def run(self):
        with open(self.filename, 'w') as f:
            f.write(self.text)


class CodeField(QPlainTextEdit):
    def __init__(self, w):
        super(CodeField, self).__init__(w)

        self.setFrameStyle(QFrame.NoFrame)
        self.setFont(QFont('Consolas', pointSize=14))
        self.stack = QUndoStack(self)
        self.stack.setUndoLimit(100)
        self.undo, self.redo = self.stack.undo, self.stack.redo

        self.undo_ = False
        self.redo_ = False

        self.setLineWrapMode(QPlainTextEdit.NoWrap)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e == QKeySequence.Undo:
            self.undo_ = True
            self.undo()
        if e == QKeySequence.Redo:
            self.redo_ = True
            self.redo()
        super(CodeField, self).keyPressEvent(e)


class CodeEditor(QWidget):
    def __init__(self, widget):
        super(CodeEditor, self).__init__(widget)

        self.code_field = CodeField(self)
        self.code_field.setVisible(False)
        self.code_field.textChanged.connect(self.code_change)

        self.code = ''
        self.changed = False
        self.tabs = 0

        self.filename = None
        self.file = None

    def code_change(self):
        if self.changed:
            self.changed = False
            return
        text = list(self.code_field.toPlainText())

        cursor = self.code_field.textCursor()
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
        self.code_field.setPlainText(text)

        if cur_new_pos:
            cur_pos = cur_new_pos

        cursor.setPosition(cur_pos)

        self.code_field.setTextCursor(cursor)
        self.code = text
        self.save()

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
        self.code_field.setPlainText(self.file.read().replace(' ' * 4, '\t'))
        self.code_field.setVisible(True)

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

    def save(self):
        Writer(self.filename, self.code.replace('\t', ' ' * 4)).start()

    def new_file(self):
        filename = QFileDialog.getSaveFileName(
            self, 'Save to...', '',
            'All files (*)'
        )[0]
        if not filename:
            return

        open(filename, 'w').close()
        self.open_file(filename)