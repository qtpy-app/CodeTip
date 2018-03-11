#-*- coding: utf-8 -*-

from PyQt5 import  QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *

import sqlite3
import sys

from Ui_MainWindow import Ui_MainWindow
from aboutMeWidget import AboutMe_Dialog
from editWidget import Edit_Dialog
from delegate import SpinBoxDelegate
sys.path.append('./CustomTitlebar')
from framelesswindow import FramelessWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, *args):

        super(MainWindow, self).__init__(parent,  *args)
        self.setupUi(self)
        #=============================== 工具栏 ================================#
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
        
        #=============================== 状态栏 ================================#
        self.checkbox=QCheckBox()
        self.checkbox.setToolTip('置顶该窗口')
        self.check=1
        self.checkbox.stateChanged.connect(self.setTop)  

        self.helpButton=QPushButton('？ ？ ？')
        self.helpButton.setToolTip('帮助')        
        font = QFont()
        font.setPointSize(6)
        self.helpButton.setFont(font)
        self.helpButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.helpButton.customContextMenuRequested.connect(self.helpMenu)#右键请求         
        
        self.stackLabel=QLabel('当前为记录表')
        
        self.statusBar.addPermanentWidget(self.checkbox)        
        self.statusBar.addPermanentWidget(self.helpButton)        
        self.statusBar.addPermanentWidget(self.stackLabel) 
        
        #=============================== action & Singnal ================================#
        self.addaction.triggered.connect(self.addData)
        self.delaction.triggered.connect(self.deleteData)
        self.freshaction.triggered.connect(self.fresh)
        self.search.returnPressed.connect(self.queryRecord)

        #===============================   db   ======================================#
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('./db/database.db')
        #================================ Timer ===================================#
        self.timer=QTimer()        
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
        self.codeModel = QSqlTableModel()##=======================================================!!
        self.codeModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.codeModel.setHeaderData(0, Qt.Horizontal, "操作")
        self.codeModel.setHeaderData(1, Qt.Horizontal, "代码")
        self.codeModel.setObjectName('codeModel')
        self.codeModel.sort (1, 0);#排序，0升序，1降序，下同
#        self.codeModel.dataChanged.connect(lambda:self.timer.singleShot(300, self.reselect));#排序，0升序，1降序，下同
        
        self.codeView = self.createView("Code_View", self.codeModel)
        self.codeView.clicked.connect(self.findrow)
        self.codeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.codeView.customContextMenuRequested.connect(self.codeMenu)#右键请求     
        delegate=SpinBoxDelegate(self.codeModel)
        self.codeView.setItemDelegate(delegate)      
        self.verticalLayout.addWidget(self.codeView)  
        self.codeView.setMouseTracking(True);

        self.codeView.entered['QModelIndex'].connect(self.showToolTip)

        #================================= search ===================================#
        self.searchModel=QSqlQueryModel()
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
        self.column=0
        self.frame=1
        self.oldTableName='' 
        self.newTableName=''
  
        #================================ setting ==================================#
        self.model=self.sort_Model
        self.setting=QSettings('./db/setting.ini', QSettings.IniFormat)
        self.getSetting()
        
    def eventFilter(self, obj, event):  
        '''
        键盘事件：如果是Alt+回车键，则弹多行文本框； <br>
                  如果是回车键或者Tab键，<br>
                      如果是 langView：<br>
                          0.2秒后调用添加表函数；<br>
                      如果是 codeView：<br>
                          如果是 总表 ，0.2秒后重新关联表，0.4秒后添加表；<br>
                          如果不是，则增加一行。<br>
        '''
        if event.type()==QEvent.KeyPress: 
            if event.key()== Qt.Key_Return and event.modifiers() == Qt.AltModifier :
                if obj == self.codeView:
                    text=str(self.codeModel.data(self.codeModel.index(self.row, self.column)))
                    fieldName = QInputDialog.getMultiLineText(self, '列名','请输入', text)#QInputDialog返回的是元组
                    if fieldName[-1]==True:
                        self.codeModel.setData(self.codeModel.index(self.row, self.column), fieldName[0])
                    
            if event.key()==Qt.Key_Return:
                
                if obj == self.langView:
                    self.timer.singleShot(200, self.addTable)
                    tablename=self.sort_Model.data(self.sort_Model.index(self.row,0))
                    self.initializeModel(self.codeModel, tablename)#!!!!!!!!!!!!!!!!      
                
                if obj == self.codeView:
