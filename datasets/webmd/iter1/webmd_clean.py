import json
import os
import re
import random

import jieba
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm




import json
import os
import re
import random

import jieba
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"
pattern_list = [
    [r'(^In (the US|Canada).*)',r'删除1:<u>\1</u>'],       # 规定格式 In (the US|Canada) ... call ...
    [r'(US residents can call their local poison control center at 1-800-222-1222. Canada residents can call a provincial poison control center.)',r'删除2:<u>\1</u>'],
    [r'(^See also.*)',r'删除3:<u>\1</u>'],    # 另见...
    [r'(^... Show More.*)',r'删除4:<u>\1</u>'],

    [r'^\b(\w+(\s\w+)?)\s+(\1)\b',r'\1删除5:<u>\3</u>'],   # 解决句首出现的单词重复的问题


]



class speicalProces:
    def __init__(self):
        pass


    def step4_rm_kongge(self, context):
        context = context.lstrip().rstrip()
        content = context.split(" ")
        first_content = content[0]
        last_content = " ".join(content[1:])
        final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', last_content)
        # 多执行一次，弥补正则边界重叠问题；
        final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', final_content)
        if len(final_content) == 0:
            return first_content

        merge_piece = first_content + final_content.lstrip()[0]

        split_word = list(jieba.cut(merge_piece, cut_all=False))
        if len(split_word[-1]) > 1:
            return first_content + final_content
        return first_content + " " + final_content

def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    # 分解处理
    result = []
    sp = speicalProces()
    context = context.split(split_token)
    print(context)
    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)
        if lang == "zh":
            item = sp.step4_rm_kongge(item)
        result.append(item)
    for item in result:
        print(item)

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
    # 对多标点进行替换
    context = re.sub(r'[。，](\s?[。，：；]){1,5}',r'。',context)
    context = re.sub(r'([,\.?])(\s?[?,\.]){1,5}',r'\1',context)
    return context



fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_webmd_preformat.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\webmd_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "bf588b27-d47d-4f2e-8a97-80d2fa7521e8":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
