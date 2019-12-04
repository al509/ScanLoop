"""
 V.15.7
 04.12.2019
"""

# -*- coding: utf-8 -*-

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
    main = MainWindow()
    main.show()

    return main

    
if __name__ == '__main__':         

    m = main()