#                    print(self.model.tableName())
                    if self.model.tableName()=='languages':
                        self.timer.singleShot(200, self.reselect)
                        self.timer.singleShot(400, self.addTable)
                    elif self.model.tableName()!='languages':
                        if self.column == self.codeModel.columnCount():
                            self.addData()

        ''' 额外知识点
        if event.type() == QEvent.MouseButtonPress:
            mouseEvent = QMouseEvent(event)
            if mouseEvent.buttons() == Qt.RightButton:
                print('click')            
        '''
        
        return QMainWindow.eventFilter(self, obj, event)
    def enterEvent(self, e):
        '''自定义标题栏需要重置光标。'''
        self.setCursor(Qt.ArrowCursor)
    def initializeModel(self, model, tablename):
        '''重关联。'''
        model.setTable(tablename)
        model.setEditStrategy(QSqlTableModel.OnFieldChange)
        model.select()
    def createView(self, title, model):
        '''创建TableView视图'''
        view =  QTableView()
        view.setModel(model)
        view.setWindowTitle(title)
        view.horizontalHeader().setSectionResizeMode(3)#列宽设置
        view.verticalHeader().setSectionResizeMode(3)#行高设置
        view.horizontalHeader().setStretchLastSection(True); #充满列宽
        view.verticalHeader().setVisible(False)#隐藏行标题
        view.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)#标题左对齐
        return view  
   
    def codeMenu(self, i):
        '''代码视图的右键菜单'''
        
        popMenu =QMenu()
#        index=self.codeView.indexAt(i)
#        popMenu.addAction(u'插入行',self.deleteData)
        popMenu.addAction(u'增加字段',self.addField)
        popMenu.addAction(u'删除字段',self.deleteField)
        popMenu.exec_(QCursor.pos())#鼠标位置    def codeMenu(self, i):
    
    def helpMenu(self):       
        '''帮助按钮的右键菜单'''
        
        popMenu =QMenu()
#        popMenu.addAction(u'查询帮助文档',self.deleteData)
        popMenu.addAction(u'关于',self.showAboutMe)
        popMenu.exec_(QCursor.pos())#鼠标位置
        #currentColumn 当前列；columnCount()总列数；currentIndex().row()在父节点下的行号
    
    def addField(self): 
        '''添加字段。''' 
        if self.oldTableName != 'languages':
            self.fieldEdit=Edit_Dialog(self)
            self.fieldEdit.setWindowModality(2)#设置为应用程序模态；0:非模态，1:非模态
            self.fieldEdit.show()
            if self.fieldEdit.exec() == QDialog.Accepted:
                try:
                    if self.fieldEdit.lineEdit_2.text() != '':
                        self.query.exec("ALTER TABLE %s ADD COLUMN %s text DEFAULT (%s);"%(self.oldTableName,
                                                                            self.fieldEdit.lineEdit.text(),
                                                                            self.fieldEdit.lineEdit_2.text()))   

                    else:
                        self.query.exec("ALTER TABLE %s ADD COLUMN %s;"%(self.oldTableName, self.fieldEdit.lineEdit.text()))
                except:
                    
                    QMessageBox.critical(self,"表名错误","名字不合法，请修改!") 
        else:
            QMessageBox.critical(self,"非法操作","该表不允许添加字段!") 
        self.initializeModel(self.codeModel, self.oldTableName)#!!!!!!!!!!!!!!!!
    def deleteField(self):
        '''如果表不是总表，则删除字段；否则提示错误。'''
        if self.oldTableName != 'languages':
            record = self.db.record(self.oldTableName)
            record.remove(self.column)
            t=[record.fieldName(i) for i in range(1, record.count())]#获取字段名
            t='id INTEGER PRIMARY KEY UNIQUE,'+','.join(t)#串接
            text='''
                PRAGMA foreign_keys = 0;
                DROP TABLE IF EXISTS sqlitestudio_temp_table;
                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM {tableName};
                DROP TABLE {tableName};
                CREATE TABLE {tableName} ({filed});
                INSERT INTO {tableName} ( {filed} ) SELECT {filed} FROM sqlitestudio_temp_table;
                DROP TABLE sqlitestudio_temp_table;
                PRAGMA foreign_keys = 1;
                '''.format(tableName=self.oldTableName, filed=t)    
            
            conn = sqlite3.connect('./db/database.db')
            c = conn.cursor()
            try:
                c.executescript(text)  
                conn.commit()
            except e:
                print(e) 
            conn.close() 
                  
        else:
            QMessageBox.critical(self,"非法操作","该表不允许删除字段!") 
        
        self.initializeModel(self.codeModel, self.oldTableName)
        
    def byField(self):   
        '''排序功能，待开发。'''    
        pass
    
    def findrow(self, i):
        self.row= i.row()
        self.column=i.column()
        self.model=self.sender().model()
        if self.model==self.sort_Model:
            self.getOldTableName()
            
            pixmapList = self.recordList()
            pixmapColumn=[i for i,x in enumerate(pixmapList) if x.find('图片')!=-1] 
            try:
                self.codeModel.setPixColumn(pixmapColumn)
            except:
                pass
            tablename=self.sort_Model.data(self.sort_Model.index(self.row,0))
            self.initializeModel(self.codeModel, tablename)# 切换表！！！！！！！！！
            if self.stackedWidget.currentIndex()==1:
                self.queryRecord()
