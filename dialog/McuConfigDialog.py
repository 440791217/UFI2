import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt5.QtGui import QFont
import constant
import json


class McuConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("平台配置")

        # 设置对话框的初始大小
        self.setGeometry(200, 200, 400, 500)

        # 创建主垂直布局
        main_layout = QVBoxLayout()
        # 设置布局的边距和间距
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 设置字体
        font = QFont()
        font.setPointSize(12)

        # 架构选择，使用水平布局
        arch_layout = QHBoxLayout()
        arch_label = QLabel("架构:")
        arch_label.setFont(font)
        self.arch_combo = QComboBox()
        self.arch_combo.setFont(font)
        # 模拟一些常见的架构
        self.architectures = ["Cortex-M4", "Cortex-R4"]
        self.arch_combo.addItems(self.architectures)
        self.arch_combo.currentIndexChanged.connect(self.update_core_options)
        arch_layout.addWidget(arch_label)
        arch_layout.addWidget(self.arch_combo)
        main_layout.addLayout(arch_layout)

        # 处理器选择，使用水平布局
        core_layout = QHBoxLayout()
        core_label = QLabel("处理器:")
        core_label.setFont(font)
        self.core_combo = QComboBox()
        self.core_combo.setFont(font)
        # 不同架构对应的处理器列表
        self.core_options = {
            "Cortex-M4": ["STM32F407"],
            "Cortex-R4": ["TMS570LS3137"]
        }
        self.update_core_options()
        core_layout.addWidget(core_label)
        core_layout.addWidget(self.core_combo)
        main_layout.addLayout(core_layout)

        # 调试器选择，使用水平布局
        debugger_layout = QHBoxLayout()
        debugger_label = QLabel("调试器:")
        debugger_label.setFont(font)
        self.debugger_combo = QComboBox()
        self.debugger_combo.setFont(font)
        self.debuggers = ["J-Link"]
        self.debugger_combo.addItems(self.debuggers)
        debugger_layout.addWidget(debugger_label)
        debugger_layout.addWidget(self.debugger_combo)
        main_layout.addLayout(debugger_layout)

        # 接口选择，使用水平布局
        interface_layout = QHBoxLayout()
        interface_label = QLabel("接口:")
        interface_label.setFont(font)
        self.interface_combo = QComboBox()
        self.interface_combo.setFont(font)
        self.interfaces = ["SWD", "JTAG"]
        self.interface_combo.addItems(self.interfaces)
        interface_layout.addWidget(interface_label)
        interface_layout.addWidget(self.interface_combo)
        main_layout.addLayout(interface_layout)

        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.setFont(font)
        ok_button.clicked.connect(self.accept)
        main_layout.addWidget(ok_button)

        self.setLayout(main_layout)

        # 读取文件并设置默认选项
        self.set_default_options()

    def update_core_options(self):
        selected_arch = self.arch_combo.currentText()
        self.core_combo.clear()
        self.core_combo.addItems(self.core_options.get(selected_arch, []))

    def get_config(self):
        arch = self.arch_combo.currentText()
        core = self.core_combo.currentText()
        debugger = self.debugger_combo.currentText()
        interface = self.interface_combo.currentText()
        data = {
            'arch': arch,
            'core': core,
            'debugger': debugger,
            'interface': interface
        }
        with open(constant.mcu_json, 'w') as wf:
            json.dump(data, wf, indent=2)
            print('111', constant.mcu_json)
        return arch, core, debugger, interface

    def set_default_options(self):
        try:
            with open(constant.mcu_json, 'r') as rf:
                data = json.load(rf)
                arch = data.get('arch', '')
                core = data.get('core', '')
                debugger = data.get('debugger', '')
                interface = data.get('interface', '')

                arch_index = self.architectures.index(arch) if arch in self.architectures else 0
                self.arch_combo.setCurrentIndex(arch_index)
                self.update_core_options()

                core_index = self.core_combo.findText(core) if core in self.core_options.get(arch, []) else 0
                self.core_combo.setCurrentIndex(core_index)

                debugger_index = self.debuggers.index(debugger) if debugger in self.debuggers else 0
                self.debugger_combo.setCurrentIndex(debugger_index)

                interface_index = self.interfaces.index(interface) if interface in self.interfaces else 0
                self.interface_combo.setCurrentIndex(interface_index)
        except FileNotFoundError:
            print("配置文件未找到，使用默认选项。")
        except ValueError:
            print("配置文件内容格式错误，使用默认选项。")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("串口配置菜单示例")
        self.setGeometry(100, 100, 600, 400)

        # 创建菜单栏
        menubar = self.menuBar()

        # 创建串口菜单
        serial_menu = QMenu("串口配置", self)
        config_action = QAction("配置串口", self)
        config_action.triggered.connect(self.show_mcu_config_dialog)
        serial_menu.addAction(config_action)
        menubar.addMenu(serial_menu)

    def show_mcu_config_dialog(self):
        dialog = McuConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            arch, core, debugger, interface = dialog.get_config()
            print(f"配置的参数 - 架构: {arch}, 处理器: {core}, 调试器: {debugger}, 接口: {interface}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    