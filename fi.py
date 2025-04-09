
import datetime
import json
import random
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QDialog,\
    QVBoxLayout, QLabel, QLineEdit, QPushButton,QMessageBox,QSplitter,QFileSystemModel,QTreeView,QTextEdit,QWidget,QHBoxLayout,\
    QGroupBox,QTabWidget,QFileDialog
from dialog.FiConfigDialog import FiConfigDialog
import os
import constant
from injector import GDBServer, Injector
from com import Uart
import shutil
import myparser

class FI:
    def __init__(self,root) -> None:
        self.root=root
        self.injector=None
        self.gdbserver=None
        self.com=None
        self.buffer1=None
        pass
    
    def show_fi_config_dialog(self):
        dialog = FiConfigDialog(self.root)
        if dialog.exec_() == QDialog.Accepted:
            mode, bfm, injnum, exenum, mem_addr, space_size, executable = dialog.get_config()
            print(f"配置的串口参数 - 端口号: {mode}, 波特率: {bfm}, 故障数量：{injnum}, 执行次数：{exenum}, 内存地址：{mem_addr}, 空间大小：{space_size}, 可执行文件地址：{executable}")
  
    def show_dialog_for_uart(self):
        QMessageBox.information(self, '提示信息', '串口没有打开。', QMessageBox.Ok)

    def show_new_inject(self):
        reply = QMessageBox.question(self.root, '确认操作', '要清除历史记录，重新开始吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            with open(constant.faults_json,'r') as rf:
                faults=json.load(rf)
            for fault in faults:
                fault['injected']=False
            with open(constant.faults_json,'w') as wf:
                json.dump(faults,wf,indent=2)
            config=self.read_inj_config()
            appPath=os.path.join('./out',config['mode'])
            if os.path.exists(appPath):
                shutil.rmtree(appPath)
            self.gen_faults()
            self.run_inject()
        else:
            return
        

    def show_last_inject(self):
        if not os.path.exists(constant.faults_json):
            QMessageBox.information(self.root, '提示信息', '没有找到历史记录，请点击重新开始!', QMessageBox.Ok)
            return
        else:
            self.run_inject()
            pass

    
    def show_stop_inject(self):
        reply = QMessageBox.question(self.root, '确认操作', '要停止当前的故障注入吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.injector:
                self.injector.running=False
                time.sleep(5)
                self.injector=None
            if self.gdbserver:
                self.gdbserver.close()
                self.gdbserver=None
            if self.com:
                self.com.close()
                self.com=None   
            self.freeze_ui(status=False)         
            return
        else:
            return        


    def freeze_ui(self,status=True):
        self.root.menu_launch.setEnabled(not status)
        self.root.menu_go.setEnabled(not status)
        self.root.menu_stop.setEnabled(status)
        pass

    def run_inject(self):
        #
        self.gdbserver=GDBServer()
        self.gdbserver.data_signal.connect(self.on_receive_gdbserver)
        self.gdbserver.start()
        #
        self.com=Uart()
        config=self.read_uart_config()
        port=config['port']
        self.com.config(port=port)
        self.com.open()
        self.com.data_signal.connect(self.on_receive_com)
        #
        self.injector=Injector()
        self.injector.set_elf_bin(' ')
        self.injector.set_gdb_bin('arm-none-eabi-gdb')
        self.injector.faults_json_path=constant.faults_json
        self.injector.data_signal.connect(self.on_receive_gdb)
        self.injector.running=True
        self.injector.start()
        #
        self.freeze_ui(status=True)
        #
        pass

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

    def gen_faults(self):
        return
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

    def read_faults(self):
        with open(constant.faults_json,'r') as rf:
            faults=json.load(rf)           
        return faults

    def read_uart_config(self):
        with open(constant.uart_json,'r') as rf:
            config=json.load(rf)
        return config
    
    def read_inj_config(self):
        with open(constant.inj_json,'r') as rf:
            data=json.load(rf)
        return data

    def on_receive_gdbserver(self,data):
        type=data['type']
        msg=data['msg']
        code=data['code']
        now = datetime.datetime.now()
        tf = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        tf_data = '{}>>{}'.format(tf, msg)
        #
        self.root.console.update_console1(data=tf_data)

        if type==0:
            return

        if code!=0:
            QMessageBox.information(self.root, '提示信息', '请查看调试器是否正常连接。', QMessageBox.Ok)
        if self.gdbserver:
            self.gdbserver.close()
            self.gdbserver=None

    def on_receive_gdb(self,data):
        type=data['type']
        msg=data['msg']
        if 'COMPLETED_TASK' in msg:
            #
            if self.injector:
                self.injector.running=False
                time.sleep(5)
                self.injector=None
            #
            if self.gdbserver:
                self.gdbserver.close()
                self.gdbserver=None
            #
            self.freeze_ui(status=False)
            return            
        # print('on_receive_gdb',msg)
        if 'WF_HEAD' in msg:
            self.buffer1=[]
        if self.buffer1 is not None:
            now = datetime.datetime.now()
            tf = now.strftime("%Y-%m-%d %H:%M:%S.%f")
            tf_data = '{}>>{}'.format(tf, msg)
            self.buffer1.append(tf_data)
            self.root.console.update_console1(data=tf_data)
        if 'WF_END' in msg:
            fault=data['fault']
            print('fault',fault)
            fault=json.loads(fault)
            app=fault['app']
            mode=fault['mode']
            id=fault['id']
            appPath=os.path.join('./out',app)
            if not os.path.exists(appPath):
                os.mkdir(appPath)
            modePath=os.path.join(appPath,mode)
            if not os.path.exists(modePath):
                os.mkdir(modePath)
            fp=os.path.join(modePath,'{:05d}.txt'.format(id))
            with open(fp,'w') as wf:
                for ln in self.buffer1:
                    wf.write(ln+'\n')
                    # print('ln',ln)
                self.buffer1=None
        
    
    def on_receive_com(self,data):
        msg=data['msg']
        now = datetime.datetime.now()
        tf = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        tf_msg = '{}>>{}'.format(tf, msg)
        if self.buffer1:
            self.buffer1.append(tf_msg)
        self.root.console.update_console2(data=tf_msg)
        pass