# -*- coding: utf-8 -*-

"""
Module implementing FramelessWindow.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sip

from Ui_framelesswindow import Ui_FramelessWindow


class FramelessWindow(QWidget, Ui_FramelessWindow):

    def __init__(self, parent=None):
        super(FramelessWindow, self).__init__(parent, Qt.FramelessWindowHint|Qt.Tool)
        self.setupUi(self)
        self._timer = QTimer()
        self.contentLayout = QHBoxLayout(self)
        
        self.restoreButton.setVisible(False)
        
        self.setAttribute(Qt.WA_TranslucentBackground);#透明
        
#        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint);
        self.boolCursor=True
        self.frame=10
        self._padding = 3 # 设置边界宽度为5        
        self._padding2 = 3 # 设置边界宽度为5        
        self.setMouseTracking(True) # 设置widget鼠标跟踪   
        self._move_drag = False        # 设置鼠标跟踪判断扳机默认值
        self._corner_drag = False
        self._bottom_drag = False
        self._top_drag = False
        self._right_drag = False
        self._left_drag = False
        #=============================== 托盘图标 ================================#
        self.tray = QSystemTrayIcon(self) #创建系统托盘对象  
        self.icon = QIcon('../db/360ask.png')  #创建图标  
        self.tray.setIcon(self.icon)  #设置系统托盘图标
        self.tray_menu = QMenu(QApplication.desktop()) #创建菜单  
        self.RestoreAction = QAction(u'还原 ', self, triggered=self.show) #添加一级菜单动作选项(还原主窗口)  
        self.QuitAction = QAction(u'退出 ', self, triggered=qApp.quit) #添加一级菜单动作选项(退出程序)  
        self.tray_menu.addAction(self.RestoreAction) #为菜单添加动作  
        self.tray_menu.addAction(self.QuitAction)  
        self.tray.setContextMenu(self.tray_menu) #设置系统托盘菜单  
        self.tray.show()

        
    @pyqtSlot()
    def on_applicationStateChanged(state):
        pass
    
    @pyqtSlot()
    def on_windowTitlebar_doubleClicked(self):
        if (self.windowState()==Qt.WindowNoState) :
            self.on_maximizeButton_clicked();
        
        elif (self.windowState()== Qt.WindowMaximized):
            self.on_restoreButton_clicked();
        
    @pyqtSlot()
    def on_minimizeButton_clicked(self):
        self.setWindowState(Qt.WindowMinimized);
    
    @pyqtSlot()
    def on_restoreButton_clicked(self):
        self.restoreButton.setVisible(False);
        self.maximizeButton.setVisible(True);
        self.setWindowState(Qt.WindowNoState);
#        self.styleWindow(True, True);
#    
    @pyqtSlot()
    def on_maximizeButton_clicked(self):
        self.restoreButton.setVisible(True);
        self.maximizeButton.setVisible(False);
        self.setWindowState(Qt.WindowMaximized);
#        self.styleWindow(True, False);
    
    @pyqtSlot()
    def on_closeButton_clicked(self):
        self.close();
        sip.delete(self.tray)
    def changeEvent(self,event):
        pass

    def setContent(self, w):
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        
        self.contentLayout.addWidget(w);
        self.windowContent.setLayout(self.contentLayout);

#    def styleWindow(self, bActive, bNoState):


    def setTitle(self, text):
        self.titleText.setText(text)
        
            
    def resizeEvent(self, QResizeEvent):
        # 自定义窗口调整大小事件
#        self.titleText.setFixedWidth(self.width()) # 将标题标签始终设为窗口宽度
        # 分别移动三个按钮到正确的位置
#        try:
#            self.closeButton.move(self.width() - self.closeButton.width(), 0)
#        except:
#            pass
#        try:
#            self.minimizeButton.move(self.width() - (self.closeButton.width() + 1) * 3 + 1, 0)
#        except:
#            pass
#        try:
#            self.maximizeButton.move(self.width() - (self.closeButton.width() + 1) * 2 + 1, 0)
#        except:
#            pass
        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + self._padding2)
                           for y in range(1, self.height() - self._padding)]        
        
        self._left_rect = [QPoint(x, y) for x in range(0 - self._padding , 0 + self._padding2)
                           for y in range(1, self.height() - self._padding)]
        
        self._top_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                         for y in range(0 - self._padding, 0 + self._padding2)]
        
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                         for y in range(self.height() - self._padding, self.height() + self._padding2)]
        
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + self._padding2)
                                    for y in range(self.height() - self._padding, self.height() + self._padding2)]

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._left_rect):
            # 鼠标左键点击左侧边界区域
            self._left_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._top_rect):
            # 鼠标左键点击顶侧边界区域
            self._top_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self.titleText.height()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势
        self.shaprCursor(QMouseEvent)
        print(QCursor.pos())
    def shaprCursor(self, QMouseEvent):
        print('------------')
        if  self.boolCursor==False:
            self._timer.stop()
            self.setCursor(Qt.ArrowCursor)
        if QMouseEvent.pos() in self._corner_rect:
            self.boolCursor=True
            self.setCursor(Qt.SizeFDiagCursor)
        elif QMouseEvent.pos() in self._bottom_rect:
            self.boolCursor=True
            self.setCursor(Qt.SizeVerCursor)
        elif QMouseEvent.pos() in self._top_rect:
            self.boolCursor=True
            self.setCursor(Qt.SizeVerCursor)
        elif QMouseEvent.pos() in self._right_rect:
            self.boolCursor=True
            self.setCursor(Qt.SizeHorCursor)
        elif QMouseEvent.pos() in self._left_rect:
            self.boolCursor=True
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.boolCursor=False
            self.setCursor(Qt.ArrowCursor)
        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        if Qt.LeftButton and self._left_drag:
            # 左侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._top_drag:
            # 上侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
#        elif Qt.LeftButton and self._move_drag:
#            # 标题栏拖放窗口位置
#            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
#            QMouseEvent.accept()

    def moveEvent(self, e):    
        print('cx:', QCursor.pos().x(),'cy:', QCursor.pos().y())
        print('gx:', self.geometry().x(),'gy:', self.geometry().y())
        print('dx:', QApplication.desktop().screenGeometry().width(),'dy:', QApplication.desktop().screenGeometry().height())

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._top_drag = False
        self._right_drag = False
        self._left_drag = False
        
    def paintEvent(self, e):        
        painter=QPainter(self);
        painter.setRenderHint(QPainter.Antialiasing); #反锯齿;
        painter.setBrush(QBrush(QColor(49,54,59)));
        painter.setPen(Qt.transparent);
        rect = self.rect();
        rect.setWidth(rect.width() );
        rect.setHeight(rect.height() );
        painter.drawRoundedRect(rect, 12, 12);
    def enterEvent(self, event):
        self._timer.timeout.connect(lambda:self.shaprCursor(event))
        self._timer.start(50)
        
        if(self.x() == self.frame-self.width()):
            self.move(-self.frame,self.y())
            #左边
        elif(self.y() == self.frame-self.height()+self.y()-self.geometry().y()):
            self.move(self.x(),-self.frame)
            #上边
        elif(self.x() == self.frame-self.width()):
            self.move(-self.frame,self.y())
            #右边            
    def leaveEvent(self,event):    
        cx,cy = QCursor.pos().x(),QCursor.pos().y()
        
        if(cx >= self.x() and cx <= self.x()+self.width()
            and cy >= self.y() and cy <= self.geometry().y()):
            return#title bar

        elif(self.x() < 0 and QCursor.pos().x()>0):
            self.move(self.frame-self.width(),self.y())
            #左边
            
        elif(self.y() < 0 and QCursor.pos().y()>0):
            self.move(self.x(), self.frame-self.height()+self.y()-self.geometry().y())
            #上边

        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
  
    ui = FramelessWindow()
    ui.show()
    sys.exit(app.exec_())
        


