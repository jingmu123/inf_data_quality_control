import matplotlib.pyplot as plt
import json

import numpy as np
from matplotlib.font_manager import FontProperties

# 设置matplotlib支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def compare_histograms(data_list):
    all_keys = []

    for item in data_list:
        val = item["value"]
        all_keys += list(val.keys())
    all_keys = list(set(all_keys))

    value_list = []
    for item in data_list:
        val = item["value"]
        new_val = [val[key] if key in val else 0 for key in all_keys]
        value_list.append({
            "name": item["name"],
            "value": new_val,
        })


    # 设置条形图的宽度

    bar_width = 1/len(data_list) - 0.05
    index = range(len(all_keys))

    # 绘制直方图
    plt.figure(figsize=(21, 13))
    color_list = ["orange","blue","yellow","red","green","purple","black"]

    for idx, item in enumerate(value_list):
        plt.bar([i + bar_width*idx for i in index], item["value"], width=bar_width, color=color_list[idx], label=item["name"])



    plt.xticks([idx for idx in index], all_keys, rotation=-60)  # 设置x轴刻度显示key名称
    locs, labels = plt.xticks()
    print(locs,labels)

    plt.title("pdf_中文（采样:195）",fontsize=14)
    # plt.xlabel('错误类型')
    plt.ylabel('错误数量')
    #plt.grid()
    plt.legend()

    plt.show()

#stage4
reclean1 = {'错误删除': 168, '有用性': 116, '无关文本': 501, '语义不完整': 51, '序号错误': 14, '缺少换行': 294, '多余换行': 167, '栏目混乱': 202, '信息完整性': 4, '信息有用性': 56, '信息不完整': 13, '多换行': 1, '多余标点': 2, '序号格式不一致': 22, '页眉': 1, '准确性': 15, '标点错误': 5, '错别字': 14, '导航栏': 4, '特殊符号': 3, '栏目混合': 1, '格式杂乱': 1, '页脚': 1}
reclean2 = {'多余换行': 152, '缺少换行': 271, '无关文本': 542, '有用性': 119, '信息有用性': 31, '序号错误': 15, '栏目混乱': 125, '序号格式不一致': 40, '错误删除': 85, '错别字': 17, '标点错误': 3, '信息不完整': 20, '信息完整性': 4, '表格格式错误': 24, '语义不完整': 31, '公式格式错误': 1, '多余标点': 1, '有用性 ': 2, '语义重复': 2, '导航栏': 3, '表格给格式错误': 1}
reclean3 = {'缺少换行': 247, '多余换行': 134, '语义不完整': 35, '序号格式不一致': 26, '错误删除': 80, '表格格式错误': 19, '无关文本': 289, '栏目混乱': 74, '页脚': 2, '有用性': 138, '信息有用性': 37, '序号错误': 13, '信息不完整': 13, '错别': 1, '错别字': 8, '导航栏': 3, '信息完整性': 1, '特殊符号': 1, '准确性': 5, '标点错误': 2, '五百文本': 1, '多余标点': 2}
reclean4 = {'错误删除': 192, '栏目混乱': 142, '缺少换行': 306, '有用性': 104, '错别字': 19, '多余换行': 77, '无关文本': 203, '语义不完整': 37, '序号格式不一致': 126, '表格格式错误': 18, '准确性': 13, '信息有用性': 24, '信息不完整': 13, '序号混乱': 1, '信息完整性': 4, ' 缺少换行': 1, '序号个性不一致': 1, '页脚': 1, '导航栏': 1, '格式杂乱': 1}
reclean5 = {'多余标点': 2, '无关文本': 384, '缺少换行': 181, '错误删除': 143, '语义不完整': 26, '语意重复': 2, '有用性': 72, '序号格式不一致': 127, '多余换行': 328, '信息不完整': 17, '栏目混乱': 91, '信息有用性': 18, '无关问': 1, '表格格式错误': 14, '表格正文混乱': 10, '错别字': 6, '导航栏': 3, '语义重复': 1, '信息完整性': 1, '标点错误': 3}

#guidelines
reclean1 = {'有用性': 20, '错别字': 138, '缺少标点': 32, '多余换行': 141, '表格格式错误': 18, '缺少换行': 181, '无关文本': 191, '语义不完整': 85, '格式杂乱': 15, '栏目混乱': 19, '错误删除': 15, '序号格式不一致': 11, '标点错误': 12, '信息有用性': 12, '特殊符号': 5, '多余标点': 7, '语意重复': 1, '页眉': 1, '信息不完整': 2, ' 无关文本': 1, '表格给格式错误': 1, '表格正文混乱': 1}

fix_dict = {
    "多换行":"多余换行",
    "信息完整性":"信息不完整",
    "页眉":"无关文本",
    "五百文本":"无关文本",
    "导航栏":"无关文本",
    "页脚":"无关文本",
    "栏目混合":"栏目混乱",
    "有用性":"信息有用性",
    "有用性 ":"信息有用性",
}
def get_new_data(data):
    new_data = {}
    for key,val in data.items():
        if key in fix_dict:
            key = fix_dict[key]
        if key not in new_data:
            new_data[key] = 0
        new_data[key] += val
    return new_data
data_list = [
    {
        "name": "reclean1",
        "value": get_new_data(reclean1),
    },
    # {
    #     "name": "reclean2",
    #     "value": get_new_data(reclean2),
    # },
    # {
    #     "name": "reclean3",
    #     "value": get_new_data(reclean3),
    # },
    # {
    #     "name": "reclean4",
    #     "value": get_new_data(reclean4),
    # },
    # {
    #     "name": "reclean5",
    #     "value": get_new_data(reclean5),
    # }
]

compare_histograms(data_list)
