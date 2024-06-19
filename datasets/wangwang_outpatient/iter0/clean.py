import json
import re
from tqdm import tqdm

pattern_list_zh = [
                   ['(?<=[，、。])[，、。]',""],
                   ['[^。]*$',""],
                   [r'([。]+\s?)\1*',"。"],
                   ]

pattern_list_en = [
                   [r'([。]+\s?)\1*',"."],
                   [r"\.\s?,\s?", "."],
                   ]


context_pattern = [
    ["。，", "。"],
]


class speicalProces:
    def __init__(self):
        self.pattern_ngram_en = r'([A-Za-z]+)\s+\1(\s+\1)*'
        self.pattern_ngram_zh = r'\b(\w+)\s+\1\b(\s+\1)*'

    def step1_mv_ngram_repeat(self,content, pattern_ngram, lang):
        part = re.findall(pattern_ngram, content, flags=re.IGNORECASE)
        if not part:
            return content
        if lang == "zh":
            for p in part:
                content = re.sub(rf'({p[0]})\s+\1(\s+\1)*', p[0], content, flags=re.IGNORECASE)
                # content=re.sub('通常需要精神病转诊。|AAABBBCCC|<><><>|ABCBCABAC|又见 脊髓病变疾病概述.）...|','',content)
        if lang == "en":
            for p in part:
                content = re.sub(rf'\b({p[0]})\s+\1\b(\s+\1)*', p[0], content, flags=re.IGNORECASE)
                # item=re.sub('© Springer Science+Business Media|Did You Know...','',item)
        return content

    def step2_rm_last_paragh(self,text,lang):
        if lang != "zh":
            return text
        context = text.split("。")
        if len(context[-1]) < 5:
            context = context[:-1]
            context[-1] = context[-1] + "。"
        new_context = []
        for item in context:
            if len(item) > 4:
                new_context.append(item)
        return "。".join(new_context)

    def step3_rm_special_char(self,text):
        if text[-2:] == "了解":
            return text[:-2]
        return text


def clean_text(context, lang):
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    if lang == "zh":
        pattern_list, pattern_ngram = pattern_list_zh, sp.pattern_ngram_zh
    else:
        pattern_list, pattern_ngram = pattern_list_en, sp.pattern_ngram_en

    # 分解处理
    result = []

    for item in context.split(split_token):
        # 1.正则
        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)

        # 2.替换 固定内容（非泛化）
        for replace_item in context_pattern:
            item = re.sub(replace_item[1], replace_item[2], item)

    # 整合
    context = split_token.join(result)

    # special_process：
    context = sp.step1_mv_ngram_repeat(context, pattern_ngram, lang)
    context = sp.step2_rm_last_paragh(context)
    context = sp.step3_rm_special_char(context)

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
        # if need
        lang = item["lang"]
        context = clean_text(context, lang)
        clean_text = post_process(context)
        item["text"] = clean_text
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")