#        elif self.model==self.codeModel:                
#            if self.stackedWidget.currentIndex()==0:
#                if self.codeModel.rowCount()==0:
#                    self.query.exec("INSERT INTO %s values('inputI', 'inputII')"%(tablename))
    def addData(self, ):

        if self.model.objectName()=='codeModel':
            for i in range(self.model.rowCount()-1, self.row, -1):
                index=self.model.index(i, 0)                
                self.model.setData(index,self.model.data(index)+1)    
                
            self.model.insertRows(self.row+1, 1)
            
            index0=self.model.index(self.row, 0)
            index10=self.model.index(self.row+1, 0)            
            index11=self.model.index(self.row+1, 1)

            self.model.setData(index10,self.model.data(index0)+1)
            self.model.setData(index11,'')
            
        elif self.model.objectName()=='sort_Model':
            self.model.insertRows(self.row+1, 1)
            # ↑ 插入的时候默认在第一行
            index=self.model.index(0, 1)
            index2=self.model.index(0, 2)

            self.model.setData(index2, 1)#设置为可见
            defaultValue=int(self.model.data(self.model.index(self.row+1, 1))) + 10
            
            self.model.setData(index, defaultValue)#设置排序序号

    def addTable(self):
        
        if self.model==self.sort_Model:
            tablename=self.model.data(self.model.index(self.model.rowCount()-1, 0))
            print(tablename)
        elif self.model==self.codeModel:
            tablename=self.model.data(self.model.index(self.row,  0))
        
#        self.query.exec("CREATE VIRTUAL TABLE %s USING fts5(Operation , Code )"%(tablename))

        self.query.exec("CREATE TABLE %s (id  INTEGER PRIMARY KEY UNIQUE, Operation , Code )"%(tablename))#建表
        
        self.query.exec("INSERT INTO %s values('1','inputI', 'inputII')"%(tablename)) #建第一条记录
        
        if tablename not in self.db.tables():
            conn = sqlite3.connect('./db/database.db')
            c = conn.cursor()
            try:
                text='''CREATE TABLE %s
                   (
                   id    INTEGER PRIMARY KEY UNIQUE,               
                   Operation      ,
                   Code           ,
                   );'''%(str(tablename))
                c.execute(text)
                conn.commit()
            except:
                QMessageBox.critical(self,"表名错误","名字不合法，请修改后按回车键!") 
            conn.close()            
        self.reselect()
    
    def deleteData(self):
        '''如果当前是第0页：<br>
            codeModel：<br>
                如果是总表：<br>
                如果不是总表：<br>
            sort_Model：隐藏表，但未删除；若想删除则需要在codeModel的languages表中删除。<br>
        '''
        if self.stackedWidget.currentIndex() !=1:
            if self.model == self.codeModel :
                if self.codeModel.tableName()=='languages' :
                    deleteTableName=self.codeModel.data(self.model.index(self.row,0))#!
                    if deleteTableName != 'languages':
                        self.codeModel.removeRows(self.row, 1)#删除数据 
                        self.query.exec('DROP TABLE %s'%(deleteTableName))
                else:
                    if self.row!=0:
                        self.codeModel.removeRows(self.row, 1)#删除数据 
                        self.reselect()                        
                        for i in range(self.row, self.model.rowCount()):
                            index=self.model.index(i, 0)                
                            self.model.setData(index,self.model.data(index)-1)                           

                        
            elif self.model == self.sort_Model:
               if self.oldTableName != 'languages' and self.model.data(self.model.index(self.row,0))!= 'languages' :
                   self.model.setData(self.sort_Model.index(self.row, 2), 0)
        
        self.reselect()

    
    def getOldTableName(self):
        '''获取旧表名。'''
        self.oldTableName = self.sort_Model.data(self.sort_Model.index(self.row,0))#!

    def getNewTableName(self):
        '''修改表名。'''
        self.newTableName = self.sort_Model.data(self.sort_Model.index(self.row,0))
        #ALTER TABLE 旧表名 RENAME TO 新表名
        self.query.exec('ALTER TABLE %s RENAME TO %s'%(self.oldTableName, self.newTableName))        
  
    def queryRecord(self):
        '''实现模糊查询。'''
        self.stackedWidget.setCurrentIndex(1)  
        if self.stackLabel.text()!='当前为【查询】结果':
            self.stackLabel.setText('当前为【查询】结果')
            
        search = str('%'+self.search.text()+'%')
        
        t=self.recordList()
        t=(" LIKE '%s' or "%(search)).join(t)#串接
        t=t+" LIKE '%s' "%(search)
        queryText = "SELECT * FROM %s WHERE %s;"%(self.oldTableName, t )

