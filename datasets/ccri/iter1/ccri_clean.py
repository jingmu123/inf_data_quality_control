from common_re import clean_pattern
import json
from tqdm import tqdm
import re

pattern_list = [
    [r'(^[\*_\\]*(Correspondence：|OPEN ACCESS|E-mail：|Copyright).*)', r'删除1:<u>\1</u>'],
    [r'(^[#\*]{0,4}\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*)', r'删除2:<u>\1</u>'],  # 删除开头为Figure的描述
    [r'(^[\*_\\]*(([A-Z][a-z]+( \w+){0,2})[,，] ?){2,}([A-Z][a-z]+( \w+){0,2})[\*_\\]*.*)', r'删除3:<u>\1</u>'],
]

pattern_more_line_feed = [
    [r'\s?[^\.!?|]\s?[#\*_]+$', r'^[#\*_]+[a-z]'],        # 上一段非标点结尾，下一段小写开头
    [r'(The|A)\s?[#\*_]+$'],   #  上一段结尾是A或者The 下一段一定要连上
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

        end_pattern = [
            [r'(^[\*\s]*(Abstract|Background)[\*\s]*(\n|$))', 0],
            [r'(^[\*\s]*(Introduction)[\*\s]*(\n|$))', 0],
        ]
        for end in end_pattern:
            flag, context = cp.delete_page_start(context, end[0], end[1])
            if flag:
                break

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
    context = cp.more_line_feed(context, pattern_more_line_feed)
    result = sp.step0_common_clean(context,cp,lang)

    new_context = []
    for item in result:
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)
        new_context.append(item)

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




fw = open(r"C:/Program Files/lk/projects/pdf/accr/accr_preformat_clean1.jsonl", "w", encoding="utf-8")
with open(r"C:/Program Files/lk/projects/pdf/accr/accr_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "5a9815c6-c389-410a-884d-86bd79e6dc56":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0',r' ',context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context, "\n--------------------------------------------------")
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
fw.close()
