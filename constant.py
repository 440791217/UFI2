import os
root_path=""
inj_json='config/inj1.json'
uart_json='config/uart.json'
faults_json='config/faults.json'
mcu_json='config/mcu.json'
inst_txt='config/instructions.txt'
inst_json='config/instructions.json'

def init_config(root):
    global inj_json,uart_json,faults_json,mcu_json,\
        inst_txt,inst_json
    #
    configpath=os.path.join(root,'config')
    if not os.path.exists(configpath):
        os.mkdir(configpath)
    #
    outpath=os.path.join(root,'out')
    if not os.path.exists(outpath):
        os.mkdir(outpath)    
    #
    scriptspath=os.path.join(root,'scripts')
    if not os.path.exists(scriptspath):
        os.mkdir(scriptspath) 
    #
    resultspath=os.path.join(root,'results')
    if not os.path.exists(resultspath):
        os.mkdir(resultspath)     
    inj_json=os.path.join(root,inj_json)
    uart_json=os.path.join(root,uart_json)
    faults_json=os.path.join(root,faults_json)
    mcu_json=os.path.join(root,mcu_json)
    inst_txt=os.path.join(root,inst_txt)
    inst_json=os.path.join(root,inst_json)