from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QDialog,\
    QVBoxLayout, QLabel, QLineEdit, QPushButton,QMessageBox,QSplitter,QFileSystemModel,QTreeView,QTextEdit,QWidget,QHBoxLayout,\
    QGroupBox,QTabWidget,QFileDialog
import os
from dialog.SerialConfigDialog import SerialConfigDialog
from dialog.McuConfigDialog import McuConfigDialog


class Dialog:
    def __init__(self,root) -> None:
        self.root=root
        pass
    

    def show_about_dialog(self):
        # 创建关于对话框
                # <p>版权所有 &copy; 2025 江苏苏度电子科技有限公司</p>
        about_text = """
        <h1>单粒子注错软件</h1>
        <p>版本: 1.0</p>
        <p>版权所有 &copy; 2025 江苏理工学院 刘智</p>
        """
        QMessageBox.about(self.root, '关于', about_text)

    
    def show_serial_config_dialog(self):
        dialog = SerialConfigDialog(self.root)
        if dialog.exec_() == QDialog.Accepted:
            port, baud_rate, data_bit, parity, stop_bit = dialog.get_config()
            print(f"配置的串口参数 - 端口号: {port}, 波特率: {baud_rate}, 数据位: {data_bit}, 校验位: {parity}, 停止位: {stop_bit}")


    def show_mcu_config_dialog(self):
        dialog = McuConfigDialog(self.root)
        if dialog.exec_() == QDialog.Accepted:
            arch, core, debugger, interface = dialog.get_config()
            print(f"配置的参数 - 架构: {arch}, 处理器: {core}, 调试器: {debugger}, 接口: {interface}")

