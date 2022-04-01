
__version__='20.2.1'
__date__='2022.04.01'


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
    # Uncomment only if application doesn't finish properly 
    # sys.exit(app.exec())
    return main_app


if __name__ == '__main__': 

    m = main()