#        queryText="SELECT * FROM %s WHERE %s MATCH '%s';"%(self.oldTableName, self.oldTableName ,self.search.text())#全文检索
    
        self.searchModel.setQuery(queryText)

    def fresh(self):
        '''返回记录表。'''
        self.stackedWidget.setCurrentIndex(0)
        self.stackLabel.setText('当前为记录表')
  
    def reselect(self):
        '''重关联。'''
        if self.codeModel.data(self.codeModel.index(self.codeModel.rowCount(), 0))!='':        
            try:
                self.model.select() 
                self.langModel.select()
                self.sort_Model.select()
    #            self.codeModel.select()
            except:
                self.langModel.select()
            
    
    def getSetting(self):
        '''读取ini配置。'''        
        if(self.setting.contains("SelectTable/selectRow")):   #此节点是否存在该数据
            self.row=int(self.setting.value("SelectTable/selectRow"))
#        if(self.setting.contains("Position/x")):   #此节点是否存在该数据
#            x=int(self.setting.value("Position/x"))
#            y=int(self.setting.value("Position/y"))
#            w=int(self.setting.value("Position/w"))
#            h=int(self.setting.value("Position/h"))
#            self.resize(w, h)

#            if x<=0:
#                self.move(-543, y)
#            elif x>=823 :
#                self.move(1356, y)
#            elif y<=-0:
#                self.move(x, -299)
#            elif 0<x<823 and y>0 :
#                self.move(x, y)

        if(self.setting.contains("SetTop/isCheck")):   #此节点是否存在该数据
            self.check=int(self.setting.value("SetTop/isCheck"))    
            self.checkbox.setChecked(self.check)
        self.langView.selectRow(self.row)
        self.oldTableName=self.sort_Model.data(self.sort_Model.index(self.row,0))
        self.initializeModel(self.codeModel, self.oldTableName)#!!!!!!!!!!!!!!!!              
        
    def closeEvent(self, event):
        self.setting.setValue("SelectTable/selectRow",str(self.row));#设置key和value，也就是参数和值  
#        self.setting.setValue("Position/x",str(self.frame-self.width()));#设置x坐标
#        self.setting.setValue("Position/y",str(self.parent().y()));#设置设置y坐标
#        self.setting.setValue("Position/w",str(self.width()));#设置宽度
#        self.setting.setValue("Position/h",str(self.height()));#设置高度
        self.setting.setValue("SetTop/isCheck",str(self.check));#设置是否置顶

    def setTop(self):
        '''设置置顶状态。'''
        if self.checkbox.isChecked():
            self.check=1
        else:
            self.check=0
    
    def showAboutMe(self):
        self.AboutMe_Dialog = AboutMe_Dialog(self)
        self.AboutMe_Dialog.show()
    def recordList(self):
        '''获取表的所有字段，返回列表。'''        
        record = self.db.record(self.oldTableName)
        list=[record.fieldName(i) for i in range(record.count())]#获取字段名
        return list
    def showToolTip(self, index):
        '''放大显示图片。'''
        ima =str(index.data())
        if 'jpg' in ima.split('.') or 'png' in ima.split('.'):
            QToolTip.showText(QCursor.pos(),  "<img src='%s'>"%(ima));
#        else:
#            QToolTip.showText(QCursor.pos(),  ima);

def setTop(w, check):
    if check==1:
        w.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.Tool|Qt.FramelessWindowHint)
    elif check==0:
        w.setWindowFlags(Qt.Widget|Qt.FramelessWindowHint)
    if w.isVisible()==False:
        w.setVisible(True);
        
if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    # if you want to using this QSS, please pip install qdarkstyle.
    import qdarkstyle
    
#    app.setStyle(QStyleFactory.create("Fusion"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5()+
    "QToolTip {opacity: 500;}"+"QToolBar {border-top: 2px groove #696969; padding:0px 0px 0px 5px; }")
    
    def excepthook(type, value, trace):
        try:
            pass
        except:
            pass
        sys.__excepthook__(type, value, trace)
    sys.excepthook = excepthook

    framelessWindow = FramelessWindow();
    ui = MainWindow(framelessWindow)

    framelessWindow.setContent(ui)
    ui.checkbox.stateChanged.connect(lambda:setTop(framelessWindow , ui.check))
    framelessWindow.closeButton.clicked.connect(ui.close)
    
    framelessWindow.show()
    
#    ui = MainWindow()    
#    ui.show()
    
    sys.exit(app.exec_())
