from common_re import clean_pattern
import json
from tqdm import tqdm
import re

pattern_list_en = [
    [r'(?:\n|^)((?:\* *)?(?:Next review due|Page last reviewed|Previous|Next|Media last reviewed|Media review due|iewed) *[:：].*)',r'删除1：<u>\1</u>'],#日期
    [r'((?:.*\n=+\n+)(?:.*how to (?:use|take) it\.)\n+(?:\* *.*\n)+\n+(?:Related conditions\n-+)\n+(?:\* *.*\n)+\n+(?:Useful resources\n-+)\n+(?:(?:\* *.*(?:\n|$))|(?: {2,}.*(?:\n|$)))+)',r'删除2：<u>\1</u>'],
    [r'(?:\n|^)((?:#* *Video[:：].*\n-*\n)(?:.*\n*)*?)(?:(.*\n-+)|$)',r'删除3：<u>\1</u>\n\2'],#视频内容
    [r'(?:\n|^)((?:About this video\n-*\n|Common questions\n-*\n|Help us improve our website\n-*\n)(?:.*\n*)*?)(?:(.*\n-+)|$)',r'删除4：<u>\1</u>\n\2'],#视频内容介绍、问题介绍、帮助我们改进网站
    [r'(?:\n|^)(Information: *\n+(?:Find out more about.*|You can report any.*\n+Visit Yellow Card.*))',r'删除5：<u>\1</u>'],#特例的信息介绍
    [r'(?:\n|^)((?:Information:\n+)?\**#* *(?:Find out more[:：]|Further information[:：]?|Want to know more\?) *\**\n-*\n+(?:(?:\* *.*\n{1,2})|(?:.*[:：].*\n{1,2}))+)',r'删除6：<u>\1</u>\n'],#固定格式的信息介绍
    [r'(?:\n|^|.)((?:Read.{1,5}more|Find(?: out)?.{1,5}more|.*has more) (?:information (about)?|about|from).*)',r'删除7：<u>\1</u>'],#单行：阅读更多获取信息
    [r'(?:\n)([Ss]ee[:：]? [^\n()（）]*(?:[Aa]ppendix|[Ff]igures?|[Tt]able|for more information|[Pp]ictures?|guide).*)',r'删除8：<u>\1</u>'],#单行：参见内容
    [r'(?:\n|^)(Credit:\n(\n.*(?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?)+)',r'删除9：<u>\1</u>'],#信贷类
    [r'(?:\n|^)(Contents *\n-+(\n+\d\..*)+)',r'删除10：<u>\1</u>'],#目录类
    [r'(?:\n|^)((?:More in.*\n-+| *Related conditions *\n-+| *Useful resources *\n-+|You can find more.*[:：])\n+(?:(?:\* *.*(?:\n|$))|(?: {2,}.*(?:\n|$)))+)',r'删除11：<u>\1</u>'],#更多内容、资源类

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


def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()

    pattern_list = pattern_list_en
    for pattern_item in pattern_list:
        context = re.sub(pattern_item[0], pattern_item[1], context)


    context = context.split(split_token)
    result = sp.step0_common_clean(context,cp,lang)
    # for item in result:
    #     print(item)

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




fw = open(r"C:\Users\Administrator\PycharmProjects\untitled\nhs\reclean1_nhs.jsonl", "a", encoding="utf-8")
with open(r"C:\Users\Administrator\PycharmProjects\untitled\nhs\nhs_preformat.jsonl", "r", encoding="utf-8") as fs:
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
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")

