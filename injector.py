import json
import time
import json
import random
import datetime
import subprocess

from soupsieve.util import lower
from pygdbmi.gdbcontroller import GdbController

from PyQt5.QtWidgets import  QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import constant


JLINK_RET_CODE_MAP = {
    0: 'No error. GDB Server closed normally.',
    -1: 'Unknown error. Should not happen.',
    -2: 'Failed to open listener port (Default: 2331).',
    -3: 'Could not connect to target. No target voltage detected or connection failed.',
    -4: 'Failed to accept a connection from Injector.',
    -5: 'Failed to parse the command line options, wrong or missing command line parameter.',
    -6: 'Unknown or no device name set.',
    -7: 'Failed to connect to J-Link.'
}


class GDBServer(QThread):
    data_signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        arch, core, debugger, interface=self.get_options()
        # assert log_file
        # self.command = 'JLinkGDBServer -port 2331 -device STM32F407ZG -endian little -speed 4000 -if swd -vd -nogui'.split()
        self.command = 'JLinkGDBServer -port 2331 -device {} -endian little \
             -speed 4000 -if {} -vd -nogui'.format(core,interface).split()
        self.proc = None
        self.running = False
        self.returncode = 0
        self.returnmsg = ''

    def get_options(self):
        try:
            with open(constant.mcu_json, 'r') as rf:
                data = json.load(rf)
                arch = data.get('arch', '')
                core = data.get('core', '')
                debugger = data.get('debugger', '')
                interface = data.get('interface', '')
        except FileNotFoundError:
            print("配置文件未找到。")
        except ValueError:
            print("配置文件内容格式错误。")
        return arch, core, debugger, interface

    def set_log_file(self, log_file):
        self.log_file = log_file

    def set_command(self, command):
        self.command = command

    def close(self):
        assert (self.proc)
        self.proc.terminate()
        self.running = False

    def run(self):
        assert self.command
       
        # 创建子进程
        self.proc = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        # 实时读取输出
        while True:
            # 读取一行输出
            output = self.proc.stdout.readline().strip()
            if output == '' and self.proc.poll() is not None:
                break
            if output:
                print(output)
                if 'Connected to target' in output:
                     self.running = True
                data={
                    'type':0,
                    'code':40,
                    'msg':output
                }
                self.data_signal.emit(data)
        self.returncode = self.proc.wait()
        if self.returncode > 127:
            self.returncode = self.returncode - 256
        self.running = False
        ret_code_map = JLINK_RET_CODE_MAP
        if self.returncode in ret_code_map.keys():
            ret_msg = ret_code_map[self.returncode]
        else:
            ret_msg = 'Unkown Error Message!'
        self.returnmsg=ret_msg
        data={
            'type':1,
            'code':self.returncode,
            'msg':ret_msg
        }
        self.data_signal.emit(data)
        print(f"子进程返回码: {self.returncode}")
        pass



WF_HEAD='WF_HEAD'
WF_END='WF_END'
INJ_HEAD='INJ_HEAD'
INJ_END='INJ_END'

