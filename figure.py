import matplotlib.pyplot as plt
import numpy as np
import sys

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
"""
def plot_fig(data,save_path=None,yy=-0.15):
    # 解析数据
    lines = data
    categories = []
    sdc_values = []
    due_values = []
    masked_values = []

    for line in lines:
        parts = line.split(',')
        categories.append(parts[0])
        sdc_values.append(float(parts[1].split(':')[1]))
        due_values.append(float(parts[2].split(':')[1]))
        masked_values.append(float(parts[3].split(':')[1]))

    # 设置图片清晰度
    plt.rcParams['figure.dpi'] = 120

    # 设置全局字体为 Times New Roman，大小为 9pt
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 8
    })

    # 创建图形并设置合适的大小，可根据实际调整
    fig, ax = plt.subplots(figsize=(3, 3))

    # 绘制堆积柱状图
    x = np.arange(len(categories))
    width = 0.6

    bottom = np.zeros(len(categories))

    # 先绘制 Masked，颜色设置为绿色
    rects1 = ax.bar(x, masked_values, width, label='Masked', bottom=bottom, color='green')
    bottom += np.array(masked_values)

    # 接着绘制 DUE，颜色设置为黑色
    rects2 = ax.bar(x, due_values, width, label='DUE', bottom=bottom, color='black')
    bottom += np.array(due_values)

    # 最后绘制 SDC，颜色设置为红色
    rects3 = ax.bar(x, sdc_values, width, label='SDC', bottom=bottom, color='red')

    # 添加标题和标签
    ax.set_ylabel('AVF')
    ax.set_title('')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=90)  # 旋转 x 轴标签 90 度

    # 手动指定图例顺序并将其放置在右上角
    handles, labels = ax.get_legend_handles_labels()
    order = [2, 1, 0]  # 对应 SDC, DUE, Masked 的顺序

    ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='upper center', bbox_to_anchor=(0.5, yy), ncol=3)


    ax.set_ylim(0, 1)
    # 调整布局
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=160)
    # 显示图形
    plt.show()


def plot_fig1(data,save_path=None,yy=-0.15):
    categories = []
    sdc_values = []
    due_values = []
    masked_values = []
    for d in data:
        category=d['category']
        sdc=d['sdc']
        due=d['due']
        masked=d['masked']
        categories.append(category)
        sdc_values.append(sdc)
        due_values.append(due)
        masked_values.append(masked)
    # 设置图片清晰度
    plt.rcParams['figure.dpi'] = 120

    # 设置全局字体为 Times New Roman，大小为 9pt
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 8
    })

    # 创建图形并设置合适的大小，可根据实际调整
    fig, ax = plt.subplots(figsize=(3, 3))

    # 绘制堆积柱状图
    x = np.arange(len(categories))
    width = 0.6

    bottom = np.zeros(len(categories))

    # 先绘制 Masked，颜色设置为绿色
    rects1 = ax.bar(x, masked_values, width, label='Masked', bottom=bottom, color='green')
    bottom += np.array(masked_values)

    # 接着绘制 DUE，颜色设置为黑色
    rects2 = ax.bar(x, due_values, width, label='DUE', bottom=bottom, color='black')
    bottom += np.array(due_values)

    # 最后绘制 SDC，颜色设置为红色
    rects3 = ax.bar(x, sdc_values, width, label='SDC', bottom=bottom, color='red')

    # 添加标题和标签
    ax.set_ylabel('AVF')
    ax.set_title('')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=90)  # 旋转 x 轴标签 90 度

    # 手动指定图例顺序并将其放置在右上角
    handles, labels = ax.get_legend_handles_labels()
    order = [2, 1, 0]  # 对应 SDC, DUE, Masked 的顺序

    ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='upper center', bbox_to_anchor=(0.5, yy), ncol=3)


    ax.set_ylim(0, 1)
    # 调整布局
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=160)
    # 显示图形
    plt.show()    

def entry():
    plot_fig(data=data.strip().split('\n'))

if __name__=='__main__':
    if len(sys.argv) < 4:
        print("请提供要分析的目录路径以及两个额外参数。")
        sys.exit(1)
    # print(data.split('\n'))
    # plot_fig(data=data.strip().split('\n'))
    entry()