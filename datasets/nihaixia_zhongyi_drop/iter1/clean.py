import json
import re
from pprint import pprint
from tqdm import tqdm
import Levenshtein

log_dict = {}
# 规则必须以列表形式存储，分别是要替换的内容，以及替换成什么内容
pattern_list = [
    [r'P\d+-P?\d+', ''],  # 删除页码
    [r'[第笔]?\d+页共\d+页', ''],  # 删除页码
    [r'.*(√|°).*', ''],  # 删除带√°的段落
    [r'[A-Z]+ \? \??\d?', ''],  # 删除带\?和英文的内容
    [r'\d? ?[^！。 ]*[A-HJ-Z]+[\.]* \??[0-46-9]? ?[0-46-9]? ?[A-HJ-Z]*', ''],  # 清洗部分的干扰英文
    [r' ?[\u4e00-\u9fa5]*书店[\u4e00-\u9fa5 ]*', ''],  # 清洗带书店的无关文本
    [r' ?\?? ?\d? ?\+\d? ?\d?', ''],  # 清洗与+有关的内容
    [r' ?([A-Z]+)\d*\?*',
     lambda s=r'\1': s[0] if s[0] in ['DNA', ' DVD', 'DVD', 'CC', 'I', 'XXX', 'LV', 'H2O', 'C', 'X', 'PPT'] else ''],
    # 删除剩余的英文，lambal的列表为保留的英文
    # 4.3
    [r's ', ''],  # 删除小写s加空格
    [r'([。，])([。，～])', r'\1'],  # 删除连续标点
    [r'～?[ ～一]\d+ \d* ?', ''],  # 删除空格加数字的无关文本
    [r'\??[71] \d?|\d+$', ''],  ##删除空格加数字的无关文本(补充部分)
    [r'["”]?\d? ?[ \d]\?+ ?[0-46-9]?[0-46-9]? ?[0-13-9]? ?', ''],  # 删除带一个空格和?
    # [r'(.{0,10}[^。，！]$)', r'\1']#内容检测模块

]

# 单个的无关文本替换
context_pattern = [
    ['内部中医教材系列', ''],
    ['海厦中医系列书籍之②《黄帝内经', ''],
    ['目录', ''],
    ['\\_', ''],
    ['第一节书籍附赠说明', ''],
    ['图示如:', ''],
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

    def step1_remove_text(self, item):  # 删除无关文本
        if item in [' ', '', r'\n']:
            return ''
        if len(item) < 10 and re.findall(r'经|论|篇|节|帝|寿|法|雪|象|呢', item) == []:
            # pprint(item)
            return ''
        elif len(item) >= 10 and len(item) < 20 and re.findall(r'曰|帝|篇|寿|节|度|艾', item) == []:
            # pprint(item)
            return ''
        elif len(item) >= 20 and len(item) <= 40 and re.findall(r'普|\||毁|乌|期|L|1', item) != []:
            # pprint(item)
            return ''
        elif len(re.findall('“', item)) > 2 and len(item) < 200:  # 删除不在上面规则里面的无关文本
            # print(item)
            return ''
        else:
            return item

    def step2_judge_Line_error(self, item):  # 修复换行错误，有一定比例的修复错误
        if re.findall(r'[^。，！\?、,？;]$', item):
            if re.findall(r'篇|节|第|内|曰|帝', item) != [] and len(item) <= 80:
                # print(item)
                return item
            else:
                return item + 'Z'
        else:
            return item

    def remove_repeat(self, item_list):#修复重复文本错误
        new_item_list = []
        length = len(item_list)-1
        i = 0
        while i < length:
                b = Levenshtein.jaro_winkler(item_list[i], item_list[i + 1])
                if b > 0.8:
                    print([item_list[i].strip("\n"), "| | |", item_list[i + 1].strip("\n")])
                    if len(item_list[i]) > len(item_list[i + 1]):
                        new_item_list.append(item_list[i])
                    else:
                        new_item_list.append(item_list[i + 1])
                    i += 2
                else:
                    new_item_list.append(item_list[i])
                    i += 1
        new_item_list.append(item_list[i])

        return new_item_list


def clean_text(context, lang="zh"):
    # 如果存在特殊处理，以类的方式整合，初始化类；
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    result = []
    for item in context.split(split_token):
        item = sp.step1_remove_text(item)
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
        item = sp.step2_judge_Line_error(item)

        result.append(item)
    result=sp.remove_repeat(result)
    context = split_token.join(result)
    context = context.replace('Z\n\n', '')
    context = context.replace(' ', '')

    # 2.替换 固定内容（非泛化）

    return context


fw = open("../../../../full_data/nihaixia_zhongyi2/nihaixia_zhongyi2_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/nihaixia_zhongyi2/nihaixia_zhongyi2_preformat.jsonl", "r", encoding="utf-8") as fs:
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
