import json
import os
import re
# from langdetect import detect
# from langdetect import detect_langs
from tqdm import tqdm
import Levenshtein

pattern_list_zh = [
    [r'(表格)?(Table)? \$\(document\).ready.*?(\} \}\); \} \}\);)', r'\n'],
    [r'(\$\(document\))?.ready.*?console', r'\n'],
    # 阅读更多后面[\s\.。]随意匹配0-3次，一定有右括号，阅读更多前面一定有左括号不能再出现其他的左右括号情况 13-16顺序固定，把英文括号作为特征
    [r'\([^\(\)]*?阅读更多[\s\.。]{0,3}\)',''],
    [r'\(', '（'],
    [r'\)', '）'],
    [r'（[^（）]*?阅读更多[\s\.。]{0,3}）',''],
    # 去除重复存在的0-10字的文本，执行两
    [r'(\b[^。]+)(\s+\1)+', r'\1'],
    [r'(\b[^。]+)(\s+\1)+', r'\1'],
    [r'（另?见([^（）阅]*?（[^(阅读更多)]{1,50}）[^（）]*?){0,6}.*?(阅读更多|）)[\s。）]{0,3}', r'\n'],
    [r'[^。]*?(\.\.\. )?阅读更多[^？。]*[\)）。？]{0,3}', r'\n'],
    # 剩下的另见两百个左右，从另见前面的句号到后面的句号
    [r'[—]{0,2}[^。——]*?另见[^。]*[\s。）]{0,3}', r'\n'],
    [r'（.{0,5}见[^（）]*(（.{0,100}）[^（）]*){0,3}）', ''],
    [r'看?法? 进行患者培训\s?', r'\n'],
    [r'[^。]*参考文献(.{0,300}?doi: [^\s]+){1,10}([^\u4e00-\u9fa5]*)?(的[^。]*。)?', r'\n'],
    [r'[^。]*参考(文献)?[^。]*.）?', r'\n'],
    [r'。的[^。]*', r'\n'],
    [r'更多信息[^，。,\.]*.', r'\n'],
    [r'www\.\w+\.\w+[^\s]*\s', r'\n'],
    [r'会在这本.*点击此处', r'\n'],
    [r'[（\(][^\)）]{0,10}(也可)?(另请)?(也)?(请)?(参|亦)(见|阅)(概述)?[^）（。]*(（[^）]{0,50}）[^）（。]*){0,3}[）。]{0,2}', r'\n'],
    [r'[^。]*参(见|阅)[^。]*', r'\n'],
    [r'[^\.,]*\.\.\. Common.TooltipReadMore', r'\n'],
    [r'请注意，本手册.*', r'\n'],
    [r'\(又见 .*[^ ]概述{1,3}', r'\n'],
    [r'\(s?S?ee[^\)]*.\.?', r'\n'],
    [r'观看这些视频.*', r'\n'],
    [r' ?\(?（?见表 ?[^。]*', r'\n'],
    [r' ?（?\(?见图 ?[^。]*', r'\n'],
    [r' ?（?\(?也见 ?[^。]*', r'\n'],
    # [r'[\(（ 也可同样]+见 ?[^。]*。?', '\n'],
    # [r'[^一-龥-。]{10,1000}', ''],
    [r'(\s[^\s]{0,20})?(（其他[^）]*)?概要\s?）?', r'\n'],
    [r'[^。]*(出版商[^。]*。|图[像片]经?由|这张照片)[^。]*。', r'\n'],
    [r'[\(（\s]{1,5}?[^\s\(（。，]*(视频|概述)[\)）\.\s]{1,5}', r'\n'],
    [r'表格[^\.，。:：]*\s', r'\n'],
    [r'[^。\u4e00-\u9fa5]{100,}', ''],
    [r'[^\u4e00-\u9fa5]*©.[^。]*。', ''],
    [r'[^。.]*[在该].{0,10}图中[^。]*。', r'\n'],
    [r'(（)?另请参双相情感障碍。(）)?', r''],
    [r'(。)?欲了解', r''],
    [r'（[^（]{0,20}讨论[^）]{0,20}）', ''],
    [r'[^。]*[左右]图[^。]*。', r'\n'],
    [r'[^。]*[左右这].{0,10}照片[^。]*。(.{0,20}照片[^。]*。){0,}', r'\n'],
    [r'†\s?', ''],
    [r'[^。]*照片由[^。]*.', ''],
    ['[^。；]*(热线|拨打)[^。]*[。）]{0,2}(国家老人虐待中心[^。]*。)?', r'\n'],
    [r'（[^（]*see [Tt]able[^）]*）', ''],
    [r'（）', ''],
    [r'([^。]*见 。)?[^。]*网站[^。]*[。）]{0,2}', r'\n'],
    # 匹配文本中连续出现的逗号、顿号或句号
    [r'[，。、]{2,}', r'。'],
    [r'=""[><]{0,2}', ''],
    [r'<(\s?\d\s?)?>([^<>]{0,50}<(\s?\d\s?)?>)?', ''],
    # # 中文之间有空格，只捕获两边的中文
    [r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2'],
    [r'(（\s?\d\s?）)([，。：])', r'\2'],
    [r'[^。]*$', ''],
    [r'([。]+\s?)\1*', r"。"],
]

pattern_list_en = [
    [r'（', '\('],
    [r'）', '\)'],
    [r'[^\.]*?View Patient Education\s?', r'\n'],
    [r'More Information The following.*', r'\n'],
    [r'(表格)?(Table)? \$\(document\).ready.*?\} \}\); \} \}\);', r'\n'],
    [r'(\$\(document\))?.ready.*?console', r'\n'],
    [r'\b([^\d]+)(\s+\1){1,2}\b',r'\1'],
    # [r'(\(\s?s?S?ee[^\.]*)?\.?\(?[^\.]*[\.]{0,3} read more [^A-Z\.]*(\.\))?', '\n'],
    [r'\([^\(\)]*?read more[\s\.]{0,3}\)',''],
    [r'\(\s?[sS]ee[^\.\)]*(\(.{0,300}?\)[^\.\(]{0,300}){0,5}.*?\)', ''],
    [r'([^\.]\d+){0,2}[^\.]*([Ss]ee.{0,300})?(\.\.\.)? read more[^\.\(\)]*(\(.{0,350}?\)[^\.\(]{0,350}){0,5}[\.\)]{0,3}(\d+[^.]*.){0,2}',r'\n'],
    [r'[^\.]*?[\.]{0,3}?\s?Common.TooltipReadMore[^\.]*\.?\)?', r'\n'],
    [r'\(Adapted from[^\(]{0,200}(\([^\)]{0,200}\)[^\(]{0,200}){0,3}\)',r'\n'],
    [r'(,)?(\s+Diagnosis reference 1.\s+)?Adapted from [^\.\n]*\.(.{0,300},\s?\d{4}\.)?(\s+Copyright 1992, American Medical Association.\s+)?',r'\n'],
    [r'[^\.]*r?R?eference(?:(?!r?R?eference).)*?(doi\s?(:|\.)\s?[^\s]*)(.{0,500}?doi\s?:\s?[^\s]*){0,10}', r'\n'],
    [r'\.(\d+–\d+)*?.{0,150}(\.?(doi|DOI)\s?(:|\.)\s?[^\s]*)(.{0,500}?(doi|DOI)\s?(:|\.)\s?[^\s]*){0,5}', r'\n'],
    [r'(?<=\.|”)(\d+\.)?(.{0,200}http[^\s]*){1,5}', r'\n'],
    [r'[^\.]*© Elsevier Inc. All Rights Reserved.([^\.]*.){2}(.*\.?doi\s?:?\s?[^\s]*)?', r'\n'],
    [r'(Image[^\.]{0,100}\.)?[^\.?]*(This|The) ([iI]mage|photo)[^\.]*.',r'\n'],
    [r'[^\.]* (Image|Photo) [^\.]*.',r'\n'],
    [r'[^\.]*PHOTO [A-Z]{2,}',r'\n'],
    [r'DR ([A-Z]+\.){1,}','\.'],
    [r'(\d\.)?[^\.]{0,300}[rR]eference(s)?(.{0,300}\d\d[/]?\d\d\)?\.[^\d]?){1,5}',r'\n'],
    [r'Epub[^\.]*\.(.{0,200}?\d+\.){0,6}',r'\n'],
    [r'\(?[^\.\(]*?[sS]ee [tT]able[^\.\)]*.',r'\n'],
    [r'[^\.]*©[^\.]*.', r'\n'],
    [r'By permission of the publisher.*?(\d{4}.|\. \\n)',r'\n'],
    [r'Table',''],
    [r'[^\.]*VIDEO',''],
    [r'\(?[^\.\(]*see [Ff]igure[^\.\)]*.',''],
    [r'PMID(.{0,20}PM.*?\d\.)?[^\.A-Z]*\.?',r'\n'],
    [r'\(?[^\.\(]*(\(.{0,100}?\)[^\.\(]{0,100}){0,3}see also[^\.\)]*(\(.{0,100}?\)[^\.\(]{0,100}){0,3}[^\.\)]*?[\.\)]{0,2}',''],
    [r'\(?[^\.\(]*[Ff]or more information[^\.\(\)]*(\(.{0,300}?\)[^\.\(]{0,300}){0,5}\)?(\sA[^\.]*.)?',r'\n'],
    [r'([aA]dapted from[^\.]{0,100}\.\s)?(Treatment references)?[^\d]\d\.\s+[^\d].{0,300}, \d{4}\.',''],
    [r'Erratum in[^\.]*[\.]',''],
    [r'\(\s?\d?\s?\)',''],
    [r'Courtesy of Tomah Memorial Hospital, Department of Physical Therapy, Tomah, WI; Elizabeth C.K. Bender, MSPT, ATC, CSCS; and Whitney Gnewikow, DPT, ATC.',''],
    [r'\(?[^\(\.]*Also see[^\(\.]*(\([^\)]*\)[^\.]*){0,3}[\.\s\)]{0,3}','\n'],
    [r'[^\.]*For detailed[^\.]*.',r'\n'],
    [r'(Diagnosis references )?(\d+\.)?[^\.]*ISBN[^\.TK]*\.?', r'\n'],
    [r'[^\n]*et al\s?:[^\n]*', r'\n'],
    [r'\n\s+?[a-z][^\.]*\.', r'\n'],
    # 特殊情况 去重的正则抓不到它
    [r'COVID-19 COVID-19 COVID-19','COVID-19'],
    # # 多个小写后面是大写分开中间加
    [r'([a-z]{2,})([A-Z])', r'\1\.\2'],
    # # 结尾半句话删除
    [r'[^\.]*$', ''],
    [r'^\.', ''],
    [r'=""', ''],
    [r'\\\.\s?',''],
    [r'([。]+\s?)\1*', r"\."],
    [r'([,\.])(\s?[,\.]\s?){1,3}', r'\1'],
    [r"\.\s?,\s?", r"\."],

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
            if context:
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

    # 句号分割判断整句重复
    def step4_remove_duplicates(self, text, lang):
        # 分割文本成句子
        # if lang == "zh":
        #     sentences = text.split("。")
        # else:
        #     sentences = text.split(".")
        #
        # unique_sentences = []
        # seen_sentences = set()
        # for sentence in sentences:
        #     old_sentence = sentence
        #     sentence = sentence.strip()  # 去除空格和换行符
        #     if sentence not in seen_sentences:
        #         unique_sentences.append(old_sentence)
        #         seen_sentences.add(sentence)
        #
        # # 重新组合文本
        # context = "。".join(unique_sentences) if lang == "zh" else ". ".join(unique_sentences)
        # return context

        # 分割文本成句子
        if lang == "zh":
            sentences = text.split("。")
        else:
            sentences = text.split(".")

        # 定义Jaro-Winkler相似度阈值
        threshold = 0.9

        # 初始化已见句子集合
        seen_sentences_set = set()

        # 初始化唯一句子列表
        unique_sentences = []

        # 遍历所有句子
        for sentence in sentences:
            old_sentence = sentence
            sentence = sentence.strip(" ").strip("\n")  # 去除空格和换行符
            # 检查当前句子是否与已见句子集合中的任何句子足够相似
            is_duplicate = False
            for seen_sentence in seen_sentences_set:
                # 计算Jaro-Winkler相似度
                jaro_winkler_distance = Levenshtein.jaro_winkler(sentence, seen_sentence)
                # 如果相似度超过阈值，则认为是重复
                if jaro_winkler_distance > threshold:
                    is_duplicate = True
                    break
            # 如果不是重复的，则添加到唯一句子列表和已见句子集合中
            if not is_duplicate:
                unique_sentences.append(old_sentence)
                seen_sentences_set.add(sentence)

        # 重新组合文本
        context = "。".join(unique_sentences) if lang == "zh" else ". ".join(unique_sentences)
        return context

    # 修理括号
    def step5_repair_parentheses(self, context, lang):
        stack = []
        # 将文本转换为列表，方便对着索引删除
        list_text = list(context)
        for i, char in enumerate(context):
            if char == '(' or char == "（" or char == '[' or char == '{':
                stack.append(i)
            elif char == ')' or char == "）" or char == ']' or char == '}':
                if not stack:
                    # 没有出现左括号,右括号直接删除
                    list_text[i] = ''
                else:
                    stack.pop()
        # 不为空说明有多余括号存在
        while stack:
            index = stack.pop()
            # 去除的括号用逗号代替
            if lang == 'zh':
                list_text[index] = '，'
            else:
                list_text[index] = ','
        return ''.join(list_text)


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
    context = sp.step4_remove_duplicates(context, lang)
    context = sp.step5_repair_parentheses(context, lang)
    return context


def post_process(context):
    # 可能存在换行符被删掉的问题，需要修改
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # context = context.lstrip(" ").lstrip(" ")
    # 消除空格问题
    context = re.sub(r'\n +\n', r"\n\n", context)
    context = re.sub(r'\n +\n', r"\n\n", context)
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub(r'[^\n]\n    --', r"\n\n    --", context)
    # 去掉过多\n的情况
    context = re.sub(r"\n{2,}", r"\n\n", context)
    context = re.sub(r'\n\.', r'\n', context)
    # 被清洗掉的句子存在相连的情况，将多个替换的换行符换成一个
    context = re.sub(r'(\n)+', r'\n', context)
    context = re.sub(r'\n([。，])', r'\1\n', context)
    context = re.sub(r'\n([,\.])', r'\1\n', context)
    context = re.sub(r'[，、。]{2,}', '。', context)
    context = re.sub(r'([,\.])(\s?[,\.]\s?){1,3}', r'\1',context)

    return context


fw = open("MSD_preformat_6_zh.jsonl", "w", encoding="utf-8")
with open("MSD_preformat_zh.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        # if need
        lang = item["lang"]
        context = clean_text(context, lang)
        context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
