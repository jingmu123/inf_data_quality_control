# coding:utf-8
# https://github.com/shibing624/pycorrector?tab=readme-ov-file
import json
import re
from collections import defaultdict

from tqdm import tqdm
import sys

import transformers
sys.path.append("../../../")

import spacy
import jieba

# import torch.nn.functional as F
# from transformers import AutoModelForSequenceClassification, AutoTokenizer
# f7f8c3e1-218e-4792-92e4-5b096bfaa2c0

pattern_list_en = [
    [r'(\\?[(（[][^\d\n][^()（）\[\]\n%=]+\d{4}[^()（）\[\]\n%= ]{0,2} *\\?[)）\]])',r'删除1：<u>\1</u>'],#( WHO 2011 ),人物+年份  ([(（][^()（）\n]*\d{4}[^()（）\n]*[)）])
    [r'(?<=\n)([# ]+(?:Search methods for identification of studies|Electronic searches) *(?:.*\n?.*)*)',r'删除2：<u>\1</u>'],#Search methods for...及一下内容删除
    [r'(\n*(?:Reason for withdrawal from publication) *(?:.*\n?.*)*)',r'整页删除：<u>\1</u>'],
    [r'[^\n*#][^\n*#](\\?[\[［(] *[0-9０-９ ]{1,3}(?:[-—–－,，、][0-9０-９ ]+)*\\?[)］\]])',r'删除3：<u>\1</u>'],#序号删除
    [r'(?:\n|^)(\** *(?:Visual summary|See more on using PICO in the Cochrane Handbook .|Unlock the full (?:Protocol|review)|Plain language summary|Open in (?:table|figure) viewer) *)(?=\n|$)',r'删除4：<u>\1</u>'],#一些个例
    [r'(?:\n)((?:Plain language summary *\n)?-+\n*available in *\n*(?:\*.*\n)+)',r'删除5：<u>\1</u>'],#语言总结
    [r'(?:\n)(PICOs\n-+\n*)(#+ *PICOs)',r'删除6：<u>\1</u>\n\2'],#重复标题
    [r'([(（\n] *(?:Appendix|Figure|Table|(?:\* ?)+)[ 0-9.]*[\n）)])|([(（] *(?:[Ss]ee[^\n()（）]*)[ 0-9.]*[）)])',r'删除7：<u>\1\2</u>'],

    [r'(\\?[(（【[][^（）()[\]\n]*(?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?[^（）()[\]\n]*[)）】\]])',r'删除8：<u>\1</u>'],#带括号链接
    [r'[^()（）【】\[\]] ((?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?)',r'删除8：<u>\1</u>'],#删除文中的链接

    [r'(?:\n|\.|；|;)([^.\n()（）]{0,10}[Ss]ee[:：]? [^\n()（）]*(?:[Aa]ppendix|[Ff]igures?|[Tt]able|module|point).*?(?:\.|\n)(?= |\n))',r'删除9：<u>\1</u>'],
    [r'(?<=\n)(The evidence in this review,.*carried out.*is up[‐ ]to[‐ ]date.*\d{4}\.)',r'删除10：<u>\1</u>'],
    [r'(?:\n)((?:(?:\**How up[‐ ]to[‐ ]date (?:was|is).*)|(?:\**Search date\** *))(?:\n*.*to \d{1,2}.*\d{4}.*))',r'删除11：<u>\1</u>'],
    [r'(?:\n)(\**Information\** *\n*-+(.*\n*.*)*)',r'删除12：<u>\1</u>'],
    [r'(?:\n|^)(.*Copyright.{0,5} \d{4} .*)',r'删除13：<u>\1</u>'],#版权声明删除
    [r'(?:\n|^)(\** *This.*updated?.* \d{4}\.?)(?=\n)',r'删除14：<u>\1</u>'],#更新声明删除
    [r'(?:\n|^)(From *(?: [^\n ]* \d{4} *[;.])+)',r'删除15：<u>\1</u>'],#摘自内容删除


]

context_pattern = [
    [r"[。，?!,]([。，?!,])", r"\1"],

]


class speicalProces:
    def __init__(self):
        pass



def clean_text(context, lang, sp):
    # print("-"*10)
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    pattern_list = pattern_list_en
    context = re.sub(r'\xa0', r' ', context)

    for pattern_item in pattern_list:
        # context = context.lstrip(" ").rstrip(" ")
        context = re.sub(pattern_item[0], pattern_item[1], context)
    # context=sp.step1_rm_reference(context)
    # 分解处理
    # result = []
    # for idx, item in enumerate(context.split(split_token)):
    #     print(item)
    #
    #
    #     for pattern_item in pattern_list:
    #         item = item.lstrip(" ").rstrip(" ")
    #         item = re.sub(pattern_item[0], pattern_item[1], item)
    #
    #     for replace_item in context_pattern:
    #         item = re.sub(replace_item[0], replace_item[1], item)
    #     print(item)
    #     result.append(item)

    # 整合

    # print(context)
    # context = split_token.join(result)
    # print(context)

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
    return context


def process_line(items, sp):
    try:
        item = json.loads(items.strip())
        # item=sp.step1_drop_Pagefooter(item)

        context = item["text"]
        lang = item["lang"]

        context = clean_text(context, lang, sp)
        context = post_process(context)
        item["text"] = context
    except:
        print("error")
        exit(0)
    item = json.dumps(item, ensure_ascii=False)
    return item

sp=speicalProces()
fw = open(r'C:\Users\Administrator\PycharmProjects\untitled\cochrane\reclean2_cochrane_label.jsonl', 'a', encoding='utf-8')
# with open(r'C:\Users\Administrator\PycharmProjects\untitled\other-medlive_zh_preformat\other-medlive_zh_preformat.jsonl', "r", encoding="utf-8") as file:
with open(r'C:\Users\Administrator\PycharmProjects\untitled\cochrane\cochrane_preformat.jsonl', "r", encoding="utf-8") as file:

    for item in tqdm(file.readlines()):

        item=process_line(item,sp)
        # with open(r'F:\zeroshots\reclean7_medicalpdfv2__preformat_zh.jsonl', 'a', encoding='utf-8') as f:
        fw.write(item+'\n')


