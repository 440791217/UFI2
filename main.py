import json
import random
import sys
import os
from front.Ui_main import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QDialog, \
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSplitter, QFileSystemModel, QTreeView, QTextEdit, QWidget, QHBoxLayout, \
    QGroupBox, QTabWidget, QFileDialog
from explore import Explore
import constant
from mydialog import Dialog
from fi import FI
from console import Console
from dialog.AnalyzerConfigDiaglog import AnalyzerConfigDiaglog as Analyzer
import sys


class MyMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

    def init(self):
        # 获取可执行文件的绝对路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            executable_path = os.path.abspath(sys.executable)
        else:
            # 如果是直接运行的 Python 脚本
            executable_path = os.path.abspath(sys.argv[0])

        # 获取可执行文件所在的目录
        script_dir = os.path.dirname(executable_path)
        print("可执行文件所在目录:", script_dir)
        constant.init_config(root=script_dir)
        # 创建主布局和主控件
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        #
        self.dialog = Dialog(root=self)
        # #
        self.explore = Explore(root=self)
        self.explore.init_file_browser(rootpath=script_dir)
        #
        self.analyer = Analyzer(root=self, rootpath=script_dir)
        #
        self.fi = FI(root=self)
        #
        self.console = Console(root=self)
        self.console.init_tab_widget()
        #
        self.init_menu()

        # 设置窗口全屏显示
        # self.showFullScreen()
        self.setWindowTitle("单粒子注错软件")
        self.show()

    def init_menu(self):
        menuBar = self.menuBar()
        fileMenu = [
            # ['新建',self.explore.new_directory],
            # ['打开',self.explore.open_directory],
            # ['保存',self.test],
            ['退出', self.show_quit],
        ]
        # viewMenu=[
        #     ['故障注入',self.test],
        #     ['工作台',self.test],
        # ]
        projMenu = [
            ['串口配置', self.dialog.show_serial_config_dialog],
            ['平台配置', self.dialog.show_mcu_config_dialog],
        ]
        fiMenu = [
            ['配置', self.fi.show_fi_config_dialog],
            # ['启动开始', self.fi.show_last_inject],
            ['启动开始', self.fi.show_new_inject],
            ['继续上次', self.fi.show_last_inject],
            ['停止', self.fi.show_stop_inject],

        ]
        analMenu = [
            # ['配置',self.test],
            ['分析', self.analyer.show_directory_selection_panel],
            # ['停止',self.test],
        ]
        helpMenu = [
            ['关于', self.dialog.show_about_dialog]
        ]
        menuItems = [
            ['文件', fileMenu],
            # ['视图',viewMenu],
            ['工程', projMenu],
            ['故障注入', fiMenu],
            ['结果分析', analMenu],
            ['帮助', helpMenu]
        ]

        for menuItem in menuItems:
            menu = menuBar.addMenu(menuItem[0])
            menu.addSeparator()
            for item in menuItem[1]:
                action = QAction(item[0], menuBar)
                action.triggered.connect(item[1])
                if menuItem[0] == '故障注入':
                    if item[0] == '启动开始':
                        self.menu_launch = action
                    elif item[0] == '继续上次':
                        self.menu_go = action
                    elif item[0] == '停止':
                        self.menu_stop = action
                        self.menu_stop.setEnabled(False)
                # action.setEnabled(False)
                menu.addAction(action)

    def show_quit(self):
        reply = QMessageBox.question(self, '确认操作', '真的要退出吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit(0)
            return
        else:
            return

    def test(msg='111'):
        print('msg:111')


class my_mainwindow(object):
    def __init__(self):
        app = QApplication(sys.argv)
        #########################
        self.myMainWindow = MyMainWindow()
        #
        self.myui = Ui_MainWindow()
        self.myui.setupUi(self.myMainWindow)
        #
        self.myMainWindow.init()
        sys.exit(app.exec_())


if __name__ == "__main__":
    my_mainwindow()
    