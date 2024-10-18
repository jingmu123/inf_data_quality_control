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
# pattern_list = [
#     [r'(^In (the US|Canada).*)',r'删除1:<u>\1</u>'],       # 规定格式 In (the US|Canada) ... call ...
#     [r'(US residents can call their local poison control center at 1-800-222-1222. Canada residents can call a provincial poison control center.)',r'删除2:<u>\1</u>'],
#     [r'(^See also.*)',r'删除3:<u>\1</u>'],    # 另见...
#     [r'(^... Show More.*)',r'删除4:<u>\1</u>'],
#
#     [r'^\b(\w+(\s\w+)?)\s+(\1)\b',r'\1删除5:<u>\3</u>'],   # 解决句首出现的单词重复的问题
# ]

pattern_list = [
    [r'(^In (the US|Canada).*)',r''],       # 规定格式 In (the US|Canada) ... call ...
    [r'(US residents can call their local poison control center at 1-800-222-1222. Canada residents can call a provincial poison control center.)',r''],
    [r'(^See also.*)',r''],    # 另见...
    [r'(^... Show More.*)',r''],
    [r'^\b(\w+(\s\w+)?)\s+(\1)\b',r'\1'],   # 解决句首出现的单词重复的问题

    [r'(\(\s?[Ss]ee[^\(\)]*(\)|$))',r''],    # 带有括号的(See ...)
    [r'(^Contact the health care professional for medical advice about side effects.*)',r''],   # 请与医疗保健专业人员联系，致电...
    [r'(^Call your doctor for medical advice about side effects.*)',r''],
    [r'(.*The National Abortion Federation.*)',r''],  # 只有一条特殊处理
    [r'(You can find more information at.*)',r''],    # 只有一条特殊处理
    [r'(^(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news).*)',r''],


]

class speicalProces:
    def __init__(self):
        pass
    def step1_repeat_delete(self,context):
        warnings1 = False
        warnings2 = False
        warnings_index = []
        for index,item in enumerate(context):
            if re.search(r'^(\*+)?Warnings:(\*)?',item) and index == 0:
                warnings1 = True
                warnings_index.append(index)
            if re.search(r'^(\*+)?Warnings:(\*)?',item) and index > 0:
                warnings2 = True
                warnings_index.append(index)

        if warnings1 and warnings2 and len(warnings_index) >= 2:
            start_index = warnings_index[0]
            end_index = warnings_index[-1]
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index):
                context[i] = "删除重复:<u>{}</u>".format(context[i])
                context[i] = ""
        return context

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
    context = sp.step1_repeat_delete(context)
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



fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean2_webmd_preformat.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\webmd_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "6dfe8f44-c020-4f75-8b6e-a8dd576659a7":
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
