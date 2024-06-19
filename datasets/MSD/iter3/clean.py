import json
import os
import re
# from langdetect import detect
# from langdetect import detect_langs
from tqdm import tqdm

pattern_list_zh = [
    [r'（?另见[^）]*.', ''],
    [r'看?法? 进行患者培训\s?', ''],
    [r'[^\。]*参考(文献)*.?doi: [^\s]+', ''],
    [r'[^\。]*参考(文献)?[^，。]*.\)?）?', ''],
    [r'[^。]*?(\.\.\. )?阅读更多[^。]*。[\)）]?', ''],
    [r'阅读更多[^一-龥]*', ''],
    [r'更多信息[^，。,\.]*.', ''],
    [r'www\.\w+\.\w+[^\s]*\s', ''],
    [r'会在这本.*点击此处', ''],
    [r'[（\(][^\)）]{0,10}(也可)?(另请)?(也)?(请)?(参|亦)(见|阅)(概述)?[^\.）\)。]*.[）\)]?', ''],
    [r'[^。]*参(见|阅)[^。]*', ''],
    [r'[^\.,]*\.\.\. Common.TooltipReadMore', ''],
    [r'(表格)?(Table)? \$\(document\).ready.*?(\} \}\); \} \}\);)', ''],
    [r'(\$\(document\))?.ready.*?console', ''],
    [r'请注意，本手册.*', ''],
    [r'\(又见 .*[^ ]概述{1,3}', ''],
    [r'\(s?S?ee[^\)]*.\.?', ''],
    [r'观看这些视频.*', ''],
    [r' ?\(?（?见表 ?[^。]*', ''],
    [r' ?（?\(?见图 ?[^。]*', ''],
    [r' ?（?\(?也见 ?[^。]*', ''],
    [r'[\(（ 也可同样]+见 ?[^。]*。?', ''],
    [r'[^一-龥-。]{10,1000}', ''],
    [r'(\s[^\s]{0,20})?(（其他[^）]*)?概要\s?）?', ''],
    [r'[^。]*((出版商[^。]*。)|(图[像片]经?由)|(这张照片))[^。]*。', ''],
    [r'[\(（\s]{1,5}?[^\s\(（。，]*(视频|概述)[\)）\.\s]{1,5}', ''],
    [r'表格[^.，。:：]*\s', ''],
    # 匹配文本中连续出现的逗号、顿号或句号
    [r'(?<=[，、。])[，、。]', ''],
    [r'[^。]*$', ''],
    [r'([。]+\s?)\1*', "。"],
    # 删除转义符
    [r'\\+',''],
    # 中文之间有空格，只捕获两边的中文
    [r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2']
]

pattern_list_en = [
    [r'(\(\s?s?S?ee[^\.]*)?\.?\(?[^\.]*[\.]{0,3} read more [^A-Z\.]*(\.\))?', ''],
    [r'[^\.]*?View Patient Education\s?', ''],
    [r'More Information The following.*', ''],
    [r'(表格)?(Table)? \$\(document\).ready.*?\} \}\); \} \}\);', ''],
    [r'(\$\(document\))?.ready.*?console', ''],
    [r'[^\.]*?[\.]{0,3}?\s?Common.TooltipReadMore[^\.]*\.?\)?', ''],
    [r'\(\s?[sS]?ee[^\)\.]*[\.\)]?\)?', ''],
    [r'[^\.]*r?R?eference(?:(?!r?R?eference).)*?(doi\s?(:|\.)\s?[^\s]*)(.{0,500}?doi\s?:\s?[^\s]*){0,10}', ''],
    [r'\.(\d+–\d+)*?.{0,150}(\.?(doi|DOI)\s?(:|\.)\s?[^\s]*)(.{0,500}?(doi|DOI)\s?(:|\.)\s?[^\s]*){0,5}', ''],
    [r'(?<=\.|”)(\d+\.)?(.{0,200}http[^\s]*){1,5}', ''],
    [r'[^\.]*© Elsevier Inc. All Rights Reserved.([^\.]*.){2}(.*\.?doi\s?:?\s?[^\s]*)?',''],
    # 多个小写后面是大写分开中间加.
    [r'([a-z]{2,})([A-Z])', r'\1\.\2'],
    # 结尾半句话删除
    [r'[^\.]*$',''],
    [r'^\.', ''],
    [r'\\+',''],
    [r'([。]+\s?)\1*', "."],
    [r"\.\s?,\s?", "."]
]

# todo: 中文空格
# clean_text = re.sub("\s+", "", clean_text)

context_pattern = [
    [r'通常需要精神病转诊。|AAABBBCCC|<><><>|ABCBCABAC|又见 脊髓病变疾病概述.）...|', ''],
    ['© Springer Science+Business Media|Did You Know...', ''],
    ["。，", "。"],
]

pattern_ngram_en = r'([A-Za-z]+)\s+\1(\s+\1)*'
pattern_ngram_zh = r'\b(\w+)\s+\1\b(\s+\1)*'
pattern_ngram_punc = r'([。]+\s?)\1*'


class speicalProces:
    def __init__(self):
        pass

    def step1_mv_ngram_repeat(self, content, pattern_ngram, lang):
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

    def step2_rm_last_paragh(self, text, lang):
        if lang != "zh": return text
        context = text.split("。")
        if len(context[-1]) < 5:
            context = context[:-1]
            context[-1] = context[-1] + "。"
        new_context = []
        for item in context:
            if len(item) > 4:
                new_context.append(item)
        return "。".join(new_context)

    def step3_rm_special_char(self, text):
        if text[-2:] == "了解":
            return text[:-2]
        return text


def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    if lang == "zh":
        pattern_list, pattern_ngram = pattern_list_zh, pattern_ngram_zh
    else:
        pattern_list, pattern_ngram = pattern_list_en, pattern_ngram_en

    # 分解处理
    result = []
    sp = speicalProces()
    for item in context.split(split_token):
        # 1.正则
        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)

        # 2.替换 固定内容（非泛化）
        for replace_item in context_pattern:
            item = re.sub(replace_item[0], replace_item[1], item)

        result.append(item)

    # 整合
    context = split_token.join(result)

    # special_process：
    context = sp.step1_mv_ngram_repeat(context, pattern_ngram, lang)
    context = sp.step2_rm_last_paragh(context, lang)
    context = sp.step3_rm_special_char(context)

    return context


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('[^\n]\n    --', "\n\n    --", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context

# 句号分割判断整句重复
def remove_duplicates(text,lang):
    # 分割文本成句子
    if lang == "zh":
        sentences = text.split("。")
        unique_sentences = []
        seen_sentences = set()
        for sentence in sentences:
            if sentence not in seen_sentences:
                unique_sentences.append(sentence)
                seen_sentences.add(sentence)
        # 重新组合文本
        context = "。".join(unique_sentences)
        return context
    else:
        sentences = text.split(". ")
        # 识别和删除重复句子
        unique_sentences = []
        seen_sentences = set()
        for sentence in sentences:
            if sentence not in seen_sentences:
                unique_sentences.append(sentence)
                seen_sentences.add(sentence)
        # 重新组合文本
        context = ". ".join(unique_sentences)
        return context


fw = open("MSD_preformat_3_new.jsonl", "w", encoding="utf-8")
with open("MSD_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        # if need
        lang = item["lang"]
        context = clean_text(context, lang)
        context = remove_duplicates(context,lang)
        context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
