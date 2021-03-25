"""
 25.03.2021
"""

# -*- coding: utf-8 -*-

__version__='18.3.0'
import sys
from packaging import version
from conda import __version__ as condaVersion
from PyQt5 import QtWidgets
from Windows.MainWindow import MainWindow



def main():
    '''Main function. Starts if you launch the program from this file.'''
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    main_app = MainWindow(version=__version__)
    main_app.show()
    if version.parse(condaVersion) > version.parse("4.9.0"):
        sys.exit(app.exec())
    return main_app


if __name__ == '__main__':

    m = main()
