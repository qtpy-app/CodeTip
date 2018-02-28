#!/usr/bin/env python


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#import Queue
import re


class SpinBoxDelegate(QItemDelegate):
#    def __init__(self):
        
    
    def paint(self, painter, option, index):

        pixmap = self.getPixmat(index)[0]
#            print(option.rect, type(option.rect))
#        painter.fillRect(option.rect, option.palette.highlight())
        if pixmap.size().width()=='' and pixmap.size().height()=='':
            painter.drawPixmap(option.rect,pixmap )
        else:
            painter.drawPixmap( option.rect.x(),option.rect.y(), pixmap.size().width(), pixmap.size().height() ,pixmap )
        
        if self.getPixmat(index)[1]==False:
            super(SpinBoxDelegate, self).paint(painter, option, index)   
   
    def sizeHint(self, option, index):
        pixmap=self.getPixmat(index)[0]
#        if pixmap.size() < QSize(100, 100)
        return pixmap.size()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, lineEdit, index):
        value = index.model().data(index, Qt.EditRole)
#        print(value)
        lineEdit.setText(value)

    def setModelData(self, lineEdit, model, index):
        value = lineEdit.text()

        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    
    def getPixmat(self, index):
        editor = str(index.data())
        pixmap=QPixmap()
        if 'jpg' in editor.split('.'):
            pixmap.load(editor)
            return pixmap, True
        else:
            return pixmap, False
        
#        return True
