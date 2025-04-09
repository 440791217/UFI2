import os
import json
import shutil
import sys



def filter_files(dir_path):
    val_fs=[]
    inval_fs=[]
    for f in sorted(os.listdir(dir_path)):
        val_status=0
        fp=os.path.join(dir_path,f)
        with open(fp,'r') as rf:
            lines=rf.readlines()
            start1=0
            start2=0
            start3=0
            for i in range(len(lines)):
                ln=lines[i]
                if 'INJ_HEAD' in ln and 'INJ_END' in ln:
                    start3=1
                    break
                if 'start main' in ln:
                    start1+=1
                if 'start intermain' in ln:
                    start2+=1
            if start1==1 and start2>10 and start3==1:
                val_status=1
        # if val_status==1:
        val_fs.append(fp)
        # else:
        #     inval_fs.append(fp)
    return val_fs,inval_fs

def plot_fig(reg_list,results,save_path):
    ln1s=[]
    ln2s=[]
    for reg in reg_list:
        result=results[reg]
        total=result['total']
        if total==0:
            continue
        sdc=round(result['sdc']/total,3)
        due=round(result['due']/total,3)
        masked=round(result['masked']/total,3)
        ln1s.append('reg {} result:{}'.format(reg,results[reg]))
        ln2s.append('{},sdc:{},due:{},masked:{}'.format(reg,sdc,due,masked))
    # for ln in ln1s:
    #     print(ln)
    # for ln in ln2s:
        # print(ln)
    # fig1.plot_fig(data=ln2s,save_path=save_path)

def parse_files(val_fs):
    result_map = {
        'sdc': 0,
        'due': 0,
        'masked': 0,
        'total': 0,
    }
    reg_result_map={

    }
    reg_list=['r0','r1','r2','r3','r4','r5','r6','r7','r8','r9','r10','r11','r12','sp','lr','pc']
    for reg in reg_list:
        reg_result_map[reg]={
            'sdc': 0,
            'due': 0,
            'masked': 0,
            'total': 0,
        }
    for fp in val_fs:
        inj_status = 0
        start_main = 0
        start_intermain=0
        FAULT_DETECTED_DWC = 0
        FAULT_DETECTED_RWC = 0
        HardFault_Handler = 0
        detect_due=0
        sdc_status = 0
        info=''
        regs=None
        reg_name=''
        with open(fp,'r') as rf:
            lines=rf.readlines()
            for ln in lines:
                if 'INJ_HEAD' in ln and 'INJ_END' in ln:
                    inj_status=1
                    info=ln[ln.find('{'):ln.rindex('}')+1]
                    # print(info)
                    info=json.loads(info)
                    regs=info['regs']
                    reg_name=regs[0]['name']
                    # print(reg_name)
                if inj_status==0:
                    continue
                if 'detect due' in ln:
                    detect_due=1
                if 'sdc' in ln:
                    sdc_status=1
        if sdc_status==1:
            result_map['sdc']+=1
            reg_result_map[reg_name]['sdc']+=1
        elif detect_due==1:
            result_map['due']+=1
            reg_result_map[reg_name]['due'] += 1
            # print('due_file:',fp,'start_main:',start_main,'start_intermain:',start_intermain,'reg_name:',reg_name)
        else:
            result_map['masked']+=1
            reg_result_map[reg_name]['masked'] += 1
        result_map['total']+=1
        reg_result_map[reg_name]['total'] += 1
    # print(reg_result_map)
    # plot_fig(reg_list=reg_list, results=reg_result_map,save_path=save_path)
    for k in reg_result_map.keys():
        reg_result_map[k]['sdc']=round(reg_result_map[k]['sdc']/reg_result_map[k]['total'],2)
        reg_result_map[k]['due']=round(reg_result_map[k]['due']/reg_result_map[k]['total'],2)
        reg_result_map[k]['masked']=round(reg_result_map[k]['masked']/reg_result_map[k]['total'],2)
        # print(reg_result_map[k]['sdc'])
    results=[]
    for k in ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9','r10' ,'r11', 'r12', 'sp', 'lr', 'pc']:
        if k in reg_result_map.keys():
            data={
                'category':k,
                'sdc':reg_result_map[k]['sdc'],
                'due':reg_result_map[k]['due'],
                'masked':reg_result_map[k]['masked']
            }
            results.append(data)
    data=[]
    sdc=round(result_map['sdc']/result_map['total'],2)
    due=round(result_map['due']/result_map['total'],2)
    masked=round(result_map['masked']/result_map['total'],2)
    data={
        'category':'app',
        'sdc':sdc,
        'due':due,
        'masked':masked
    }
    results.append(data)
    for result in results:
        print(result)
    
    return results

def main(**args):
    object = args['object']
    dp=args['dp']
    dir_path = '{}/{}/RF/'.format(dp,object)
    dir_path1 = '{}/{}.png'.format(dp,object)
    val_fs,inval_fs=filter_files(dir_path=dir_path)
    # print('val_fs num:{},inval_fs num:{}'.format(len(val_fs),len(inval_fs)))
    result_map,reg_result_map=parse_files(val_fs=val_fs,save_path=dir_path1)


def analyze_data(input_path=None,output_path=None):
    val_fs,inval_fs=filter_files(dir_path=input_path)
    # print('val_fs num:{},inval_fs num:{}'.format(len(val_fs),len(inval_fs)))
    results=parse_files(val_fs=val_fs)
    with open(output_path,'w') as wf:
        json.dump(results,wf,indent=2)


if __name__=='__main__':
    if len(sys.argv) >3:
        input_path=sys.argv[1]
        output_path=sys.argv[2]
        analyze_data(input_path=input_path,output_path=output_path)
    else:
        analyze_data(input_path='/home/mark/github/UFI2/out/RF',output_path='/home/mark/github/UFI2/results/rf.log')
    # dp = '/home/mark/github/UFI1/ide/out/'
    # # outs=[]
    # # out=main(object=ar,dp=dp)
    # # outs.append(out)
    # main(object='',dp=dp)

    # main(object='mm')