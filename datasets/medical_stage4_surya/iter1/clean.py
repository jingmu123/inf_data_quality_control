import json
import os
import re
from tqdm import tqdm
import math
import numpy as np


pattern_list_en = [
    #带特殊符号的图片中内容
    [r'[^\n]*(■|❏)[^\n]*',''],
    [r'👍|▶|●|©|®|([^\n]*↑[^\n]*)|†|¶|║|§|∧|™', ''],
    #句末数字引用
    ##1.带括号 book (1，2).
    [r'(?<=([^0-9]|\.))\s*\(\d+\s*(?:[-,;–.]\d+)*\)\s*(?=(\n|\.|,))',''],
    ##2.不带括号但是数字前是句号. 数字后是换行或者大写字母
    [r'(?<=[^0-9]\.)\s*\d+\s*(?:[-,;–.]\d+)*(?=$)',''],
    ##3.带括号(30° downward approximately).(5.19)
    [r'(?<=\.)\(\d+\s*(?:[-,;–.]\d+)*\)',''],
    #无关图片引用
    [r'[^\n]*\b(Fig(s?)(ure)?(s?))\b\.(\s*| )(\d+)?\.?[^\n]*',''],
    [r'(\()\b(Figure(s?)|figure(s?)|Section|diagram|Appendix|Box|(S|s)ource(s?)|Fig|p)\b:?\.?\s*(\d+)?(\.?).*?(\))',''],
    #句首无关数字
    [r'(?<=[^0-9]\.)\s*\d+(?:\s*[-;,–.]\s*\d+\s*)*\s*(?=[A-Z])',''],
    #参考文献
    [r'[^\n]*((\d+\s*(\(\d+\))?:)|(\s*\b(P|p)p\b\s*(:|\.)?))\s*\d+(?:[-;–]\d+)*[^\n]*',''],
    [r'[^\n]*[A-Z]+[a-z]*\s*[A-Z]*[a-z]*\.(\s*\d+?\s*(?:-\d+)*,?)?(\d+;)?\s*\d{4}[^\n]*',''],
    [r'[^\n]*([A-Z]|[a-z])￥[^\n]*',''],

    #去除带有网址的句子
    [r'[^\n\.]*(\()?\s*https?://[^\s]+\s*(\))?[^\n\.]*',''],
    [r'[^\n]*\b(?:(W|w)ww\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b[^\n]*', ''],
    [r'[^\n]*(D|d)oi:[^\n]*','']


        ]

context_pattern=[
    [r'¬\s*',''],
    [r'\(\s*\)','']


        ]
class speicalProces:
    def __init__(self):
        pass

    #去除左右侧栏
    def step1_drop_Sidebar(self,item):
        left_min, right_max = math.inf, 0
        text_boundary = []
        for dic in item["attr"]["raw_info"]:
            text_boundary.append(len(dic["raw_context"]))
        k = np.percentile(sorted(text_boundary), 60)

        for dic in item["attr"]["raw_info"]:
            if len(dic["raw_context"]) > k and dic["full_blocks"][2] > right_max:
                right_max = dic["full_blocks"][2]
                # left_min = dic["full_blocks"][0]
                print(right_max)
                # print(left_min)
            if len(dic["raw_context"]) > k and dic["full_blocks"][0] < left_min:
                left_min = dic["full_blocks"][0]

        for dic in item["attr"]["raw_info"]:
            if dic["full_blocks"][2] > right_max or dic["full_blocks"][0] < left_min:
                for dic_text in dic["raw_context"]:
                    item["text"] = re.sub(dic_text["text"], "", item["text"])
                    item["text"] = re.sub(dic_text["text"].strip("-"), "", item["text"])
        return item

    #去除页脚
    def step2_drop_Pagefooter(self,item):
        down_max = 0
        text_boundary = []

        for dic in item["attr"]["raw_info"]:
            text_boundary.append(len(dic["raw_context"]))
        k = np.percentile(sorted(text_boundary), 60)

        for dic in item["attr"]["raw_info"]:
            if len(dic["raw_context"]) > k and dic["full_blocks"][3] > down_max:
                down_max = dic["full_blocks"][3]

        for dic in item["attr"]["raw_info"]:
            if dic["full_blocks"][3] > down_max:
                for dic_text in dic["raw_context"]:
                    item["text"] = re.sub(dic_text["text"], "", item["text"])
                    item["text"] = re.sub(dic_text["text"].strip("-"), "", item["text"])
        return item



def clean_text(context, lang):
    split_token = "\n\n\n"

    if lang == 'en':
        pattern_list = pattern_list_en

    result = []
    sp = speicalProces()
    try:
        context=sp.step1_drop_Sidebar(context)
    except Exception as e:
        pass
    try:
        context=sp.step2_drop_Pagefooter(context)
    except Exception as e:
        pass

    context = context["text"]

    for item in context.split(split_token):
        # print(item)
        item = item.strip(split_token).strip()
        item = re.sub("\n\n","￥",item)

        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)
            item = item.strip()
        for pattern_item in context_pattern:
            item = re.sub(pattern_item[0], pattern_item[1], item)
        item = re.sub("￥","\n\n",item)

        result.append(item)
    context = split_token.join(result)
    return context


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    #
    return context

fw = open("../../../../full_data/medical_stage4_surya/medical_stage4_surya_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/medical_stage4_surya/drop_o_imgbox/medical_stage4_surya_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())

        context=item
        # lang = item["lang"]
        context = clean_text(context, "en")
        context = post_process(context)
        print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")

