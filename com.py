import time
import threading
import serial
import serial.tools.list_ports
import glob
import datetime
import json
from PyQt5.QtCore import QThread, pyqtSignal


class Uart(QThread):
    data_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.running=False
        self.com=serial.Serial()
        self.com.port = None  # 设置端口号
        self.com.baudrate = 115200  # 设置波特率
        self.com.bytesize = 8  # 设置数据位
        self.com.stopbits = 1  # 设置停止位
        pass

    def config(self,port=None,baudrate=115200,bytesize=8,stopbits=1,timeout=0.1):
        assert (port)
        self.com.port=port
        self.com.baudrate=baudrate
        self.com.bytesize=bytesize
        self.com.stopbits=stopbits
        self.com.timeout=timeout
        print('串口配置 port:{},baudrate:{},bytesize:{},stopbits:{},timeout:{}\n'.format(
        self.com.port,self.com.baudrate,self.com.bytesize,self.com.stopbits,self.com.timeout))


    def open(self):
        self.com.open()
        print('串口已经打开')
        self.running=self.com.is_open
        self.start()


    def close(self):
        self.running=False
        time.sleep(0.3)
        self.com.close()

    def read(self):
        # data = self.com.read(size=self.com.in_waiting)
        msg = self.com.readline()
        msg=msg.decode('utf-8', errors='ignore').strip()
        # data = self.com.readline()
        if msg:
            data={
                'type':0,
                'msg':msg
            }
            self.data_signal.emit(data)
            # print('data',data)

    def run(self):
        while self.running:
            try:
                if self.com.in_waiting>0:
                    self.read()
            except Exception as e:
                print('串口异常，已关闭')
                self.close()
                pass
