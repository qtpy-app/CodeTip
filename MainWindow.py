# -*- coding: utf-8 -*-

from PyQt5 import  QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase , QSqlTableModel, QSqlQueryModel, QSqlQuery
from PyQt5.QtCore import Qt 

import sqlite3
import sip
from Ui_MainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow,):
    updateView=pyqtSignal()
    def __init__(self, parent=None, *args):

        super(MainWindow, self).__init__(parent, *args)
        self.setupUi(self)
        
        self.search=QLineEdit()
        self.search.setPlaceholderText('搜索命令')
        
        self.addaction = QtWidgets.QAction( "添加", self,)
        self.delaction = QtWidgets.QAction( "删除(Ct+D)", self)
        self.freshaction = QtWidgets.QAction("刷新(F5)", self)
        self.saveaction = QtWidgets.QAction("保存", self)

        self.toolBar.addAction(self.addaction)
        self.toolBar.addWidget(self.search)
        self.toolBar.addAction(self.freshaction)
        self.toolBar.addAction(self.delaction)

        self.delaction.setShortcut( "Ctrl+D")
        self.freshaction.setShortcut( "F5")
        
        self.checkbox=QCheckBox()
        self.checkbox.setToolTip('置顶该窗口')
        self.checkbox.clicked.connect(self.setTop)        

        self.helpButton=QPushButton('?')
        self.helpButton.setToolTip('帮助')        
        font = QFont()
        font.setPointSize(6)
        self.helpButton.setFont(font)
        
        self.indexLabel=QLabel('当前为记录表')
        
        self.statusBar.addPermanentWidget(self.checkbox)        
        self.statusBar.addPermanentWidget(self.helpButton)        
        self.statusBar.addPermanentWidget(self.indexLabel) 
        
        #=============================== 托盘图标 ================================#
        self.tray = QSystemTrayIcon(self) #创建系统托盘对象  
        self.icon = QIcon('db/360ask.png')  #创建图标  
        self.tray.setIcon(self.icon)  #设置系统托盘图标
        self.tray_menu = QMenu(QApplication.desktop()) #创建菜单  
        self.RestoreAction = QAction(u'还原 ', self, triggered=self.show) #添加一级菜单动作选项(还原主窗口)  
        self.QuitAction = QAction(u'退出 ', self, triggered=qApp.quit) #添加一级菜单动作选项(退出程序)  
        self.tray_menu.addAction(self.RestoreAction) #为菜单添加动作  
        self.tray_menu.addAction(self.QuitAction)  
        self.tray.setContextMenu(self.tray_menu) #设置系统托盘菜单  
        self.tray.show()
        #=============================== action & Singnal ================================#
        self.addaction.triggered.connect(self.addData)
        self.delaction.triggered.connect(self.deleteData)
        self.freshaction.triggered.connect(self.fresh)
        self.search.returnPressed.connect(self.queryRecord)
        
#        self.checkbox.clicked.connect(self.se)
        #===============================   db   ======================================#
        
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./db/database.db')
            
        #===================================== langue & sort =======================================#
        self.langModel  = QSqlTableModel(); 
        self.initializeModel(self.langModel, 'languages')
        self.langModel.setHeaderData(0, Qt.Horizontal, "语言")
        self.langModel.setHeaderData(1, Qt.Horizontal, "排序")
        self.langModel.setHeaderData(2, Qt.Horizontal, "可见")  
        self.langModel.setEditStrategy( QSqlTableModel.OnFieldChange)
        self.langModel.setFilter('visual=1')
        self.langModel.dataChanged.connect(self.getNewTableName)#!!!!!!!!!!!
        
        self.langView = self.createView("Langue_View", self.langModel)
        self.langView.clicked.connect(self.findrow)
        self.langView.horizontalHeader().setSectionResizeMode(3)#列宽设置
        
        self.sort_Model =  QSortFilterProxyModel(); 
        self.sort_Model.setObjectName('sort_Model')
        self.sort_Model.setSourceModel(self.langModel);
        self.sort_Model.sort (1, 0);#排序，0升序，1降序，下同
        self.langView.setModel (self.sort_Model);    
#        self.sort_Model.setFilterRegExp(QRegExp("1"));
#        self.sort_Model.setFilterKeyColumn(2)
        '''一列右对齐  待补充'''

        self.verticalLayout_4.addWidget(self.langView)
        #================================= code =====================================#
        self.codeModel=QSqlTableModel()
        self.codeModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.codeModel.setHeaderData(0, Qt.Horizontal, "操作")
        self.codeModel.setHeaderData(1, Qt.Horizontal, "代码")
        self.codeModel.setObjectName('codeModel')
        
        self.codeView = self.createView("Code_View", self.codeModel)
        self.codeView.clicked.connect(self.findrow)
        self.codeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.codeView.customContextMenuRequested.connect(self.myListWidgetContext)#右键请求         
#        self.codeView.customContextMenuRequested.connect(self.findrow)#右键请求         
        self.verticalLayout.addWidget(self.codeView)       
