import os


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)