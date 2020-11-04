# TAKEN FROM https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting AND MODIFIED

import builtins

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def _format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    if not color:
        color = '#A9B7C6'

    _color = QColor()
    _color.setNamedColor(color)

    format_ = QTextCharFormat()
    format_.setForeground(_color)
    if 'bold' in style:
        format_.setFontWeight(QFont.Bold)
    if 'italic' in style:
        format_.setFontItalic(True)

    return format_


STYLES = {
    'basic': _format(None),
    'keyword': _format('#CC7832'),
    'builtin': _format('#8888C6'),
    'special_function': _format('#B200B2'),
    'operator': _format(None),
    'brace': _format(None),
    'def+class': _format('#CC7832'),
    'string': _format('#6A8759'),
    'string2': _format('#6A8759'),
    'comment': _format('#808080', 'italic'),
    'self+cls': _format('#94558D'),
    'decorator': _format('#BBB529'),
    'numbers': _format('#6897BB'),
    'constant': _format('#9876AA'),
    'special_variables': _format(None)
}


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
        'with', 'as'
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        r'\+', '-', r'\*', '/', '//', r'\%', r'\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        r'\^', r'\|', r'\&', r'\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        r'\{', r'\}', r'\(', r'\)', r'\[', r'\]',
    ]

    special_variables = [
        '__name__', '__main__', '__file__', '__loader__', '__spec__', '__package__', '__builtins__'
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = [(r'.', 0, STYLES['basic'])]

        # Keyword, operator, brace, builtin and special words rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in PythonHighlighter.braces]
        rules += [(r'\b%s\b' % f, 0, STYLES['builtin'])
                  for f in dir(builtins)]
        rules.append((r'__\w+__', 0, STYLES['special_function']))  # special functions like __init__
        rules += [(r'\b%s\b' % v, 0, STYLES['special_variables'])  # special variables like __name__
                  for v in PythonHighlighter.special_variables]

        # All other rules
        rules += [
            # 'self and cls'
            (r'\bself|cls\b', 0, STYLES['self+cls']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b', 1, STYLES['def+class']),
            # 'class' followed by an identifier
            (r'\bclass\b', 1, STYLES['def+class']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format_ in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format_)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