#        #================================= Timer=====================================#
        self.timer=QTimer()
        #================================= search ===================================#
        self.searchModel=QSqlQueryModel()
#        self.initializeModel(self.searchModel, 'langue')
        self.searchModel.setHeaderData(0, Qt.Horizontal, "操作")
        self.searchModel.setHeaderData(1, Qt.Horizontal, "代码")        
        self.searchModel.setObjectName('searchModel')

        self.searchView=self.createView("Search_View", self.searchModel)
        self.verticalLayout_2.addWidget(self.searchView)
        #================================  query  ===================================#
        self.query = QSqlQuery()

        #================================  installEventFilter  ===================================#
        self.langView.installEventFilter(self) 
        self.codeView.installEventFilter(self) 
        #================================ initData ==================================#
        self.row=0
        self.frame=1
        self.oldTableName='' 
        self.newTableName=''     
        #================================ setting ==================================#
#        self.setTabOrder(self.langView, self.codeView);
        self.model=self.sort_Model
        self.setting=QSettings('./db/setting.ini', QSettings.IniFormat)
        self.getSetting()
        
    def eventFilter(self, obj, event):  
        if event.type()==QEvent.KeyPress:    
            if event.key()== Qt.Key_Return and event.modifiers() == Qt.AltModifier :
                if obj == self.codeView:
                    print('123')
                    self.edit=QTextEdit()
                    self.edit.setWindowModality(2)#设置为应用程序模态，0:非模态，1:非模态
                    self.edit.show()
                    
            elif event.key()==Qt.Key_Return or event.key()==Qt.Key_Tab:
                if obj == self.langView:
                    self.timer.singleShot(200, self.addTable)
                    tablename=self.sort_Model.data(self.sort_Model.index(self.row,0))
                    self.initializeModel(self.codeModel, tablename)#!!!!!!!!!!!!!!!!      
                    
                if obj == self.codeView:
                    if self.model.tableName()=='languages':
                        self.timer.singleShot(200, self.reselect)
                        self.timer.singleShot(400, self.addTable)

        return False    
        
    def enterEvent(self, event):
        if(self.x() == self.frame-self.width()):
            self.move(-self.frame,self.y())
            #左边
        elif(self.y() == self.frame-self.height()+self.y()-self.geometry().y()):
            self.move(self.x(),-self.frame)
            #上边
    def leaveEvent(self,event):    
        cx,cy=QCursor.pos().x(),QCursor.pos().y()
        
        if(cx >= self.x() and cx <= self.x()+self.width()
            and cy >= self.y() and cy <= self.geometry().y()):
            return#title bar

        elif(self.x() < 0 and QCursor.pos().x()>0):
            self.move(self.frame-self.width(),self.y())
            #左边
            
        elif(self.y() < 0 and QCursor.pos().y()>0):
            self.move(self.x(), self.frame-self.height()+self.y()-self.geometry().y())
    #def mouseReleaseEvent(self, event):
        #peint('x:',self.x(),';y:',self.y())        
        
    def moveEvent(self, event):
        print(self.geometry(), self.width(), self.height())
        print(self.geometry().x(), self.geometry().y())
    def initializeModel(self, model, tablename):
        model.setTable(tablename)
        model.select()

    def createView(self, title, model):
        view =  QTableView()
        view.setModel(model)
        view.setWindowTitle(title)
        view.horizontalHeader().setSectionResizeMode(3)#列宽设置
        view.verticalHeader().setSectionResizeMode(3)#行高设置
        view.horizontalHeader().setStretchLastSection(True); #充满列宽
        view.verticalHeader().setVisible(False)#隐藏行标题
        view.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)#标题左对齐
       
        return view  
        
    def myListWidgetContext(self):
        popMenu =QMenu()
        
        popMenu.addAction(u'插入行',self.deleteData)
        popMenu.addAction(u'在左增加字段',self.addField)
        popMenu.addAction(u'在右增加字段',self.addField)
        popMenu.exec_(QCursor.pos())#鼠标位置
        popMenu.addAction(u'删除字段',self.deleteData)
        #currentColumn 当前列；columnCount()总列数；currentIndex().row()在父节点下的行号
 
    def addField(self):    
        pass
            
    def findrow(self, i):
        self.row= i.row()
        print(i.column())
        self.model=self.sender().model()
        
        self.getOldTableName()
        
        if self.model==self.sort_Model:
           
            tablename=self.sort_Model.data(self.sort_Model.index(self.row,0))
            self.initializeModel(self.codeModel, tablename)#!!!!!!!!!!!!!!!!
            
            if self.stackedWidget.currentIndex()==0:
                if self.codeModel.rowCount()==0:
                    self.query.exec("INSERT INTO %s values('inputI', 'inputII')"%(tablename))
            
            else:
                self.queryRecord()
            

    def addData(self, ):
        try:
            self.model.insertRows(self.model.rowCount(), 1)
        except:
            pass
        index=self.model.index(0, 1)
        
        if self.model.objectName()=='codeModel':
            defaultValue=''
            self.model.setData(index, defaultValue)
            
        elif self.model.objectName()=='sort_Model':
            index2=self.model.index(0, 2)
            self.model.setData(index2, 1)#设置为可见
            
            defaultValue=self.model.data(self.model.index(self.sort_Model.rowCount()-1, 1))+10
            self.model.setData(index, defaultValue)#设置排序序号

    def addTable(self):
        
        if self.model==self.sort_Model:
            tablename=self.model.data(self.model.index(self.model.rowCount()-1, 0))
        elif self.model==self.codeModel:
            tablename=self.model.data(self.model.index(self.row,  0))
        
        self.query.exec("CREATE VIRTUAL TABLE %s USING fts5(Operation , Code )"%(tablename))
        
        if tablename not in self.db.tables():
            conn = sqlite3.connect('./db/database.db')
            c = conn.cursor()
            try:
                text="CREATE TABLE %s\
                   (ID INT PRIMARY KEY     NOT NULL,\
                   NAME           TEXT    NOT NULL,\
                   AGE            INT     NOT NULL,\
                   ADDRESS        CHAR(50));"%(str(tablename))
                c.execute(text)
                conn.commit()
            except:
                QMessageBox.critical(self,"表名错误","名字不合法，请修改后按回车键!") 
            conn.close()            
        self.reselect()
    def deleteData(self):
        if self.model == self.codeModel :
            if self.codeModel.tableName()=='languages' :
                deleteTableName=self.model.data(self.model.index(self.row,0))#!
                if deleteTableName != 'languages':
                    self.model.removeRows(self.row, 1)#删除数据 
                    self.query.exec('DROP TABLE %s'%(deleteTableName))
            else:
                self.model.removeRows(self.row, 1)#删除数据 
        
        elif self.model == self.sort_Model:
           if self.oldTableName != 'languages' and self.model.data(self.model.index(self.row,0))!= 'languages' :
               self.model.setData(self.sort_Model.index(self.row, 2), 0)
        self.codeModel.submitAll()
        
        self.reselect()
        
    def getOldTableName(self):
        self.oldTableName = self.sort_Model.data(self.sort_Model.index(self.row,0))#!
