from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QDialog,\
    QVBoxLayout, QLabel, QLineEdit, QPushButton,QMessageBox,QSplitter,QFileSystemModel,QTreeView,QTextEdit,QWidget,QHBoxLayout,\
    QGroupBox,QTabWidget,QFileDialog

class Console:
    def __init__(self,root) -> None:
        self.root=root
        pass

    def init_tab_widget(self):
        # 创建 QTabWidget
        self.tab_widget = QTabWidget()

        # 创建第一个标签页
        self.console_module1 = QTextEdit()
        self.console_module1.setReadOnly(True)
        self.tab_widget.addTab(self.console_module1, "系统窗口")

        # 创建第二个标签页
        self.console_module2 = QTextEdit()
        self.console_module2.setReadOnly(True)
        self.tab_widget.addTab(self.console_module2, "通信窗口")

        # 设置标签页小部件的固定高度
        self.tab_widget.setFixedHeight(200)

        # 将标签页小部件添加到主布局的底部
        self.root.main_layout.addWidget(self.tab_widget)
    
    def update_console1(self,data):
        self.console_module1.append(data)
        # 自动滚动到最新消息
        scrollbar = self.console_module1.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_console2(self,data):
        self.console_module2.append(data)
        # 自动滚动到最新消息
        scrollbar = self.console_module2.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())