# coding:utf-8
from common_re import clean_pattern
import json
from tqdm import tqdm
import re

pattern_list_en = [
    [r'([\u4e00-\u9fff])', r'删除17：<u>\1</u>'],# 汉字删除
    [r'(?:\n|^)((?:©.*\d{4}\n*)(?:.*(?:https?:\/\/(?:www\.)?|www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?))',r'删除1：<u>\1</u>'],#版权介绍
    [r'(?:\n|^)((.*(?:https?:\/\/(?:www\.)?|www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\n*)(©.*\d{4}))',r'删除1：<u>\1</u>'],

    [r'(?:\n|^)((?:.*class="ContactIcon">.*\n+)(?:.*\n)*?)(#* *Keywords|#* *Abstract|.*\n-+)',r'删除2：<u>\1</u>\n\2'],

    [r'(?:[^\n])(\*\*Fig(?:ures?|\.) ?\d+[.-]\d+[^\n*]*\*+)',r'删除3：<u>\1</u>'],
    [r'(?:\n|^)(\**Fig(?:ures?|\.) ?[0-9A-Z]+([.-]\d+)*[:：]?(?:\n+(?:[^\n ]{1,} ){3,}[^\n ]{2,}[^.?!]|.*))',r'删除3：<u>\1</u>'],#图
    [r'(?:\n)(Table [0-9.]+ \. .*\n+)(\n<sup>(<em>)?[a-z ]+(<\/em>)?<\/sup>.*\n)+',r'删除4：<u>\1</u>'],#表
    [r'(?:\n|^)(Table \d+[-–.]\d+ • .*)',r'删除4：<u>\1</u>'],

    [r'(\n|[^\d]\.|\?|!|\))( *[0-9:]+)(?:\n)',r'\1删除5：<u>\2</u>'],#单行数字
    [r'([_*]*This page intentionally left blank *(?:\d+|to match pagination of print book)?[_*]*)',r'删除6：<u>\1</u>'],
    [r'([0-9 ]+ Cases in[^\n.]*)(?:\n)',r'删除7：<u>\1</u>'],
    [r'(￾|◻|)',r'删除8：<u>\1</u>'],#特殊符号
    [r'((?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?)',r'删除9：<u>\1</u>'],#需要补充
    [r'(\\?[(（[][^\d\n][^()（）\[\]\n%=]+\d{4}[^()（）\[\]\n%= ]{0,2} *\\?[)）\]])',r'删除10：<u>\1</u>'],#（人物+年份）
    [r'(?:\n|^)(By [A-Z].*[^\n.])',r'删除11：<u>\1</u>'],#作者介绍
    [r'(?:\n|^)((?:Key Points[0-9]+\n+)(?:Case [0-9]+:.*)?)',r'删除12：<u>\1</u>'],#空标题
    [r'(?:\n|^)([*| ]*CASE CORRELATES[*| ]*\n*[*| -]*\n*[*| -●·]*See.*\n{0,2}[| -]*)',r'删除13：<u>\1</u>'],#案例例子删除
    [r'(?:\n|^)([A-Z]{1,2})(?:\n)',r'删除14：<u>\1</u>'],#单行的单独字母
    # [r'[^\n*#][^\n*#](\\?[\[［(] *[0-9０-９ ]{1,3}(?:[-—–－,，、][0-9０-９ ]+)*\\?[)］\]])',r'删除15：<u>\1</u>'],#序号
    [r'(?:\n|^)(Recommended Reading\n*(?:.*\n*)*)(?:\n|$)',r'删除16：<u>\1</u>'],#推荐阅读删除
    #个例
    [r'(?:\n|^)(> Courtesy of Dr. Mae Melvin, Centers for Disease Control and Prevention.|> Reproduced, with permission, from USMLERx.com.|FAITH, VALUES AND CULTURE|Faith, Values and Culture|_Kimberly L. DiMaria_|_Children’s Hospital Colorado, Aurora, CO, USA_)',r'删除个例：<u>\1</u>'],
    [r'(?:\n|^)(\*\*CCFC\d{4}\*\*)',r'删除18：<u>\1</u>'],
    [r'([a-zA-Z，,0-9’:：;(] ?)(\n+)([a-z0-9‘)][^.][^.])',r'\1 删除换行 \3'],



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
                    # print(pattern_item)
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




fw = open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\reclean1_medical_case_handled.jsonl", "a", encoding="utf-8")
# with open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\test.jsonl", "r", encoding="utf-8") as fs:
with open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\medical_case_handled_preformat.jsonl", "r",encoding="utf-8") as fs:

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

