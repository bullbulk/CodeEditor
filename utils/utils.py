import json
import os
import sys


def setup_excepthook():
    _excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        _excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook


def get_config() -> dict:
    if 'data' not in os.listdir():
        os.mkdir('data')
    if 'config.json' not in os.listdir('data'):
        json.dump({}, open('data/config.json', 'w'))
    c = json.load(open('data/config.json', 'r'))
    if type(c) != dict:
        raise TypeError('Invalid config file. The result of deserialization must be a dict. Delete the config.json.')
    return c


def clear_data():
    for i in os.listdir('data'):
        if i not in ['config.json', 'style.qss']:
            os.remove('data/' + i)
