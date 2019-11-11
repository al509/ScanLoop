"""
 V.14
 11.11.2019
"""

# -*- coding: utf-8 -*-

import sys
import traceback
from PyQt5.QtWidgets import QApplication

from Windows.MainWindow import MainWindow

# from PyQt5.QtCore import QMetaType%
# QMetaType.qRegisterMetaType("object")
# QMetaType.qRegisterMetaType("list")
# QMetaType.qRegisterMetaType("dict")

if __name__ == '__main__':
    try:
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
#        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print('Exception')  
        traceback.print_exc()

#if __name__ == "__main__":
#    def run_app():
#        app = QApplication(sys.argv)
#        mainWin = MainWindow()
#        mainWin.show()
#        app.exec_()
#    run_app()