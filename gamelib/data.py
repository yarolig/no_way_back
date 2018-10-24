import os

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))
base_dir = os.path.normpath(os.path.join(data_py, '..'))


def filepath(filename):
    return os.path.join(data_dir, filename)


def musicpath(filename):
    return os.path.join(base_dir, 'music', filename)


def modelpath(filename):
    return os.path.join(base_dir, 'models', filename)


def userpath(filename):
    return os.path.join(base_dir, 'userdata', filename)