class Injector(QThread):
    data_signal = pyqtSignal(dict)
    SUPPORT_MODES=['RF','IOV','IOV','MEM']

    @staticmethod
    def debug(msg):
        print(msg)

    @staticmethod
    def bit_flip(value, flip_pos):
        value ^= (1 << flip_pos)
        return value


    def __init__(self):
        super().__init__()
        self.elf_bin = None
        self.gdb_bin = None
        self.gdbmi = None
        self.port = 2331
        self.mode = 'RF'
        self.faults=None
        self.running=False
        self.faults_json_path=None


    def check_init(self):
        assert self.elf_bin
        assert self.gdb_bin
        assert self.port
        assert self.faults_json_path
        assert self.mode in Injector.SUPPORT_MODES

    def set_elf_bin(self, elf_bin):
        self.elf_bin = elf_bin

    def set_gdb_bin(self, gdb_bin):
        self.gdb_bin = gdb_bin

    def set_fault(self, fault):
        self.fault = fault

    def get_fault(self):
        return self.fault

    def set_mode(self, mode):
        self.mode = mode

    def set_port(self, port):
        self.port = port

    def send(self, command=None):
        assert (command)
        response = self.gdbmi.write(command)
        Injector.debug(response)
        return response

    def launch(self):
        command = [self.gdb_bin, "--nx", "--quiet",
                   "--interpreter=mi3", self.elf_bin]
        self.gdbmi = GdbController(command)
        Injector.debug(self.gdbmi.command)  # print actual command run as subprocess

    def remote(self):
        status=False
        response=self.send(command='target remote:{}'.format(self.port))
        for res in response:
            if res['type'] == 'console':
                if 'Remote debugging using :{}'.format(self.port) in res['payload']:
                    status=True
        return status


    def extended_remote(self):
        self.send(command='target extended-remote:{}'.format(self.port))

    def init(self):
        commands = [
            'set confirm off',
            'set pagination off',
            'set history save',
            'set verbose off',
            'set print pretty on',
            'set print arrary off',
            'set print arrary-indexes on',
            'set python print-stack full'
        ]
        for command in commands:
            self.send(command=command)

    def begin(self):
        self.send(command='monitor reset')

    def nexti(self):
        self.send(command='nexti')

    def stepi(self):
        self.send(command='stepi')
        self.send(command='display $pc')

    def go_ahead(self):
        self.send(command='monitor go')

    def halt(self):
        self.send(command='monitor halt')

    def get_register(self, name=None):
        assert (name)
        rsp=self.send(command='monitor reg {}'.format(name))
        value=None
        for ln in rsp:
            if ln['type']=='target':
                payload=ln['payload']
                name1=payload[payload.find('(')+1:payload.find(')')].split('=')[0].strip()
                value=payload[payload.find('(')+1:payload.find(')')].split('=')[1].strip()
                assert (lower(name)==lower(name1))
        Injector.debug('register name:{},value:{}'.format(name,value))
        return value

    def set_register(self, name=None,value=None):
        assert (name)
        assert value
        self.send(command='monitor reg {} = {}'.format(name, value))

    def get_memory(self,name=None):
        assert (name)
        rsp=self.send(command='monitor memU8 {}'.format(name))
        for ln in rsp:
            if ln['type']=='target':
                payload=ln['payload']
                name1=payload.split()[3].strip()
                value=payload[payload.find('=')+1:payload.find(')')].strip()
                assert (int(name,16)==int(name1,16))
        Injector.debug('memory name:{},value:{}'.format(name,value))
        return value
    
    def set_memory(self,name=None,value=None):
        assert (name)
        assert value
        self.send(command='monitor memU8 {} = {}'.format(name, value))   

    def stepi(self):
        self.send(command='monitor si') 

    def quit(self):
        response = self.gdbmi.exit()
        Injector.debug(response)

    def test(self):
        response = self.gdbmi.write('11 {}'.format(self.exec_file))
        Injector.debug(response)

    def profile_inst(self):
        # self.launch()
        # self.init()
        # self.extended_remote()
        # self.begin()
        # self.halt()
        # self.stepi()
        pass

    # def

    def do_inject_rf(self):
        regs=self.fault['regs']
        Injector.debug(self.fault)
        # step.1:get registers
        for reg in regs:
            name = reg['name']
            flips = reg['flips']
            before_value = self.get_register(name=name)
            after_value = int(before_value, 16)
            for pos in flips:
                after_value = Injector.bit_flip(value=after_value, flip_pos=pos)
            after_value = hex(after_value)
            self.set_register(name=name, value=after_value)
            after_value1 = self.get_register(name=name)
            ###############specialf case
            if 'pc' in name:
                pass
            else:
                assert (int(after_value, 16) == int(after_value1, 16))
            ############################
            reg['before_value'] = before_value
            reg['after_value'] = after_value1
        # print(self.fault)
        pass

    def do_inject_mem(self):
        mems=self.fault['mems']
        for mem in mems:
            name=mem['name']
            flips=mem['flips']
            before_value = self.get_memory(name=name)
            after_value = int(before_value, 16)
            for pos in flips:
                after_value = Injector.bit_flip(value=after_value, flip_pos=pos)
            after_value = hex(after_value)
            self.set_memory(name=name, value=after_value)
            after_value1 = self.get_memory(name=name)
            mem['before_value'] = before_value
            mem['after_value'] = after_value1
        pass

    def do_inject_inst(self):
        mode=self.fault['mode']
        regs=self.fault['regs']
        current_pc=self.get_register(name='pc')
        inst_key=str(int(current_pc,16))
        inst=self.inst_map[inst_key]
        iov_action=inst['iov_action']
        self.fault['pc']=current_pc
        self.fault['inst_type']=inst['type']    
        Injector.debug(inst)
        if iov_action=='after' and mode=='IOV':
            self.stepi()
            pass
        # step.1:get registers
        for reg in regs:
            flips = reg['flips']
            if mode=='IOA' and len(inst['adr_regs']):
                random_reg = random.choice(inst['adr_regs'])
            elif mode=='IOV' and len(inst['dst_regs']):
                random_reg = random.choice(inst['dst_regs'])
            else:
                random_reg=None
            if random_reg:
                before_value = self.get_register(name=random_reg)
                after_value = int(before_value, 16)
                for pos in flips:
                    after_value = Injector.bit_flip(value=after_value, flip_pos=pos)
                after_value = hex(after_value)
                self.set_register(name=random_reg, value=after_value)
                after_value1 = self.get_register(name=random_reg)
                ###############specialf case
                # if 'pc' in random_reg:
                #     pass
                # else:
                #     assert (int(after_value, 16) == int(after_value1, 16))
                ############################
                reg['before_value'] = before_value
                reg['after_value'] = after_value1
       
            
            
