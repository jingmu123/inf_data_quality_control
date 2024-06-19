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
    [r'.*(地址：|旺旺：|最新修正版|倪海厦(注解|中医)|版权所有|责任编辑|排版设计|印张|精胶装|印制：|页数：).*', ''],
    # 清洗无关文本
    [r'([。，\?])([。，～\?])', r'\1'],  # 删除连续标点
    [r'(\d+) +', r'\1'],  # 删除空格
    [r'\(cid:\d+\)', ''],

]

# 单个的无关文本替换
context_pattern = [
    ['□', '口'],
    ['ロ','口'],
    ['目 录', ''],
    ['图示如：', ''],
    ['''倪海厦中医系列书籍之②《黄帝内经》
倪海厦注解《黄帝内经》
民国 倪海厦注解 策划 守候诚实国学书店
印制：守候诚实国学书店
地址：http://chshsd.taobao.com/
旺旺：守候诚实 QQ：498609360
排版设计：肖丽君
印刷：彩色印刷 装订：精胶装
责任编辑：小梅
版权所有 翻版必究
开本大 16 开 21 X 29.7 （厘米）印张 14
2014 年 最新修正版 第九次印刷 字数：55 万 4 千字
页数：301 定价：60 元倪海厦人纪系列书籍之②《黄帝内经》''', ''],
    ['则生痿？也',''],
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
    #context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    return context


class speicalProces:
    def __init__(self):
        pass

    def step1_remove_text(self, item):
        if item in menu_new:
            item = '\x95'+item + '\x95'
            # print(item)
            return item
        elif len(item) < 2000000 and '篇' in item:
            item_spilt=str(item).split('。')
            if item_spilt[-1] in menu_new :
                item = ''.join(item_spilt[0:-1]) +'。\x95'+item_spilt[-1]+'\x95'
                # print(item)
                return item
            elif '篇' in item_spilt[-1]  and re.findall('[是别断？究之都很那张他我”黄\d]',item_spilt[-1])==[]:
                # print(item_spilt[-1])
                item = ''.join(item_spilt[0:-1]) +'。\x95'+item_spilt[-1]+'\x95'
                return item
            else:
                pass
                # print(item)
        elif '节' in item:
            pass
            # print(item)
        if re.findall('([。？！] *)$', item) != []:#给结尾未。加换行标记符号
            item = item + '\x95'
            # print(item)
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
    context = re.sub(r'\nP\d+-P?\d+', '', context)  # 删除页码
    context = re.sub(r'\n(守候诚实国学书店)', r'\1', context)  # 先删除\n去掉干扰
    context = re.sub(r'本资料仅共内部学习交流使用请阅读后自觉销毁', r'', context)  # 先删除\n去掉干扰
    context = re.sub(r'守候诚实国学书店 第 [1-8] 页 共 301 页 内部中医教材系列倪海厦人纪系列书籍之②《黄帝内经》', r'', context)  # 先删除\n去掉干扰

    for item in context.split(split_token):
        sp.step2_menu(item)  # 得到目录
    for i in menu:
        if '篇' in i:
            name = str(i).replace(' ', '').split('篇')
            menu_new.append(name[1] + '篇' + name[0])
        menu_new.append(i)
    print(menu_new)
    # print(menu_new)
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
    context = re.sub(r'守候诚实国学书店 第 \d+页 共 301页 内部中医教材系列(倪海厦人纪系列书籍之②《黄帝内经》)?', '',
                     context)
    context = re.sub('\n+', '\n\n', context)

    # 2.替换 固定内容（非泛化）

    return context


fw = open("../../../../full_data/nihaixia_zhongyi/nihaixia_zhongyi_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/nihaixia_zhongyi/nihaixia_zhongyi_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        context = post_process(context)
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
