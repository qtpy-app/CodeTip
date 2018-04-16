import os, traceback, platform, threading, subprocess
import subprocess
from subprocess import call



from PyQt5 import  QtGui, QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


import time
from aboutMeWidget import AboutMe_Dialog

class Git_Syn(QObject):
    
    '''
    cls:静态方法必须参数,无意义.<br>
    parent:父级窗口.<br>
    '''

    @classmethod
    def init(cls, parent, ):
        '''
        流程: <br>
        检测到存在.git,询问删除,确认删除,取消确认则弹窗请求重新配置;<br>
                  确认删除则删除。
                       询问删除,否定删除,则重新配置ini文件。
        检测到不存在，则开始创建配置。
        
        os.system 和 call 都是调用 终端操作 , 但是 前者会有黑窗口。
        '''
        systemTpye = platform.system()#判断操作系统类型
        if os.path.exists('.git'):
            msg=QMessageBox.warning(parent, '请确认', '检测到已存在仓库目录,重新配置是否删除.git文件夹？不删除只修改配置信息。',
                                QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
            if msg==QMessageBox.Yes:
                msg=QMessageBox.warning(parent, '请确认', '确认删除.git文件夹？', QMessageBox.Yes|QMessageBox.No)
                if msg==QMessageBox.Yes:#确认删除.git
                    if systemTpye =='Windows':

                        try:
#                            CREATE_NO_WINDOW = 0x08000000
#                            call('cmd rd/s/q .git', creationflags=CREATE_NO_WINDOW)#这里用这样会阻塞,能解决的请联系625781186@qq.com
                            os.system('rd/s/q .git')#但是这样有小黑窗。
                            Git_Syn.creatGit(parent, systemTpye)
                        except:
                            Git_Syn.creatMsg(parent)
                            QMessageBox.information(parent, '删除失败', '如果删除失败就是作者Bug, 请手动删除后重试。')
                    else:
                        try:
                            os.system('rm -rf .git')
                            Git_Syn.creatGit(parent, systemTpye)
                        except:
                            QMessageBox.information(parent, '删除失败', '如果删除失败就是作者Bug, 请手动删除。')

                elif msg==QMessageBox.No:#不删除
                    QMessageBox.information(parent, '请重新操作', '请重新点击配置远程仓库菜单。')

            elif msg==QMessageBox.No:
                remoteName=Git_Syn.R_W_setting()
                try:
                    subprocess.Popen('git remove %s'%remoteName, shell=True)
                    Git_Syn.creatGit(parent,systemTpye)
                except:
                    Git_Syn.creatGit(parent,systemTpye)
        else:#不存在.git,创建.git
            Git_Syn.creatGit(parent, systemTpye)

    @classmethod
    def gitPush(cls, parent):
        remoteName=Git_Syn.R_W_setting()

        try:
            subprocess.Popen("git add db", shell=True)
            subprocess.Popen('git commit -m "This is a db."', shell=True)
        except:
            errmsg = traceback.format_exc()
            try:
                if 'nothing added to' in errmsg:
                    pass
                else:Git_Syn.creatMsg(parent)
            except:
                pass
        try:
            push = PushThread(remoteName)
            return push
        except Exception :
            Git_Syn.creatMsg(parent)
    @classmethod
    def gitPull(cls, parent):
        remoteName=Git_Syn.R_W_setting()        

        try:
            pull = PullThread(remoteName)
            return pull
        except :
            try:
                if 'nothing added to' in errmsg:
                    pass
                else:Git_Syn.creatMsg(parent)
            except:
                pass            
    @classmethod            
    def push_pull(cls, parent, type):
        cls.textedit = AboutMe_Dialog(parent);
        
        cls.resultEdit=QPlainTextEdit()
        cls.textedit.verticalLayout.addWidget(cls.resultEdit)
        
        icon = QIcon()
        icon.addPixmap(QPixmap(":/ima/git.ico"), QIcon.Normal, QIcon.Off)
        cls.textedit.setWindowIcon(icon)
        cls.textedit.setWindowTitle("等待git结果")
        cls.textedit.setWindowModality(0)#设置为应用程序模态；0:非模态，1:非模态,2.应用程序模态
        cls.textedit.show()
        
        pushaction=Git_Syn.gitPush(parent)
        pullaction=Git_Syn.gitPull(parent)
        
        pushaction.SignalAppendText.connect(
            Git_Syn.onTextAppend, type=Qt.QueuedConnection)
        pullaction.SignalAppendText.connect(
            Git_Syn.onTextAppend, type=Qt.QueuedConnection)
        if type==7:#上传
            if not pullaction.isRunning():#not runing:
                pushaction.start()
            else:
                QMessageBox.information(parent, '注意！', '正在下载，请稍后重试。')
        elif type==8:#下载
            if not pushaction.isRunning(): #not runing:
                pullaction.start()
            else:
                QMessageBox.information(parent, '注意！', '正在上传，请稍后重试。')     
    
    def onTextAppend(text):
        print(text)
        Git_Syn.resultEdit.appendPlainText(text)
    
    def creatGit(parent,systemTpye):
        '''
        创建远程仓库。
        '''
        gitDialog=QInputDialog(parent)
        gitDialog.setWindowTitle('配置远程仓库')            
        gitDialog.setLabelText('远程仓库地址: ')
        gitDialog.setOkButtonText('&OK')
        gitDialog.setWhatsThis('配置远程仓库,实现同步功能。')

        icon = QIcon()
        icon.addPixmap(QPixmap(":/ima/git.ico"), QIcon.Normal, QIcon.Off)
        gitDialog.setWindowIcon(icon)

        if gitDialog.exec()==QDialog.Accepted:
            remoURLpath=gitDialog.textValue()#远程仓库地址
                
#                创建本地仓库的两种方法，第二种会出现一会儿cmd窗口
            if systemTpye=='Windows':
                CREATE_NO_WINDOW = 0x08000000
                try:
                    call('git init', creationflags=CREATE_NO_WINDOW)
                except:
                    QMessageBox.critical(parent, '错误', '请确认电脑已经安装了Git软件')
                    return     
            else:
                try:
                    os.system("git init")
                except:
                    QMessageBox.critical(parent, '错误', '请确认电脑已经安装了Git软件')
                    return

            try:
                os.popen("git add db")
                os.popen('git commit -m "This is a db."')
            except:
                Git_Syn.creatMsg(parent)
        
            gitDialog.setLabelText('远程仓库: ')
            gitDialog.setWindowIcon(icon)
            gitDialog.setTextValue('remoteDB')
            if gitDialog.exec()==QDialog.Accepted:
                
                remoteName=gitDialog.textValue() #远程仓库在本地名
                os.popen("git remote add %s %s"%(remoteName,remoURLpath))
                Git_Syn.R_W_setting(remote=remoteName, path=remoURLpath)
                
            else:
                return
        else:
            return
    def R_W_setting(**path_remote):
        '''
        读取和写入配置文件
        '''
        setting=QSettings('./db/setting.ini', QSettings.IniFormat)
        if path_remote=={}:
            if(setting.contains("GitRemote/remoteName")):   #是否否存在仓库名称
                remoteName=str(setting.value("GitRemote/remoteName"))
                return (remoteName)
        else:
            #不存在远程路径
            if 'remote' in path_remote:
                setting.setValue("GitRemote/remoteName",path_remote['remote']);#写本地仓库名
                
            if 'path' in path_remote:
                setting.setValue("GitRemote/path",path_remote['path']);#写本地仓库名
    def creatMsg(parent):
        '''
        信息弹窗提示。
        '''
        errmsg = traceback.format_exc()
        gitMsg=QMessageBox(parent)

        icon = QIcon()
        icon.addPixmap(QPixmap(":/ima/git.ico"), QIcon.Normal, QIcon.Off)
        gitMsg.setWindowIcon(icon)
        gitMsg.setIcon(QMessageBox.Critical)
        gitMsg.setWindowTitle("错误")	

        gitMsg.setText(errmsg)
        gitMsg.setDetailedText(errmsg)
        gitMsg.setStandardButtons(QMessageBox.Ok)
        gitMsg.exec_()	

class PushThread(QThread):
    SignalAppendText = pyqtSignal(str)
    def __init__(self, remoteName):
        super(PushThread, self).__init__()
        self.remoteName=remoteName

    def run(self):
        try:
            result = subprocess.Popen('git push -v --progress "%s" master:master'%self.remoteName, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        

            print("end2")            
            stdout = str(result.stdout.read(), encoding="gb2312")
            print(stdout, type(stdout))
            stderr = str(result.stderr.read(), encoding="gb2312")
            print(stderr, type(stderr))            
            print("end1")              
            self.SignalAppendText.emit(stdout+"\n"+"="*35+"\n")
            self.SignalAppendText.emit(stderr+"\n"+"-"*35+"\n")

#            if "* branch            master     -> FETCH_HEAD" in 
            print("end")
        except:
            print('error')
class PullThread(QThread):
    SignalAppendText = pyqtSignal(str)
    def __init__(self, remoteName):
        super(PullThread, self).__init__()
        self.remoteName=remoteName

    def run(self):
        try:
            result = subprocess.Popen("git pull --rebase %s master"%self.remoteName, shell=True)
            res = result.read()  
            for line in res.splitlines():  
                print(line)
                self.SignalAppendText.emit(line)
        except:
            errmsg = traceback.format_exc()
            if 'find remote ref master' in errmsg:
                pass
            else:
                QMessageBox.critical(QWidget(),'错误!', errmsg)
