import matplotlib.pyplot as plt
import numpy as np
import sys
import json
# 原始数据
data = """
r0,sdc:0.102,due:0.661,masked:0.237
r1,sdc:0.208,due:0.406,masked:0.386
r2,sdc:0.01,due:0.071,masked:0.919
r3,sdc:0.286,due:0.0,masked:0.714
r4,sdc:0.09,due:0.73,masked:0.18
r5,sdc:0.344,due:0.356,masked:0.3
r6,sdc:0.723,due:0.0,masked:0.277
r7,sdc:0.0,due:0.171,masked:0.829
r8,sdc:0.378,due:0.533,masked:0.089
r9,sdc:0.144,due:0.557,masked:0.299
r10,sdc:0.0,due:0.149,masked:0.851
r11,sdc:0.0,due:0.011,masked:0.989
r12,sdc:0.0,due:0.0,masked:1.0
sp,sdc:0.0,due:0.898,masked:0.102
lr,sdc:0.0,due:0.032,masked:0.968
pc,sdc:0.07,due:0.74,masked:0.19
app,sdc:0.07,due:0.74,masked:0.19
"""

def analyze_data(input_path=None,output_path=None):
    # output_path=sys.argv[3]
    result_data=data.strip().split('\n')
    # print('result_path',result_path)
    # print('script_path',script_path)
    #
    # categories = []
    # sdc_values = []
    # due_values = []
    # masked_values = []
    results=[]
    #
    for line in result_data:
        parts = line.split(',')
        category=parts[0]
        sdc=float(parts[1].split(':')[1])
        due=float(parts[2].split(':')[1])
        masked=float(parts[3].split(':')[1])
        results.append(
            {
                'category':category,
                'sdc':sdc,
                'due':due,
                'masked':masked
            }
        )
        # categories.append(parts[0])
        # sdc_values.append(float(parts[1].split(':')[1]))
        # due_values.append(float(parts[2].split(':')[1]))
        # masked_values.append(float(parts[3].split(':')[1]))
    # print('result_path',result_path)
    # parsed_results={
    #     'categories':categories,
    #     'sdc_values':sdc_values,
    #     'due_values':due_values,
    #     'masked_values':masked_values
    # }
    with open(output_path,'w') as wf:
        json.dump(results,wf,indent=2)
    # print(json.dumps(results))
    return

if __name__=='__main__':
    if len(sys.argv) < 4:
        print("请提供要分析的目录路径和结果保存路径。")
        sys.exit(1)
    input_path=sys.argv[1]
    output_path=sys.argv[2]
    analyze_data(input_path,output_path)