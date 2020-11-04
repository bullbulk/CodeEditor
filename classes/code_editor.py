import sys
import threading
from subprocess import Popen

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QFrame

from classes.toolbar import Toolbar

PAIR_SYMBOLS = {'(': ')', "'": "'", '"': '"', '{': '}', '[': ']'}


class Writer(threading.Thread):
    def __init__(self, filename, text):
        super().__init__()
        self.filename = filename
        self.text = text

    def run(self):
        with open(self.filename, 'w') as f:
            f.write(self.text)


class CodeEditor(QWidget, Toolbar):
    def __init__(self, widget):
        super(CodeEditor, self).__init__(widget)

        self.field = QPlainTextEdit(self)
        self.field.setFrameStyle(QFrame.NoFrame)
        self.field.setFont(QFont('Consolas', pointSize=14))
        self.field.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.field.setStyleSheet('border-style: solid; border-width: 2px; border-color: #515151')

        self.field.setVisible(False)
        self.field.textChanged.connect(self.code_change)

        self.code = ''
        self.changed = False
        self.tabs = 0

        self.filename = None
        self.file = None

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
        self.save()

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
