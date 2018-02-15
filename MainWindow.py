# -*- coding: utf-8 -*-


from PyQt5 import  QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase , QSqlTableModel, QSqlQueryModel, QSqlQuery
from PyQt5.QtCore import Qt 

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
        
        self.pushBu=QPushButton()
        self.toolBar.addWidget(self.pushBu)
        self.pushBu.clicked.connect(self.se)
        #=============================== action & Singnal ================================#
        self.addaction.triggered.connect(self.addData)
        self.delaction.triggered.connect(self.deleteData)
        self.freshaction.triggered.connect(self.fresh)
        self.search.returnPressed.connect(self.queryRecord)
        
        self.pushBu.clicked.connect(self.se)
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
        self.verticalLayout.addWidget(self.codeView)       
#        #================================= Timer=====================================#
        self.timer=QTimer()
        #================================= search ===================================#
        self.seachModel=QSqlQueryModel()
#        self.initializeModel(self.seachModel, 'langue')
        self.seachModel.setHeaderData(0, Qt.Horizontal, "操作")
        self.seachModel.setHeaderData(1, Qt.Horizontal, "代码")        
        self.seachModel.setObjectName('seachModel')

        self.searchView=self.createView("Search_View", self.seachModel)
        self.verticalLayout_2.addWidget(self.searchView)
        #================================  query  ===================================#
        self.query = QSqlQuery()
        #================================  installEventFilter  ===================================#
        self.langView.installEventFilter(self) 
        self.codeView.installEventFilter(self) 
        #================================ initData ==================================#
        self.row=0
        self.oldTableName='' 
        self.newTableName=''     
        #================================ setting ==================================#
#        self.setTabOrder(self.langView, self.codeView);
        self.model=self.sort_Model
        self.setting=QSettings('./db/setting.ini', QSettings.IniFormat)
        self.writeSetting()
        
        self.se()
        
    def eventFilter(self, obj, event):  
        if event.type()==QEvent.KeyPress:    
            if event.key()==Qt.Key_Return or event.key()==Qt.Key_Tab:
                if obj == self.langView:
                    self.timer.singleShot(200, self.addTable)
                    tablename=self.sort_Model.data(self.sort_Model.index(self.row,0))
                    self.initializeModel(self.codeModel, tablename)#!!!!!!!!!!!!!!!!      
                    
                if obj == self.codeView:
                    if self.model.tableName()=='languages':
                        self.timer.singleShot(200, self.reselect)
                        self.timer.singleShot(400, self.addTable)
        return False                

    def initTbleName(self): #初始化 langModel 的表
        [self.query.exec("insert into languages(lang) values('%s')"%(i_tablename)) for i_tablename in self.db.tables()]
            
        self.langModel.select() 
        
    def initializeModel(self, model, tablename):
        model.setTable(tablename)
        
        model.select()

    def createView(self, title, model):
        view =  QTableView()
        view.setModel(model)
        view.setWindowTitle(title)
        view.horizontalHeader().setSectionResizeMode(3)#列宽设置
        view.horizontalHeader().setStretchLastSection(True); #充满列宽
        view.verticalHeader().setVisible(False)#隐藏行标题
        view.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)#标题左对齐
        return view        
    
    def findrow(self, i):
        self.row= i.row()
        self.model=self.sender().model()
        
        self.getOldTableName()
        
        if self.model==self.sort_Model:
            row=self.row
            tablename=self.sort_Model.data(self.sort_Model.index(row,0))
            self.initializeModel(self.codeModel, tablename)#!!!!!!!!!!!!!!!!
            
            if self.codeModel.rowCount()==0:
                self.query.exec("insert into %s values('inputI', 'inputII')"%(tablename))
            
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
        self.query.exec("create table %s(operation char not null, code char)"%(str(tablename)))
        print('222', tablename)
    def deleteData(self):
        if self.model == self.codeModel :
            if self.codeModel.tableName()=='languages' :
                deleteTableName=self.model.data(self.model.index(self.row,0))#!
                if deleteTableName != 'languages':
                    self.model.removeRows(self.row, 1)#删除数据 
                    self.query.exec('DROP TABLE %s'%(deleteTableName ))
            else:
                self.model.removeRows(self.row, 1)#删除数据 
        
        elif self.model == self.sort_Model:
           if self.oldTableName != 'languages':
               self.model.setData(self.sort_Model.index(self.row, 2), 0)
        self.codeModel.submitAll()
        
        self.reselect()
        
    def getOldTableName(self):
        self.oldTableName = self.sort_Model.data(self.sort_Model.index(self.row,0))#!
        print(
        'self.row:', self.row, '\n', 
        'self.oldname:', self.oldTableName, 
        )        
    
    def getNewTableName(self):
        self.newTableName = self.sort_Model.data(self.sort_Model.index(self.row,0))
        #ALTER TABLE 旧表名 RENAME TO 新表名
        self.query.exec('ALTER TABLE %s RENAME TO %s'%(self.oldTableName, self.newTableName))        
  
    def queryRecord(self):
#        self.stackedWidget.setCurrentIndex(1)
#        condition=self.search.text()
        self.langModel.setFilter(None)   
        self.langModel.select()  

    def fresh(self):
        self.stackedWidget.setCurrentIndex(0)  
  
    def reselect(self):
        try:
            self.model.select() 
            self.langModel.select()
            self.sort_Model.select()
        except:
            self.langModel.select()
            
    def writeSetting(self):            
        if(self.setting.contains("SelectTable/selectRow")):   #此节点是否存在该数据
            self.row=int(self.setting.value("SelectTable/selectRow"))
        else:
            self.setting.beginGroup(str("SelectTable"));#节点开始  
            self.setting.setValue("selectRow","0");#设置key和value，也就是参数和值  
            self.setting.endGroup();#节点结束  
            
    def closeEvent(self, event):
        self.setting.setValue("SelectTable/selectRow",str(self.row));#设置key和value，也就是参数和值  
        self.codeModel.submitAll()
        
    def se(self):
        self.langView.selectRow(self.row)
        tablename=self.sort_Model.data(self.sort_Model.index(self.row,0))
        self.initializeModel(self.codeModel, tablename)#!!!!!!!!!!!!!!!!
    

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
