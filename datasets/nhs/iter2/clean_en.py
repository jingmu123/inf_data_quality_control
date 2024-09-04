from common_re import clean_pattern
import json
from tqdm import tqdm
import re

pattern_list_en = [
    [r'(?:\n|^)((?:\* *)?(?:Next review due|Page last reviewed|Previous|Next|Media last reviewed|Media review due|iewed) *[:：].*)',r'删除1：<u>\1</u>'],#日期
    # [r'((?:.*\n=+\n+)(?:.*how to (?:use|take) (?:it|them)\.)\n+(?:\* *.*\n)+\n+(?:Related conditions\n-+)\n+(?:\* *.*\n)+\n+(?:Useful resources\n-+)\n+(?:(?:\* *.*(?:\n|$))|(?: {2,}.*(?:\n|$)))+)',r'删除2：<u>\1</u>'],
    # [r'((?:.*\n=+\n+).*\n+(?:\* *.*\n)+\n+(?:Related information\n-+)\n+(?:\*? {2,}.*(?:\n|$))+)',r'删除2：<u>\1</u>'],

    [r'(?:\n|^)((?:#* *Video[:：].*\n-*\n)(?:.*\n*)*?)(?:(.*\n-+)|$)',r'删除3：<u>\1</u>\n\2'],#视频内容
    [r'(?:\n|^)(#* *(?:About this video[:：]?\n-*\n|Common questions[:：]?\n-*\n|Help us improve our website[:：]?\n-*\n|More information[:：]?\n-*\n)(?:.*\n*)*?)(?:(.*\n-+)|$)',r'删除4：<u>\1</u>\n\2'],#视频内容介绍、问题介绍、帮助我们改进网站
    [r'(?:\n|^)(Information: *\n+(?:Find out more about.*|You can report any.*\n+Visit Yellow Card.*|(Watch.*\n*)+))',r'删除5：<u>\1</u>'],#特例的信息介绍.9.04 观看视频类
    [r'(?:\n|^)((?:Information:\n+)?\**#* *(?:Find out more[:：]?|Further information[:：]?|Want to know more\?) *\**\n-*\n+(?:(?:\* *.*\n{1,2})|(?:.*[:：].*\n{1,2}))+)',r'删除6：<u>\1</u>\n'],#固定格式的信息介绍
    [r'(?:.|\n|^)((?:Read.{1,5}more|Find(?: out)?.{1,5}more|[^.]*?(?:GOV\.UK)? has more) (?:information (?:about)?|about|from).*)',r'删除7：<u>\1</u>'],#单行：阅读更多获取信息
    [r'(?:\n)([Ss]ee[:：]? [^\n()（）]*(?:[Aa]ppendix|[Ff]igures?|[Tt]able|for more information|[Pp]ictures?|guide|guidance).*)',r'删除8：<u>\1</u>'],#单行：参见内容
    [r'(?:\n|^)(Credit:\n(\n.*(?:\n| )*(?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)? *)+)',r'删除9：<u>\1</u>'],#信贷类
    [r'(?:\n|^)((?:Contents *|On this page *)\n-+(\n+\d{1,2}\..*)+)',r'删除10：<u>\1</u>'],#目录类
    [r'(?:\n|^)((?:More in.*\n-+| *Related conditions *\n-+| *Useful resources *\n-+|You can find more.*[:：]|Here is an image.*|Related information *\n-+)\n+(?:(?:\* *.*(?:\n|$))|(?: {2,}.*(?:\n|$)))+)',r'删除11：<u>\1</u>'],#更多内容、资源类
    [r'(?:\n|^)(Read about the symptoms of.*|Visit .*(?:website|(?:more|further) information.|read more|\.org|\.com|\.cn|site).*)',r'删除12：<u>\1</u>'],#了解病症与游览类
    [r'(?:\n|^)(\**(?:Email|Phone|Tel|Website|Contact details|Fax|Updated)[:：].*)',r'删除13：<u>\1</u>'],#联系方式与更新日期
    [r'(?:\n|^)((?:<a>Community content from HealthUnlocked<\/a>|Long description, image \d{1,2}\.))',r'删除14：<u>\1</u>'],


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
    def step1_rm_longtext(self,context):
        result_1=re.findall(r'((Where to find help and support\n-+)(\n*[^#]*\n)((### .*\n+.*\n+)(\* *.*\n)+\n+){2,}(\n*[^#]*(?:\n|$)))',context)


        r1=re.findall(r'((?:.*how to (use|take) (it|them)\.)\n+(?:\*? {2,}.*(?:\n|$))+)',context)
        r2=re.findall(r'((?:Related conditions\n-+)\n+(?:\*? {2,}.*(?:\n|$))+)',context)
        r3=re.findall(r'((?:Useful resources\n-+)\n+(?:\*? {2,}.*(?:\n|$))+)', context)
        result_2=len(r1)+len(r2)+len(r3)

        r4=re.findall(r'(?:\n|^)((?:.{3,15} is .*)\n+(?:\*? {2,}.*(?:\n|$))+)',context)
        r5=re.findall(r'((?:Related information\n-+)\n+(?:\*? {2,}.*(?:\n|$))+)',context)
        result_3=len(r4)+len(r5)

        if len(result_1)>0 or result_2==3 or result_3==2:
            return '整页删除\n'+context
        else:
            return context



def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()
    context=sp.step1_rm_longtext(context)
    pattern_list = pattern_list_en
    for pattern_item in pattern_list:
        # print(pattern_item)
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




fw = open(r"C:\Users\Administrator\PycharmProjects\untitled\nhs\reclean2_nhs.jsonl", "a", encoding="utf-8")
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

