#!/usr/bin/env python


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import time

class SpinBoxDelegate(QItemDelegate, ):
    def __init__(self,  parent=None, *args):
        super(SpinBoxDelegate, self).__init__(parent, *args)
        self.timer=QTimer()

    def paint(self, painter, option, index):
        item=self.getPixmat( index)
        pixmap = item['pixmap']
#            print(option.rect, type(option.rect))
#        painter.fillRect(option.rect, option.palette.highlight())
        if item['bool']==False:
            super(SpinBoxDelegate, self).paint(painter, option, index)           
        
        else:
            painter.drawPixmap( option.rect.x() ,
                                option.rect.y() , 
                                item['width'] , 
                                item['height'] , 
                                pixmap )
   
    def sizeHint(self, option, index):
        item=self.getPixmat( index)
        if item['bool']==True:
            width=item['width']
            height=item['height']
            return QSize(width,height)
        else:
            value=str(index.data())
            value=value.split('\n')
            return QSize(option.rect.width(), len(value)*19)

    def createEditor(self, parent, option, index):

        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, lineEdit, index):
        value = index.model().data(index, Qt.EditRole)
        lineEdit.setText(value)

    def setModelData(self, lineEdit, model, index):
        value = lineEdit.text()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    
    def getPixmat(self,  index):
        editor = str(index.data())
        pixmap=QPixmap()
        if 'jpg' in editor.split('.') or 'png' in editor.split('.'):
            pixmap.load(editor)
            if pixmap.size().width()>150 and pixmap.size().height()<150:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':150,
                    'height':pixmap.size().height()}
            elif pixmap.size().width()<150 and pixmap.size().height()>150:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':pixmap.size().width(),
                    'height':150}
            elif pixmap.size().width()>150  and pixmap.size().height()>150:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':150,
                    'height':150}            
            elif pixmap.size().width()<150  and pixmap.size().height()<150:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':pixmap.size().width(),
                    'height':pixmap.size().height()}
        else:
            return {'pixmap':pixmap, 'bool':False}

    def eventFilter(self, obj, event):
        if event.type()==QEvent.KeyPress: 
            if  event.key()== Qt.Key_V and event.modifiers() == Qt.ControlModifier :       
                filename= 'ima/'+time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.jpg'
                clipboard = QApplication.clipboard()      
                data = clipboard.mimeData()
                if data.hasImage():
                    data.imageData().save(filename,'JPG',90)
                    im = data.imageData()
                    clipboard.setText(filename)
                    self.timer.singleShot(200, lambda:clipboard.setImage(im))
        return False
