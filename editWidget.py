# -*- coding: utf-8 -*-

"""
Module implementing aboutMe_Dialog.
"""
from PyQt5 import  QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

import webbrowser

class Edit_Dialog(QDialog):

    def __init__(self, parent=None):

        super(Edit_Dialog, self).__init__(parent)
        loadUi("ui/editBox.ui", self)
        self.okButton.setShortcut( "Alt+Return")
        self.lineEdit.setPlaceholderText('字段名称')
        self.lineEdit_2.setPlaceholderText('默认值(选填)')
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Edit_Dialog()
    ui.show()
    sys.exit(app.exec_())
