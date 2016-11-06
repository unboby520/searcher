# coding: utf8
#
# searcher - misc
#
# Author: ilcwd
# Create: 14/11/10
#
import os
import random


def import_module(package):
    m = __import__(package)
    current = os.path.dirname(m.__file__)

    if '.' in package:
        apppath = os.path.join(current, *package.split('.')[1:])
    else:
        apppath = current

    submodules = []
    for fname in os.listdir(apppath):
        if not fname.endswith('.py') or fname.startswith('_'):
            continue

        submodules.append(fname[:-3])

    return __import__(package, fromlist=submodules)


def generate_request_id(now=0):
    return '%x-%08x' % (now, random.randint(0, 0xFFFFFFFF))


def main():
    pass


if __name__ == '__main__':
    main()