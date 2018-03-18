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
        item=self.getPixmat(index, option)
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
        item=self.getPixmat(index, option)
        if item['bool']==True:
            width=item['width']
            height=item['height']
            return QSize(width,height)
        else:
            return super(SpinBoxDelegate, self).sizeHint(option, index)

    def createEditor(self, parent, option, index):

        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, lineEdit, index):
        value = index.model().data(index, Qt.EditRole)
        lineEdit.setText(str(value))

    def setModelData(self, lineEdit, model, index):
        value = lineEdit.text()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    
    def getPixmat(self,  index, option):
        '''如果index中有.jpg或.png，把路径转换为pixmap。<br>
        如果图片宽 > 格 且高 < 150 ， 设置宽300，高为原高；<br>
        如果图片宽 <150 且高 > 150 ， 设置宽为原宽，高为150；<br>
        如果图片宽 <150 且高 < 150 ， 设置宽为原宽，高为原高；<br>
        '''
        editor = str(index.data())
        pixmap=QPixmap()
        if 'jpg' in editor.split('.') or 'png' in editor.split('.'):
            pixmap.load(editor)
            if pixmap.size().width()>option.rect.width() and pixmap.size().height()<150:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':300,
                    'height':pixmap.size().height()}
            elif pixmap.size().width()<150 and pixmap.size().height()>150:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':pixmap.size().width(),
                    'height':150}
            elif pixmap.size().width()>150 and pixmap.size().height()>150:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':150,
                    'height':150}            
            elif pixmap.size().width()<150  and pixmap.size().height()<150:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':pixmap.size().width(),
                    'height':pixmap.size().height()}
            else:
                return {'pixmap':pixmap, 'bool':True, 
                    'width':pixmap.size().width(),
                    'height':pixmap.size().height()}

        else:
            return {'pixmap':'可输入文字', 'bool':False}

    def eventFilter(self, obj, event):
        '''按下Ctrl+V后，如果粘贴板是图片，命名图片保存在ima文件夹下，<br>
           把名字给粘贴板，再把图片还原到粘贴板。'''
        if event.type()==QEvent.KeyPress: 
            if  event.key()== Qt.Key_V and event.modifiers() == Qt.ControlModifier :
                
                clipboard = QApplication.clipboard()  
                data = clipboard.mimeData()
                if data.hasImage():             
                    filename= 'db/ima/'+time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.jpg'
                    data.imageData().save(filename,'JPG',90)
                    im = data.imageData()
                    clipboard.setText(filename)
                    self.timer.singleShot(200, lambda:clipboard.setImage(im))  
                    
        return False
