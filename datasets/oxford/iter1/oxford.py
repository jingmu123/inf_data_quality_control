from common_re import clean_pattern
import json
from tqdm import tqdm
import re

pattern_list = [
    # [r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?)\s?\d+[\*#]{0,4})',r'删除1:<u>\1</u>'],     # 删除单行一直Figure 1
    [r'(^Open in new tab Download slide.*)',r''],       # 单行只有一个Open in new tab Download slide
]

pattern_page_ending = [
    r'^ACKNOWLEDGMENT(S)?',
    r'^ACKNOWLEDGEMENT(S)?(\n|$)',    # 单行只有一个ACKNOWLEDGEMENTS以下的需要删除
    r'^AVAILABILITY OF DATA AND MATERIAL(\n|$)',  # 单行AVAILABILITY OF DATA AND MATERIAL全为大写
    r'^CONFLICT OF INTEREST STATEMENT',   # 单行利益冲突CONFLICT OF INTEREST STATEMENT 全为大写
    r'^This is a correction' # 这是更正...  这一页都没用
]

pattern_more_line_feed = [
    [r'^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table)\s?\d+[\*#]{0,4}']
]
class speicalProces:
    def __init__(self):
        pass
    def step0_common_clean(self,context,cp,lang):
        result = []

        ending_starts = cp.ending_starts()
        combined_ending_startsss = '|'.join(ending_starts)
        context = cp.delete_page_ending(context, combined_ending_startsss)
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


def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()
    context = context.split(split_token)
    context = sp.step0_common_clean(context,cp,lang)
    new_context = []
    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)
        new_context.append(item)
    # 合并所有正则模式，用 | 连接
    combined_pattern = '|'.join(pattern_page_ending)
    new_context = cp.delete_page_ending(new_context,combined_pattern)
    new_context = cp.more_line_feed(new_context, pattern_more_line_feed)

    i = 0
    while i < len(new_context):
        if re.search(r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?)\s?\d+[\*#]{0,4})',new_context[i]):
            new_context[i] = re.sub(r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?)\s?\d+.*)',r'删除1:<u>\1</u>',new_context[i])
        print(new_context[i])
        i += 1


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




fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_oxford.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\oxford_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "d7862d6c-cf32-428e-9ffd-4abcfab29c8e":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0',r' ',context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")

