import json
import os
import re
from tqdm import tqdm

def clean_text(context):
    split_token = "\n\n"

    result = []

    for item in context.split(split_token):
        item = re.sub(r"\n"," ",item)
        result.append(item)
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
    return context


fw = open("../../../../full_data/mimic_iv_radiology/mimic_iv_radiology_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/mimic_iv_radiology/mimic_iv_radiology_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")





