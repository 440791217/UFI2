import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt5.QtGui import QFont
import serial
import serial.tools.list_ports
import serial
import serial.tools.list_ports
import glob
import os
import json
import constant


def get_ports():
    ports=[]
    # 获取所有可用串口的列表
    devices0 = serial.tools.list_ports.comports()
    devices1 = glob.glob('/dev/ttyCH*')
    if devices0:
        for dev in devices0:
            ports.append(dev.device)
            print('端口号：',ports)
    if devices1:
         for dev in devices1:
            ports.append(dev)
            print('端口号：',ports)
    return sorted(ports) 


class SerialConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("串口配置")

        # 设置对话框的初始大小
        self.setGeometry(200, 200, 400, 350)

        # 创建主垂直布局
        main_layout = QVBoxLayout()
        # 设置布局的边距和间距
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 设置字体
        font = QFont()
        font.setPointSize(12)

        # 端口号选择，使用水平布局
        port_layout = QHBoxLayout()
        port_label = QLabel("端口号:")
        port_label.setFont(font)
        self.port_combo = QComboBox()
        self.port_combo.setFont(font)
        # 模拟一些常见的串口端口号，实际使用中可以动态获取
        # ports = ["COM1", "COM2", "COM3", "COM4"]
        ports=get_ports()
        self.port_combo.addItems(ports)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_combo)
        main_layout.addLayout(port_layout)

        # 波特率选择，使用水平布局
        baud_layout = QHBoxLayout()
        baud_label = QLabel("波特率:")
        baud_label.setFont(font)
        self.baud_combo = QComboBox()
        self.baud_combo.setFont(font)
        baud_rates = ["9600", "115200", "230400"]
        self.baud_combo.addItems(baud_rates)
        baud_layout.addWidget(baud_label)
        baud_layout.addWidget(self.baud_combo)
        main_layout.addLayout(baud_layout)

        # 数据位选择，使用水平布局
        data_bit_layout = QHBoxLayout()
        data_bit_label = QLabel("数据位:")
        data_bit_label.setFont(font)
        self.data_bit_combo = QComboBox()
        self.data_bit_combo.setFont(font)
        data_bits = ["5", "6", "7", "8"]
        self.data_bit_combo.addItems(data_bits)
        data_bit_layout.addWidget(data_bit_label)
        data_bit_layout.addWidget(self.data_bit_combo)
        main_layout.addLayout(data_bit_layout)

        # 校验位选择，使用水平布局
        parity_layout = QHBoxLayout()
        parity_label = QLabel("校验位:")
        parity_label.setFont(font)
        self.parity_combo = QComboBox()
        self.parity_combo.setFont(font)
        parities = ["Odd", "Even"]
        self.parity_combo.addItems(parities)
        parity_layout.addWidget(parity_label)
        parity_layout.addWidget(self.parity_combo)
        main_layout.addLayout(parity_layout)

        # 停止位选择，使用水平布局
        stop_bit_layout = QHBoxLayout()
        stop_bit_label = QLabel("停止位:")
        stop_bit_label.setFont(font)
        self.stop_bit_combo = QComboBox()
        self.stop_bit_combo.setFont(font)
        stop_bits = ["1", "1.5", "2"]
        self.stop_bit_combo.addItems(stop_bits)
        stop_bit_layout.addWidget(stop_bit_label)
        stop_bit_layout.addWidget(self.stop_bit_combo)
        main_layout.addLayout(stop_bit_layout)

        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.setFont(font)
        ok_button.clicked.connect(self.accept)
        main_layout.addWidget(ok_button)

        self.setLayout(main_layout)
        #
        if os.path.exists(constant.uart_json):
            with open(constant.uart_json,'r') as rf:
                self.config=json.load(rf)
        else:
            self.config={
                "port": "/dev/ttyCH343USB0",
                "br": "115200",
                "pb": "Even",
                "sb": "1",
                "db": "8"
            }
        self.port_combo.setCurrentText(self.config['port'])
        self.baud_combo.setCurrentText(self.config['br'])
        self.data_bit_combo.setCurrentText(self.config['db'])
        self.parity_combo.setCurrentText(self.config['pb'])
        self.stop_bit_combo.setCurrentText(self.config['sb'])

    def get_config(self):
        port = self.port_combo.currentText()
        baud_rate = self.baud_combo.currentText()
        data_bit = self.data_bit_combo.currentText()
        parity = self.parity_combo.currentText()
        stop_bit = self.stop_bit_combo.currentText()
        self.config={
            "port": port,
            "br": baud_rate,
            "pb": parity,
            "sb": stop_bit,
            "db": data_bit
        }
        with open(constant.uart_json,'w') as wf:
            json.dump(self.config,wf,indent=2)
        return port, baud_rate, data_bit, parity, stop_bit
    


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
        config_action.triggered.connect(self.show_serial_config_dialog)
        serial_menu.addAction(config_action)
        menubar.addMenu(serial_menu)

    def show_serial_config_dialog(self):
        dialog = SerialConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            port, baud_rate, data_bit, parity, stop_bit = dialog.get_config()
            print(f"配置的串口参数 - 端口号: {port}, 波特率: {baud_rate}, 数据位: {data_bit}, 校验位: {parity}, 停止位: {stop_bit}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())