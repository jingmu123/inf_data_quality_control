import json
import os
import re
# from langdetect import detect
# from langdetect import detect_langs
from tqdm import tqdm

pattern_list_zh = [
    [r'\(', '（'],
    [r'\)', '）'],
    [r'（另见([^（）阅]*?（[^(阅读更多)]{1,50}）[^（）]*?){0,6}.*?(阅读更多|）)[\s。）]{0,3}','\n'],
    # 剩下的另见两百个左右，从另见前面的句号到后面的句号
    [r'[—]{0,2}[^。——]*?另见[^。]*[\s。）]{0,3}','\n'],
    [r'看?法? 进行患者培训\s?', '\n'],
    [r'[^\。]*参考(文献)*.?doi: [^\s]+', '\n'],
    [r'[^\。]*参考(文献)?[^，。]*.\)?）?', '\n'],
    [r'[^。]*?(\.\.\. )?阅读更多[^？。]*[\)）。？]{0,3}', '\n'],
    [r'。的[^。]*','\n'],
    # 去除重复存在的0-10字的文本
    [r'\b((\w+)|([\u4e00-\u9fa5]{0,10}))\b\s*(?=\1)',''],
    [r'更多信息[^，。,\.]*.', '\n'],
    [r'www\.\w+\.\w+[^\s]*\s', '\n'],
    [r'会在这本.*点击此处', '\n'],
    [r'[（\(][^\)）]{0,10}(也可)?(另请)?(也)?(请)?(参|亦)(见|阅)(概述)?[^\.）\)。]*.[）\)]?', '\n'],
    [r'[^。]*参(见|阅)[^。]*', '\n'],
    [r'[^\.,]*\.\.\. Common.TooltipReadMore', '\n'],
    [r'(表格)?(Table)? \$\(document\).ready.*?(\} \}\); \} \}\);)', '\n'],
    [r'(\$\(document\))?.ready.*?console', '\n'],
    [r'请注意，本手册.*', '\n'],
    [r'\(又见 .*[^ ]概述{1,3}', '\n'],
    [r'\(s?S?ee[^\)]*.\.?', '\n'],
    [r'观看这些视频.*', '\n'],
    [r' ?\(?（?见表 ?[^。]*', '\n'],
    [r' ?（?\(?见图 ?[^。]*', '\n'],
    [r' ?（?\(?也见 ?[^。]*', '\n'],
    [r'[\(（ 也可同样]+见 ?[^。]*。?', '\n'],
    # [r'[^一-龥-。]{10,1000}', ''],
    [r'(\s[^\s]{0,20})?(（其他[^）]*)?概要\s?）?', '\n'],
    [r'[^。]*(出版商[^。]*。|图[像片]经?由|这张照片)[^。]*。', '\n'],
    [r'[\(（\s]{1,5}?[^\s\(（。，]*(视频|概述)[\)）\.\s]{1,5}', '\n'],
    [r'表格[^\.，。:：]*\s', '\n'],
    ['[^。\u4e00-\u9fa5]{100,}',''],
    ['[^\u4e00-\u9fa5]*©.[^。]*。',''],
    [r'\n。','。\n'],
    # 匹配文本中连续出现的逗号、顿号或句号
    [r'([，、。])[，、。]', r'\1'],
    [r'=""', ''],
    [r'<(\s?\d\s?)?>([^<>]{0,50}<(\s?\d\s?)?>)?',''],
    # 中文之间有空格，只捕获两边的中文
    [r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2'],
    [r'(（\s?\d\s?）)([，。：])', r'\2'],
    [r'[^。]*$', ''],
    [r'([。]+\s?)\1*', "。"],
]

pattern_list_en = [
    [r'（', '\('],
    [r'）', '\)'],
    [r'[^\.]*?View Patient Education\s?', '\n'],
    [r'More Information The following.*', '\n'],
    [r'(表格)?(Table)? \$\(document\).ready.*?\} \}\); \} \}\);', '\n'],
    [r'(\$\(document\))?.ready.*?console', '\n'],
    # [r'(\(\s?s?S?ee[^\.]*)?\.?\(?[^\.]*[\.]{0,3} read more [^A-Z\.]*(\.\))?', '\n'],
    ['([^\.]\d+){0,2}[^\.]*([Ss]ee.{0,300})?(\.\.\.)? read more[^\.\(]*(\(.{0,350}?\)[^\.\(]{0,350}){0,5}[\.\)]{0,3}(\d+[^.]*.){0,2}','\n'],
    [r'\(\s?[sS]ee[^\.\)]*(\(.{0,300}?\)[^\.\(]{0,300}){0,5}.*?\)', ''],
    [r'[^\.]*?[\.]{0,3}?\s?Common.TooltipReadMore[^\.]*\.?\)?', '\n'],
    [r'[^\.]*r?R?eference(?:(?!r?R?eference).)*?(doi\s?(:|\.)\s?[^\s]*)(.{0,500}?doi\s?:\s?[^\s]*){0,10}', '\n'],
    [r'\.(\d+–\d+)*?.{0,150}(\.?(doi|DOI)\s?(:|\.)\s?[^\s]*)(.{0,500}?(doi|DOI)\s?(:|\.)\s?[^\s]*){0,5}', '\n'],
    [r'(?<=\.|”)(\d+\.)?(.{0,200}http[^\s]*){1,5}', '\n'],
    [r'[^\.]*© Elsevier Inc. All Rights Reserved.([^\.]*.){2}(.*\.?doi\s?:?\s?[^\s]*)?', '\n'],
    ['(Image[^\.]{0,100}\.)?[^\.?]*(This|The) ([iI]mage|photo)[^\.]*.','\n'],
    ['[^\.]* (Image|Photo) [^\.]*.','\n'],
    ['[^\.]*PHOTO [A-Z]{2,}','\n'],
    ['DR ([A-Z]+\.){1,}','\.'],
    ['(\d\.)?[^\.]{0,300}[rR]eference(.{0,300}\d\d[/]?\d\d\)?\.[^\d]?){1,5}','\n'],
    ['Epub[^\.]*\.(.{0,200}?\d+\.){0,6}','\n'],
    ['\(?[^\.\(]*?[sS]ee [tT]able[^\.\)]*.','\n'],
    [r'[^\.]*©[^\.]*.', r'\n'],
    [r'By permission of the publisher.*?(\d{4}.|\. \\n)','\n'],
    [r'Table',''],
    ['\(?[^\.\(]*(\(.{0,100}?\)[^\.\(]{0,100}){0,3}see also[^\.\)]*(\(.{0,100}?\)[^\.\(]{0,100}){0,3}[^\.\)]*?[\.\)]{0,2}',''],
    ['\(?[^\.\(]*[Ff]or more information[^\.\(\)]*(\(.{0,300}?\)[^\.\(]{0,300}){0,5}\)?(\sA[^\.]*.)?','\n'],
    # 多个小写后面是大写分开中间加
    [r'([a-z]{2,})([A-Z])', r'\1\.\2'],
    # 结尾半句话删除
    [r'[^\.]*$', ''],
    [r'^\.', ''],
    [r'=""', ''],
    [r'\\\.',''],
    [r'([。]+\s?)\1*', "."],
    [r'([,\.])[,\.]', r'\1'],
    [r"\.\s?,\s?", "."],

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

    # 句号分割判断整句重复
    def step4_remove_duplicates(self,text, lang):
        # 分割文本成句子
        if lang == "zh":
            sentences = text.split(r"。")
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
            sentences = text.split(r". ")
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

    # 修理括号
    def step5_repair_parentheses(self,context, lang):
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
    context = sp.step4_remove_duplicates(context,lang)
    context = sp.step5_repair_parentheses(context,lang)
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
    context = re.sub(r'\n\.','\n',context)
    context = re.sub(r'(\n)+','\n',context)
    return context





fw = open("MSD_preformat_4_en.jsonl", "w", encoding="utf-8")
with open("MSD_preformat_en.jsonl", "r", encoding="utf-8") as fs:
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
