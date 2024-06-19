import json
import re
from pprint import pprint
from tqdm import tqdm
import Levenshtein

log_dict = {}
menu = []
menu_new = []
# 规则必须以列表形式存储，分别是要替换的内容，以及替换成什么内容
pattern_list = [
    [r'P\d+-P?\d+', ''],  # 删除页码
    [r'.*(书店|地址：|旺旺：|系列书籍之|最新修正版|倪海厦注解|版权所有|责任编辑|排版设计|印张|精胶装).*', ''],  # 清洗无关文本
    [r'([。，])([。，～])', r'\1'],  # 删除连续标点
    ['(\d+) +', r'\1']  # 删除空格

]

# 单个的无关文本替换
context_pattern = [
    ['本资料仅共内部学习交流使用请阅读后自觉销毁', ''],
    ['目 录', ''],
    ['图示如：', ''],
]


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context


class speicalProces:
    def __init__(self):
        pass

    def step1_remove_text(self, item):
        if item in menu_new:
            item = item + '\x95'
            return item

        if re.findall('([。？ ！] *)$', item) != [] or item in menu:
            item = item + '\x95'
        return item

    def step2_menu(self, item):
        if re.findall('[^\.]*\.{10,}\d+', item) != []:
            menu_name = re.sub('([^\.]*)\.{10,}\d+', r'\1', item)
            menu.append(menu_name)
            return ''
        return item


def clean_text(context, lang="zh"):
    # 如果存在特殊处理，以类的方式整合，初始化类；
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    result = []
    context=re.sub('\n(守候.*书店)',r'\n\n\1')
    for item in context.split(split_token):
        sp.step2_menu(item)  #得到目录
    for i in menu:
        if '篇' in i:
            name = str(i).replace(' ', '').split('篇')
            menu_new.append(name[1] + '篇' + name[0])
        menu_new.append(i)
    print(menu_new)
    for item in context.split(split_token):
        item = sp.step2_menu(item)
        item = sp.step1_remove_text(item)

        if item == '':
            continue

        for replace_item in context_pattern:
            item = item.replace(replace_item[0], replace_item[1])
        # 1.正则
        for pattern_item in pattern_list:
            if re.findall(pattern_item[0], item) != []:
                if str(pattern_item[0]) not in log_dict:
                    log_dict[str(pattern_item[0])] = re.findall(pattern_item[0], item)
                else:
                    log_dict[str(pattern_item[0])] = log_dict[str(pattern_item[0])] + re.findall(pattern_item[0], item)
            item = re.sub(pattern_item[0], pattern_item[1], item)
        result.append(item)
    context = split_token.join(result)
    context = re.sub('([^\x95])\n', r'\1', context)
    context = re.sub('\x95', '\n', context)
    context = re.sub('\n+', '\n\n', context)

    # 2.替换 固定内容（非泛化）

    return context


fw = open("../../../../full_data/nihaixia_zhongyi2/nihaixia_zhongyi2_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/nihaixia_zhongyi2/nihaixia_zhongyi2_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        # context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
    # print(log_dict.keys())  # 打印log等内容
    # for i in log_dict.keys():
    #     if i in [r'P\d+-P?\d+', r'[第笔]?\d+页共\d+页', r'.*(√|°).*', r'[A-Z]+ \? \??\d?',
    #              r'\d? ?[^！。 ]*[A-HJ-Z]+[\.]* \??[0-46-9]? ?[0-46-9]? ?[A-HJ-Z]*',
    #              r' ?[\u4e00-\u9fa5]*书店[\u4e00-\u9fa5 ]*', r' ?([A-Z]+)\d*\?*', r' ?\?? ?\d? ?\+\d? ?\d?', r's ',
    #              r'["”]?\d? ?[ \d]\?+ ?[0-46-9]?[0-46-9]? ?[0-13-9]? ?', r'([。，])([。，～])', r'～?[ ～一]\d+ \d* ?',
    #              r'\??[71] \d?|\d+$']:
    #         pass
    #     else:
    #         pprint(log_dict[i])
