# -*- coding: utf-8 -*-

"""
Module implementing aboutMe_Dialog.
"""
from PyQt5 import  QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

#from Ui_aboutMe import Ui_aboutMe_Dialog
import webbrowser
import codetip_qrc_rc

class AboutMe_Dialog(QMainWindow):

    def __init__(self, parent=None):

        super(AboutMe_Dialog, self).__init__(parent)
#        self.setupUi(self)
        loadUi("ui/aboutMe.ui", self)
        self.textBrowser.setOpenLinks(False)
        self.textBrowser.anchorClicked.connect(self.anchorClickedSlot)#
    def anchorClickedSlot(self, url):
        return webbrowser.open_new_tab(url.toString())	        

    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = AboutMe_Dialog()
    ui.show()
    sys.exit(app.exec_())

