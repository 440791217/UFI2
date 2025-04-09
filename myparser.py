import subprocess
import json
def parse_assembly(fp1):
    func_inst_map = {}
    current_func = None
    with open(fp1, 'r') as rf:
        lines=rf.readlines()
        for line in lines:
            line=line.rstrip()
            if line.endswith('>:'):
                current_func = line[:-1]
                base_addr=current_func.split(' ')[0].strip()
                # print(current_func,'-',base_addr)
                func_inst_map[current_func] = []
            elif line.startswith(' '):
                # func_inst_map[current_func].append(line)
                parts1 = line.split(';')[0].strip()
                parts2 = parts1.split('\t')
                inst_addr=parts2[0].split(':')[0]
                inst_addr=base_addr[0:len(base_addr)-len(inst_addr)]+inst_addr
                # print(inst_addr)
                inst_code=parts2[1].strip()
                inst_type=parts2[2].strip()
                if len(parts2)>3:
                    inst_op=parts2[3].strip()
                else:
                    inst_op=''
                inst_arr=[inst_addr,inst_code,inst_type,inst_op,parts1.strip()]
                func_inst_map[current_func].append(inst_arr)
    return func_inst_map

def extract_inst_type(funcs):
    myset=[]
    for f in funcs:
        for inst_arr in funcs[f]:
            name=inst_arr[2]
            if name not in myset:
                myset.append(name)
    for t in sorted(myset):
        print('myset:',t)

def start_with(arg1,arg2):
    status=False
    for t in arg2:
        if arg1.startswith(t):
            status=True
    return status


def identify_ops(funcs1):
    typearr1=['ad','and','asr','lsl','lsr','mla','mls','mov','mul','mvn','orr','sdiv','smlabb',\
        'sub','sxt','ubfx','udiv','uxt']
    inst_maps={}
    for f in funcs1:
        insts=funcs1[f]
        for inst in insts:
            inst_addr=inst[0].lower()
            inst_code=inst[1].lower()
            inst_type=inst[2].lower()
            inst_ops=inst[3].lower()
            dst_regs=[]
            adr_regs=[]
            iov_action='after'

            if start_with(inst_type,typearr1):
                reg1=inst_ops.split(',')[0].strip()
                dst_regs=[reg1]
                # print(dst_regs)
                pass
            elif start_with(inst_type,['ldm']):
                reg1=inst_ops.replace(' ','').split('{')[1].strip('}').split(',')
                dst_regs=reg1
                # print(dst_regs)
                pass
            elif start_with(inst_type,['ldr']):
                reg1=inst_ops.split(',')[0].strip()
                reg2=inst_ops.split(',')[1].strip().split(',')[0].strip('[').strip(']')
                dst_regs=[reg1]
                adr_regs=[reg2]
                # print(inst,reg1,reg2)
                pass
            elif start_with(inst_type,['stm']):
                reg1=inst_ops.replace(' ','').split('{')[1].strip('}').split(',')
                dst_regs=reg1
                iov_action='before'
                # print(dst_regs,'00000000',inst_ops)
                pass
            elif start_with(inst_type,['str']):
                reg1=inst_ops.split(',')[0].strip()
                reg2=inst_ops.split(',')[1].strip().split(',')[0].strip('[').strip(']')
                dst_regs=[reg1]
                adr_regs=[reg2]
                iov_action='before'
                pass
            inst_maps[int(inst_addr,16)]={
                'type':inst_type,
                'addr':inst_addr,
                'code':inst_code,
                'dst_regs':['r12' if reg == 'ip' else reg for reg in dst_regs],
                'adr_regs':['r12' if reg == 'ip' else reg for reg in adr_regs],
                'iov_action':iov_action,
            }
    for k in inst_maps:
        # print(inst_maps[k])
        pass
    return inst_maps


def export_asm(fp1=None,fp2=None):
    command='arm-none-eabi-objdump -d {} > {}'.format(fp1,fp2)
    # print(command)
    # 执行简单的ls命令，列出当前目录下的文件
    result = subprocess.run(command, shell=True,  text=True)
    print('result code:',result.returncode)
    return result.returncode
    
def main(fp1='dnn_llvm.out',fp2='config/instrcutions.txt',fp3='config/instructions.json'):
    rc=export_asm(fp1=fp1,fp2=fp2)
    if rc!=0:
        print('111')
        exit(-1)
    funcs = parse_assembly(fp1=fp2)
    # extract_inst_type(funcs=funcs)
    inst_map=identify_ops(funcs1=funcs)
    # print(123123)
    with open(fp3,'w') as wf:
        json.dump(inst_map,wf,indent=2)
        for inst in inst_map:
            # print(inst,'--',inst_map[inst])
            pass
    return True

if __name__=='__main__':
    main(fp1='dnn_llvm.out')