#        print(
#        'self.row:', self.row, '\n', 
#        'self.oldname:', self.oldTableName, 
#        )        
#    
    def getNewTableName(self):
        self.newTableName = self.sort_Model.data(self.sort_Model.index(self.row,0))
        #ALTER TABLE 旧表名 RENAME TO 新表名
        self.query.exec('ALTER TABLE %s RENAME TO %s'%(self.oldTableName, self.newTableName))        
  
    def queryRecord(self):
        self.stackedWidget.setCurrentIndex(1)  
        if self.indexLabel.text()!='当前为查询结果':
            self.indexLabel.setText('当前为查询结果')
        queryText="SELECT * FROM %s WHERE %s MATCH '%s';"%(self.oldTableName, self.oldTableName, self.search.text())

        self.searchModel.setQuery(queryText)
        
#        self.reselect()

    def fresh(self):
        self.stackedWidget.setCurrentIndex(0)
        self.indexLabel.setText('当前为记录表')
  
    def reselect(self):
        try:
            self.model.select() 
            self.langModel.select()
            self.sort_Model.select()
        except:
            self.langModel.select()
            
    def getSetting(self):            
        if(self.setting.contains("SelectTable/selectRow")):   #此节点是否存在该数据
            self.row=int(self.setting.value("SelectTable/selectRow"))
       
        if(self.setting.contains("Position/x")):   #此节点是否存在该数据
            x=int(self.setting.value("Position/x"))
            y=int(self.setting.value("Position/y"))
            w=int(self.setting.value("Position/w"))
            h=int(self.setting.value("Position/h"))
    
            self.resize(w, h)
#            self.move(x, y)
            
        self.langView.selectRow(self.row)
        tablename=self.sort_Model.data(self.sort_Model.index(self.row,0))
        self.initializeModel(self.codeModel, tablename)#!!!!!!!!!!!!!!!!              
        
    def closeEvent(self, event):
        self.setting.setValue("SelectTable/selectRow",str(self.row));#设置key和value，也就是参数和值  
        self.setting.setValue("Position/x",str(self.frame-self.width()));#设置key和value，也就是参数和值  
        self.setting.setValue("Position/y",str(self.geometry().y()));#设置key和value，也就是参数和值  
        self.setting.setValue("Position/w",str(self.width()));#设置key和value，也就是参数和值  
        self.setting.setValue("Position/h",str(self.height()));#设置key和value，也就是参数和值  
        sip.delete(self.tray)
    def setTop(self):
        if self.checkbox.isChecked():
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.Widget)
        if self.isVisible()==False:
            self.setVisible(True);

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # if you want to using this QSS, please pip install qdarkstyle.
    import qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    def excepthook(type, value, trace):
        try:
            pass
        except:
            pass
        sys.__excepthook__(type, value, trace)
    sys.excepthook = excepthook
    
    ui=MainWindow()
    ui.show()
    sys.exit(app.exec_())
