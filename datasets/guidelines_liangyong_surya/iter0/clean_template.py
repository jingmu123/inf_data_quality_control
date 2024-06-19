import json
import re
from tqdm import tqdm

# 规则必须以列表形式存储，分别是要替换的内容，以及替换成什么内容
pattern_list_zh = [
                   ['(?<=[，、。])[，、。]',""],
                   ['[^。]*$',""],
                   [r'([。]+\s?)\1*',"。"],
                ]
pattern_list_en = [
                   [r'([。]+\s?)\1*',"."],
                   [r"\.\s?,\s?", "."],
                ]

# 对于规则以外，无法泛化的内容放这里
context_pattern = [
    ["。，", "。"],
]


class speicalProces:
    def __init__(self):
        pass

    def step1_xxx(self,context):
        # todo: 如果需要特殊处理
        pass


def clean_text(context, lang):
    # 如果存在特殊处理，以类的方式整合，初始化类；
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    # 如果区分语种
    if lang == "zh":
        pattern_list, pattern_ngram = pattern_list_zh, sp.pattern_ngram_zh
    else:
        pattern_list, pattern_ngram = pattern_list_en, sp.pattern_ngram_en

    # 1. 分解处理
    result = []
    for item in context.split(split_token):
        # 1.正则
        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)

        # 2.替换 固定内容（非泛化）
        for replace_item in context_pattern:
            item = item.replace(replace_item[0], replace_item[1])
        result.append(item)


    # 2. 整合
    context = split_token.join(result)

    # 3. 特殊处理(if need)

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

fw = open("../../../../full_data/MSD/MSD_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/MSD/MSD_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        # if don't need lang
        # context = clean_text(context)
        # else: you need
        lang = item["lang"]
        context = clean_text(context, lang)

        clean_text = post_process(context)
        item["text"] = clean_text
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")