###################################################

    def send_msg(self,type=2,msg=None,fault=''):
        assert msg
        data={
            'type':type,
            'fault':fault,
            'msg':msg,
        }
        self.data_signal.emit(data)

    def run(self):
        self.check_init()
        with open(self.faults_json_path,'r') as rf:
            self.faults=json.load(rf)
        with open(constant.inst_json,'r') as rf:
            self.inst_map=json.load(rf)
        self.set_mode(mode=self.faults[0]['mode'])
        for i in range(len(self.faults)):
            if not self.running:
                break
            self.fault=self.faults[i]
            if self.fault['injected']:
                continue
            self.send_msg(msg='{}'.format(WF_HEAD),fault=self.fault)
            before_tm=self.fault['before_tm']
            after_tm=1
            #step1:launch
            self.launch()
            self.init()
            status=self.remote()
            assert 'Remote connection is lost.' and status
            self.begin()
            self.go_ahead()
            #step2:wait for random seconds
            time.sleep(before_tm)
            self.halt()
            #step3:inject faults
            if self.mode=='RF':
                self.do_inject_rf()
            elif self.mode=='MEM':
                self.do_inject_mem()
                pass
            elif self.mode=='IOV' or self.mode=='IOA':
                self.do_inject_inst()
            inj_info='{}>>{}<<{}'.format(INJ_HEAD,json.dumps(self.fault),INJ_END)
            self.send_msg(msg=inj_info)
            #step4:resume execution
            self.go_ahead()
            time.sleep(after_tm)
            self.halt()
            self.quit()
            self.send_msg(msg='{}'.format(WF_END),fault=json.dumps(self.fault))
            #
            self.fault['injected']=True
            #
            if (self.fault['id']+1) % 10==0 or self.fault['id']==0:
                print('faults_json_path',self.faults_json_path)
                with open(self.faults_json_path,'w') as wf:
                    json.dump(self.faults,wf,indent=2)
            time.sleep(0.5)
        self.send_msg(msg='COMPLETED_TASK')
        pass
