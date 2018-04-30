# CodeTip
这是一个在QSqltableModel+tableview上显示图片的例子，
并且带有贴边隐藏和自定义标题栏样式。

使用前请 pip installer qdarkstyle

![Alt text](https://github.com/625781186/codetip/raw/master/ima/gitima.jpg)

## How to package it?
- 如果你想用pyinstaller打包这个项目，成功打包之后需要复制ui文件夹，db文件夹到./dist/MainWindow目录下。    
( If you want to use pyinstaller to package this program, after successful packaging, you need to copy the ui folder and the db folder to the./dist/MainWindow directory. )
## How to use it?
- 在左侧按Ctrl+B会添加一个单元，写入数据后按Enter会创建数据表 (注意不能是数字开头或带有其他符号例如5C，C++之类的)；
    - 更改序号可以更改项目的排序
    - 可见设置为0之后可以去languages表中设置为1，都是写完之后按回车才刷新结果；
- 在左侧数据表中按Ctrl+D并不会真正删除数据表，只是设置为不可见，想要真正删除表，请选择languages项目，到里面去删除；
- 按Ctrl+F搜索框会获得鼠标焦点，可以进行模糊搜索；搜索之后按F5返回原先的列表；
- 如果要输入多行文字，请在单元格编辑状态下按Alt+Enter;
- 如果粘贴板中有图片，在单元格编辑状态下按Ctrl+V 可以把图片路径写入数据库，并在视图中显示略缩图，鼠标进入略缩图后ToolTip会显示出图片；
    - 图片实际保存在./db/ima目录下，如果删除掉表格中的图片路径，实际不会删除图片，鼠标右键？？？按钮清理图片才会真正删除；
- 可以远程添加github仓库作为远程同步目录，当然你需要在你的电脑上先安装git软件，这个功能是可用的，但是没有经过严谨的测试，存在未知bug；
### 下一步要做的：
    - 添加置顶win下其他窗体的功能；


