
from Windows.MainWindow import MainWindow
from PyQt5 import QtWidgets
from packaging import version
import sys
__version__ = '20.3.36'
__date__ = '2023.01.19'


# from conda import __version__ as condaVersion


def main():
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    main_app = MainWindow(version=__version__, date=__date__)
    main_app.show()
    # Uncomment only if application doesn't finish properly
    # sys.exit(app.exec())
    return main_app


if __name__ == '__main__':
    m = main()
