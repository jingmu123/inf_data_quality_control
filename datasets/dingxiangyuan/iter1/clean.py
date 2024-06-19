import json
import os
import re
from tqdm import tqdm

pattern_list_zh = [
                   [r'\\|`|^',''],# 匹配文本中多余符号\、`、^
                   ['图片来源：.*',''],#图片来源：visualdx
                   [r'<br/><br/>',''],
                   ['(<sup>)?(\\\\)?(\\[|［)(\\d+|(\\d+[,.、~～-]\\s*\\d+.*))(\\\\)?(\\]|］)(</sup>)?',''],#<sup>[1]</sup>
                   ['<sup>',''],
                   ['【.*日期.*】',''],#【 核准日期 】【 修改日期 】
                   [r'\d{4}-\d{2}-\d{2}',''],#2008-07-23
                   [r'（?图\s*\d+:.*?）?','']#图 2：医疗器械）
                     ]

class speicalProces:
    def __init__(self):
        pass

    #去除 ...登录 问题
    def step1_drop_login(self,content):
        split_token = "\n\n"
        if split_token not in context:
            split_token = "\n"
        pattern=r'录登\s*\.\.\.(.*?)[。，,、：:；(]'
        text=content.strip(' ').split(split_token)
        for i in range(len(text)):
            text[i]=re.sub(pattern,'。',text[i][::-1])[::-1]
        for i in range(len(text)):
            pattern1 = r'[\u4e00-\u9fa5]/[\u4e00-\u9fa5]' #删除中文文本中多余的/，如医/院，但是不删除单位里的/，如kg/m2
            sq_list = re.findall(pattern1, text[i])
            for j in sq_list:
                if j in text[i]:
                    text[i] = text[i].replace(j, j.replace('/', ''))
        text=split_token.join(text)
        return text

    #去除空格问题
    def step2_strip(self, context):
        split_token = "\n\n"
        if split_token not in context:
            split_token = "\n"
        new_context = []
        context = context.split(split_token)
        for item in context:
            item = item.lstrip().rstrip()
            context_s=item.split("\n")
            for i in range(len(context_s)):
                context_s[i] = context_s[i].lstrip().rstrip()
            item="\n".join(context_s)
            new_context.append(item)
        return split_token.join(new_context)


def clean_text(context):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    result = []
    sp = speicalProces()
    context=sp.step1_drop_login(context)
    for item in context.split(split_token):
        item = item.strip(split_token)
        for pattern_item in pattern_list_zh:
            item = re.sub(pattern_item[0], pattern_item[1], item)
        result.append(item)

    context = split_token.join(result)
    return context


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # context = re.sub('\n\n-*', "", context)
    context = re.sub(r'\n-{3,}\n', "", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context


fw = open("../../../../full_data/dingxiangyuan/dingxiangyuan_clean.jsonl.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/dingxiangyuan/dingxiangyuan_preformat.jsonl.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        sp = speicalProces()
        context = sp.step2_strip(context)
        context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")





