from common_re import clean_pattern
import json
from tqdm import tqdm
import re


pattern_list = [
    [r'(^[\*#]{0,4}图\s?\d+.*)',r'删除1:<u>\1</u>'],
    [r'(（\s{0,}）)',r'删除2:<u>\1</u>'], # 空括号里面什么都没有
    [r'(（详见[^（）]*）)',r'删除3:<u>\1</u>'],   # 详见...
    [r'(^(视频).*)',r'删除4:<u>\1</u>'],  # 单行只有一个视频
    [r'(（请扫描文章首页左下角二维码）)',r''],
    [r'本病例选自.*',r''],
    [r'([，。]见(图|表)\d+[^，。]*)',r'删除5:<u>\1</u>'],   # 见图/表1...
    [r'(（[^（）]*视频[^（）]*）)',r'删除6:<u>\1</u>'],    # 带有（）的...视频
]

pattern_page_ending = [

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
                if index + 1 < len(context) and re.search(r'^[\*#]{0,4}(图|表)\s?\d+[\*#]{0,4}$', stripped_item):
                    # 合并到下一个 item
                    context[index] = item.rstrip() + "|删除段之间换行|" + context[index + 1].lstrip().lstrip()
                    # 删除下一个 item
                    del context[index + 1]
                    # 不增加 index, 继续检查当前索引位置的元素
                    index = index - 1
                    continue
            index += 1
        return context
    def step2_repeated_paragraph(self,context):   # 删除掉重复的表叙述
        for index,item in enumerate(context):
            if re.search(r'^[\*#]{0,4}表\s?\d+',item.strip()):
                if item.strip() == context[index+1].strip():
                    del context[index+1]
        return context
def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()
    context = context.split(split_token)
    if len(context) < 3:
        return ""
    result = sp.step0_common_clean(context,cp,lang)
    context = sp.step1_morelinefeed(result)
    context = sp.step2_repeated_paragraph(context)
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
        new_context = cp.delete_page_ending(new_context, ending)
    for index,item in enumerate(new_context):
        print(index,item)

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




fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_cmcr.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\cmcr_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "0103327b-63de-4496-b426-2bda1b1e26d9":
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

