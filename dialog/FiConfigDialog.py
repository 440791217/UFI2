import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QDialog, QVBoxLayout, \
    QHBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QFileDialog,QMessageBox
from PyQt5.QtGui import QFont, QRegExpValidator
from PyQt5.QtCore import QRegExp
import json
import os
import constant
import myparser
import random


class FiConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("故障注入配置")

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

        # 模式选择，使用水平布局
        mode_layout = QHBoxLayout()
        mode_label = QLabel("模式:")
        mode_label.setFont(font)
        self.mode_combo = QComboBox()
        self.mode_combo.setFont(font)
        # 模拟一些常见的串口端口号，实际使用中可以动态获取
        self.ports = ["RF", 'IOV', 'IOA', 'MEM']
        self.mode_combo.addItems(self.ports)
        # 设置模式选择框的长度
        self.mode_combo.setFixedWidth(100)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        main_layout.addLayout(mode_layout)

        # 翻转类型选择，使用水平布局
        bfm_layout = QHBoxLayout()
        bfm_label = QLabel("翻转类型:")
        bfm_label.setFont(font)
        self.bfm_combo = QComboBox()
        self.bfm_combo.setFont(font)
        self.bfm_options = ["1"]
        self.bfm_combo.addItems(self.bfm_options)
        # 设置输入框长度
        self.bfm_combo.setFixedWidth(100)
        bfm_layout.addWidget(bfm_label)
        bfm_layout.addWidget(self.bfm_combo)
        main_layout.addLayout(bfm_layout)

        # 故障数量选择，使用水平布局
        injnum_layout = QHBoxLayout()
        injnum_label = QLabel("故障数量:")
        injnum_label.setFont(font)
        self.injnum_input = QLineEdit()
        self.injnum_input.setFont(font)
        # 为 MEM 模式设置验证器，允许输入 0 到 0.1 之间的浮点数
        float_validator = QRegExpValidator(QRegExp(r'^0(\.\d+)?$|^0\.1$'))
        self.injnum_input.setValidator(float_validator)
        self.injnum_input.setReadOnly(True)  # 初始时只读
        self.injnum_input.setText("1")
        # 设置输入框长度
        self.injnum_input.setFixedWidth(100)
        injnum_layout.addWidget(injnum_label)
        injnum_layout.addWidget(self.injnum_input)
        main_layout.addLayout(injnum_layout)

        # 执行次数选择，使用水平布局
        exenum_layout = QHBoxLayout()
        exenum_label = QLabel("执行次数:")
        exenum_label.setFont(font)
        self.exenum_combo = QComboBox()
        self.exenum_combo.setFont(font)
        self.exenum_options = {
            "RF": ["500", "1000", "1500", "2000"],
            "IOV": ["500", "1000", "1500", "2000"],
            "IOA": ["500", "1000", "1500", "2000"],
            "MEM": ["500", "1000", "1500", "2000"],
        }
        self.exenum_combo.addItems(self.exenum_options["RF"])
        # 设置输入框长度
        self.exenum_combo.setFixedWidth(100)
        exenum_layout.addWidget(exenum_label)
        exenum_layout.addWidget(self.exenum_combo)
        main_layout.addLayout(exenum_layout)

        # 内存地址输入，使用水平布局
        mem_addr_layout = QHBoxLayout()
        mem_addr_label = QLabel("内存地址（十六进制）:")
        mem_addr_label.setFont(font)
        self.mem_addr_input = QLineEdit()
        self.mem_addr_input.setFont(font)
        hex_validator = QRegExpValidator(QRegExp("[0-9A-Fa-f]+"))
        self.mem_addr_input.setValidator(hex_validator)
        # 设置输入框长度
        self.mem_addr_input.setFixedWidth(100)
        mem_addr_layout.addWidget(mem_addr_label)
        mem_addr_layout.addWidget(self.mem_addr_input)
        main_layout.addLayout(mem_addr_layout)

        # 空间大小输入，使用水平布局
        space_size_layout = QHBoxLayout()
        space_size_label = QLabel("空间大小（十六进制）:")
        space_size_label.setFont(font)
        self.space_size_input = QLineEdit()
        self.space_size_input.setFont(font)
        self.space_size_input.setValidator(hex_validator)
        # 设置输入框长度
        self.space_size_input.setFixedWidth(100)
        space_size_layout.addWidget(space_size_label)
        space_size_layout.addWidget(self.space_size_input)
        main_layout.addLayout(space_size_layout)

        # 可执行文件地址选择，使用水平布局
        executable_layout = QHBoxLayout()
        executable_label = QLabel("可执行文件地址:")
        executable_label.setFont(font)
        self.executable_input = QLineEdit()
        self.executable_input.setFont(font)
        self.executable_input.setReadOnly(True)
        self.executable_input.setFixedWidth(200)
        select_button = QPushButton("选择文件")
        select_button.setFont(font)
        select_button.clicked.connect(self.select_executable_file)
        executable_layout.addWidget(executable_label)
        executable_layout.addWidget(self.executable_input)
        executable_layout.addWidget(select_button)
        main_layout.addLayout(executable_layout)

        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.setFont(font)
        ok_button.clicked.connect(self.accept)
        main_layout.addWidget(ok_button)

        self.setLayout(main_layout)

        # 连接模式选择框的信号
        self.mode_combo.currentIndexChanged.connect(self.update_options)

        inj_json = constant.inj_json
        if os.path.exists(inj_json):
            with open(inj_json, 'r') as rf:
                self.config = json.load(rf)
        else:
            self.config = {
                "app": '',
                "mode": "RF",
                "bfm": "1",
                "injnum": "1",
                "exenum": "1000",
                "mem_addr": "8001600",
                "space_size": "3EA00",
                "executable": ""
            }
        #
        self.mode_combo.setCurrentText(self.config['mode'])
        self.bfm_combo.setCurrentText(self.config['bfm'])
        self.injnum_input.setText(self.config['injnum'])
        self.exenum_combo.setCurrentText(self.config['exenum'])
        self.mem_addr_input.setText(self.config['mem_addr'])
        self.space_size_input.setText(self.config['space_size'])
        self.executable_input.setText(self.config['executable'])

    def update_options(self):
        selected_mode = self.mode_combo.currentText()
        self.exenum_combo.clear()
        self.exenum_combo.addItems(self.exenum_options[selected_mode])

        if selected_mode in ["RF", "IOV", "IOA"]:
            self.injnum_input.setReadOnly(True)
            self.injnum_input.setText("1")
        elif selected_mode == "MEM":
            self.injnum_input.setReadOnly(False)
            if not self.injnum_input.hasAcceptableInput():
                self.injnum_input.setText("0.00001")

    def select_executable_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择可执行文件", "", "可执行文件 (*.out *.bin *.hex *.elf);;所有文件 (*.*)")
        if file_path:
            self.executable_input.setText(file_path)

    def get_config(self):
        mode = self.mode_combo.currentText()
        bfm = self.bfm_combo.currentText()
        injnum = self.injnum_input.text()
        exenum = self.exenum_combo.currentText()
        mem_addr = self.mem_addr_input.text()
        space_size = self.space_size_input.text()
        executable = self.executable_input.text()
        self.config = {
            "app": '',
            "mode": mode,
            "bfm": bfm,
            "injnum": injnum,
            "exenum": exenum,
            "mem_addr": mem_addr,
            "space_size": space_size,
            "executable": executable
        }
        if not os.path.exists(executable):
            QMessageBox.information(self, '提示信息', '没有设置或找到可执行文件!', QMessageBox.Ok)
            return
        else:
            myparser.main(fp1=executable,fp2=constant.inst_txt,fp3=constant.inst_json)
        inj_json = constant.inj_json
        with open(inj_json, 'w') as wf:
            json.dump(self.config, wf, indent=2)
        self.gen_faults()

        return mode, bfm, injnum, exenum, mem_addr, space_size, executable

    def gen_faults(self):
        data=self.read_inj_config()
        app=data['app']
        mode=data['mode']
        bfm=int(data['bfm'])
        ###
        if mode=='MEM':
            num=float(data['injnum'])
        else:
            num=int(data['injnum'])
        ####
        times=int(data['exenum'])
        reg_collection = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9','r10' ,'r11', 'r12', 'sp', 'lr', 'pc']
        reg_width=32
        faults=[]
        for i in range(int(times)):
            before_tm = random.random() * 1+1
            fault = {
                'app':app,
                'mode':mode,
                'id': i,
                'num':num,
                'regs': [],
                'mems': [],
                'before_tm': before_tm,
                'flips': [],
                'injected': False
            }
            if mode=='RF':
                fault=self.gen_rf_faults(reg_collection=reg_collection,reg_width=reg_width,bfm=bfm,fault=fault)
            elif mode=='MEM':
                fault=self.gen_mem_faults(fault=fault)
            elif mode=='IOV' or mode=='IOA':
                fault=self.gen_inst_faults(reg_width=reg_width,bfm=bfm,fault=fault)
            faults.append(fault)
        with open(constant.faults_json,'w') as wf:
            json.dump(faults,wf,indent=2)
        return faults


    def gen_rf_faults(self,reg_collection,reg_width,bfm,fault):
        random_regs = random.sample(reg_collection, 1)
        for reg in random_regs:
            flips = random.sample(range(reg_width), bfm)
            obj={
                'name':reg,
                'flips': flips,
                'before_value': -1,
                'after_value': -1,
            }
            fault['regs'].append(obj)
        return fault
    
    def gen_inst_faults(self,reg_width,bfm,fault):
        flips = random.sample(range(reg_width), bfm)
        obj={
            'flips': flips,
            'before_value': -1,
            'after_value': -1,
        }
        fault['regs'].append(obj)
        return fault
    
    def gen_mem_faults(self,fault,mem_width=8,bfm=1):
        with open(constant.inj_json,'r') as rf:
            data=json.load(rf)
        mem_addr='0x'+data['mem_addr']
        space_size='0x'+data['space_size']
        injnum=data['injnum']
        mem_addr=int(mem_addr,16)
        space_size=int(space_size,16)
        injnum=float(injnum)
        num=int(space_size*injnum)
        for i in range(num):
            flips = random.sample(range(mem_width), bfm)
            addr=mem_addr+random.randint(0,space_size)
            obj={
                'id':i,
                'name':hex(addr),
                'flips': flips,
                'before_value': -1,
                'after_value': -1,
            }
            fault['mems'].append(obj)
        return fault

    
    def read_inj_config(self):
        with open(constant.inj_json,'r') as rf:
            data=json.load(rf)
        return data

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
        config_action.triggered.connect(self.show_fi_config_dialog)
        serial_menu.addAction(config_action)
        menubar.addMenu(serial_menu)

    def show_fi_config_dialog(self):
        dialog = FiConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            mode, bfm, injnum, exenum, mem_addr, space_size, executable = dialog.get_config()
            print(f"配置的串口参数 - 端口号: {mode}, 波特率: {bfm}, 故障数量：{injnum}, 执行次数：{exenum}, 内存地址：{mem_addr}, 空间大小：{space_size}, 可执行文件地址：{executable}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    