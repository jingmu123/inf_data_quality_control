from common_re import clean_pattern
import json
from tqdm import tqdm
import re

pattern_list = [
    [r'(^Full size.*)',r'删除1:<u>\1</u>'],     # Full size image/table 原文这里应该是一个图/表没识别出图形
    [r'([\*#]{0,4}Additional file.*)',r'删除2:<u>\1</u>'],   # 附加文件
    [r'(\([^\(\)]*(arrow|←|→)[^\(\)]\))',r''],      #  ...箭头 描述图里面不同颜色的箭头
    [r'(\([pP]\.?\d+[^\(\)]*\))',r'删除3:<u>\1</u>'],
    [r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table).*)',r'删除4:<u>\1</u>']  # 图表
]

pattern_page_ending = [
    [r'^Consents?(\n|$)'],    # 单行只有一个Consent以下的需要删除
    [r'^Availability of supporting data'],    # 数据可用性以下内容需要删
]

class speicalProces:
    def __init__(self):
        pass
    def step0_common_clean(self,context,cp,lang):
        result = []

        ending_starts = cp.ending_starts()
        for ending_start in ending_starts:
            start = ending_start[0]
            context = cp.delete_page_ending(context, start)

        pattern_en = cp.clean_pattern_en()
        pattern_zh = cp.clean_pattern_zh()
        for item in context:
            # 1.正则
            if lang == "en":
                for pattern_item in pattern_en:
                    src = pattern_item[0]
                    tgt = pattern_item[1]
                    item = re.sub(src, tgt, item)
            else:
                for pattern_item in pattern_zh:
                    src = pattern_item[0]
                    tgt = pattern_item[1]
                    item = re.sub(src, tgt, item)
            result.append(item)
        return result

    def step1_morelinefeed(self,context):
        for index,item in enumerate(context):
            if item.strip() == "":   # 去除某些段出现空字符串
                del context[index]
        index = 0
        while index < len(context):
            item = context[index]
            # 合并以小写字母或特定标点符号开头的段落
            stripped_item = item.strip()
            if index >= 0:
                if index + 1 < len(context) and re.search(r'^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE))s?\.?\s\d+[\*#]{0,4}$', stripped_item):
                    # 合并到下一个 item
                    context[index] = item.rstrip() + "|删除段之间换行|" + context[index + 1].lstrip().lstrip()
                    # 删除下一个 item
                    del context[index + 1]
                    # 不增加 index, 继续检查当前索引位置的元素
                    index = index - 1
                    continue
            index += 1
        return context

def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()
    context = context.split(split_token)


    result = sp.step0_common_clean(context,cp,lang)
    context = sp.step1_morelinefeed(result)
    new_context = []
    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)
        new_context.append(item)
    for ending_start in pattern_page_ending:
        ending = ending_start[0]
        new_context = cp.delete_page_ending(new_context,ending)
    for item in new_context:
        print(item)

    context = split_token.join(new_context)

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




fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_jmedical.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\jmedical_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "a6f6dd6d-67bf-4323-9175-fab10b402fcd":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        if re.search(r'^Correction',context):
            context = "本页删除\n" + context
        context = re.sub(r'\xa0',r' ',context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")

