# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'analyzer_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(462, 187)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(360, 10, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 321, 151))
        self.groupBox.setObjectName("groupBox")
        self.lineEdit_min_wave = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_min_wave.setGeometry(QtCore.QRect(70, 20, 41, 20))
        self.lineEdit_min_wave.setObjectName("lineEdit_min_wave")
        self.label_15 = QtWidgets.QLabel(self.groupBox)
        self.label_15.setGeometry(QtCore.QRect(20, 10, 41, 31))
        self.label_15.setWordWrap(True)
        self.label_15.setObjectName("label_15")
        self.lineEdit_max_wave = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_max_wave.setGeometry(QtCore.QRect(70, 50, 41, 20))
        self.lineEdit_max_wave.setObjectName("lineEdit_max_wave")
        self.label_17 = QtWidgets.QLabel(self.groupBox)
        self.label_17.setGeometry(QtCore.QRect(130, 80, 41, 41))
        self.label_17.setWordWrap(True)
        self.label_17.setObjectName("label_17")
        self.lineEdit_min_peak_level = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_min_peak_level.setGeometry(QtCore.QRect(170, 80, 31, 31))
        self.lineEdit_min_peak_level.setObjectName("lineEdit_min_peak_level")
        self.checkBox_plot_results_separately = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_plot_results_separately.setGeometry(QtCore.QRect(140, 30, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.checkBox_plot_results_separately.setFont(font)
        self.checkBox_plot_results_separately.setWhatsThis("")
        self.checkBox_plot_results_separately.setTristate(False)
        self.checkBox_plot_results_separately.setObjectName("checkBox_plot_results_separately")
        self.label_31 = QtWidgets.QLabel(self.groupBox)
        self.label_31.setGeometry(QtCore.QRect(10, 80, 61, 41))
        self.label_31.setWordWrap(True)
        self.label_31.setObjectName("label_31")
        self.lineEdit_number_of_peaks_to_search = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_number_of_peaks_to_search.setGeometry(QtCore.QRect(80, 80, 31, 31))
        self.lineEdit_number_of_peaks_to_search.setObjectName("lineEdit_number_of_peaks_to_search")
        self.label_32 = QtWidgets.QLabel(self.groupBox)
        self.label_32.setGeometry(QtCore.QRect(230, 80, 61, 41))
        self.label_32.setWordWrap(True)
        self.label_32.setObjectName("label_32")
        self.lineEdit_min_peak_distance = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_min_peak_distance.setGeometry(QtCore.QRect(280, 79, 31, 31))
        self.lineEdit_min_peak_distance.setObjectName("lineEdit_min_peak_distance")
        self.checkBox_find_widths = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_find_widths.setGeometry(QtCore.QRect(240, 30, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.checkBox_find_widths.setFont(font)
        self.checkBox_find_widths.setWhatsThis("")
        self.checkBox_find_widths.setTristate(False)
        self.checkBox_find_widths.setObjectName("checkBox_find_widths")
        self.label_16 = QtWidgets.QLabel(self.groupBox)
        self.label_16.setGeometry(QtCore.QRect(20, 40, 41, 31))
        self.label_16.setWordWrap(True)
        self.label_16.setObjectName("label_16")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Analyzer options"))
        self.lineEdit_min_wave.setText(_translate("Dialog", "1530"))
        self.label_15.setText(_translate("Dialog", "<html><head/><body><p>λ<span style=\" vertical-align:sub;\">min</span>, nm</p></body></html>"))
        self.lineEdit_max_wave.setText(_translate("Dialog", "1590"))
        self.label_17.setText(_translate("Dialog", "<html><head/><body><p>Peak height, dB</p></body></html>"))
        self.lineEdit_min_peak_level.setText(_translate("Dialog", "3"))
        self.checkBox_plot_results_separately.setText(_translate("Dialog", "Plot  separately"))
        self.label_31.setText(_translate("Dialog", "<html><head/><body><p>Number of peaks to be find</p></body></html>"))
        self.lineEdit_number_of_peaks_to_search.setText(_translate("Dialog", "1"))
        self.label_32.setText(_translate("Dialog", "<html><head/><body><p>Distance between peaks</p></body></html>"))
        self.lineEdit_min_peak_distance.setText(_translate("Dialog", "60"))
        self.checkBox_find_widths.setText(_translate("Dialog", "find widths"))
        self.label_16.setText(_translate("Dialog", "<html><head/><body><p>λ<span style=\" vertical-align:sub;\">max</span>, nm</p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

