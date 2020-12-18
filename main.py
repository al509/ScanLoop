"""
 18.12.2020
"""

# -*- coding: utf-8 -*-

__version__='18.2.1'
from packaging import version
from conda import __version__ as condaVersion


import sys
if 'init_modules' in globals(  ):
    # second or subsequent run: remove all but initially loaded modules
    for m in sys.modules.keys(  ):
        if m not in init_modules:
            del(sys.modules[m])
else:
    # first run: find out which modules were initially loaded
    init_modules = sys.modules.keys(  )

from PyQt5 import QtWidgets
from Windows.MainWindow import MainWindow


def main():
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    main = MainWindow(version=__version__)
    main.show()
    if (version.parse(condaVersion) > version.parse("4.9.0")):
        sys.exit(app.exec())
    return main


if __name__ == '__main__':

    m = main()