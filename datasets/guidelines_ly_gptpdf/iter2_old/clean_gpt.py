import json
import re

import numpy as np
from tqdm import tqdm
import math
import spacy
import random
from nltk.corpus import wordnet
import inflect
inflect = inflect.engine()
import kenlm
from nltk.tokenize import word_tokenize
import fasttext
from collections import defaultdict
model = kenlm.LanguageModel(r"C:\Users\Administrator\Desktop\4k_gram.klm")
fasttext_model = fasttext.load_model('fenlei_model.bin')


import signal
from tqdm import tqdm
from contextlib import contextmanager


# 带标签版
pattern_list = [
# 带特殊符号的无关内容
[
    r'(\([^\(\)]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(http)|(\.html))[^\)\(]*\))',
    r'删除20:<u>\1</u>'
],
[
    r'([^\d][^\.\n]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(http)|(\.html))[^\n]*)',
    r'删除1:<u>\1</u>'
],
[
    r'(\n\s*[a-zA-Z\.]\s*\n)',
    r'删除2:<u>\1</u>'
],
[
    r'([^\n]*Copyright[^\n]*)',
    r'删除3:<u>\1</u>'
],
[
    r'(ISBN\s*[A-Z0-9-]*)',
    r'删除4:<u>\1</u>'
],
[
    r'(👍|▶|●|©|®|([^\n]*↑[^\n]*)|†|¶|║|§|∧|™|■|❏|□|✓|✔|❍|😃|�|∑|✦|❤️|❤)',
    r'删除5:<u>\1</u>'
],
[
    r'(\(\s?\b([Ff]igure[s]?|Section|diagram|Appendix|Box|[Ss]ource[s]?|[Ff]igs?|p|FIGURE)\b[^\)\n]*\))',
    r''
],

[
    r'((\([^\(]{0,20})\s[Ff]igures?[^\(\)]*.)',
    r'删除8:<u>\1</u>'
],
[
    r'([\(\[]\s?([Tt]able|[sS]ee)[^\)\]]*?[\)\]])',
    r'删除9:<u>\1</u>'
],
# [
#     # r'([^\n\.]*\bFigs?(ure)?s?\b\.?[\s* ](\d+)?\.?[^\n]*)',
#     r'([^\n\.]*(Figs?(ure)?s?|FIGURE)\s?\.?\s?(\d+\.\d+)?[^\n\.]*\.?)',
#     r'删除7:<u>\1</u>'
# ],
# [
#     r'([^\n\.]*Fig[s]?(ure)?s?(\s\d\.)?[^\n\.]*\.)',
#     r'删除10:<u>\1</u>'
# ],
[
    r'(\([\d\s,\.\-–]{1,50}\))',
    r'删除11:<u>\1</u>'
],
[
    r'([^\d])(\[\s?\d{1,4}(\s{0,3}[\-–—,\.]\s{0,3}\d{1,4}){0,20}\s?\])',
    r'\1删除12:<u>\2</u>'
],
[
    r'([^\d])([1-9][0-9]{1,4}(\s{0,3}[\-–,\.]\s{1,3}[1-9][0-9]{1,4}){1,20})([^\d]?)',
    r'\1删除13:<u>\2</u>\4'
],
[
    r'(\[\s?(\d{1,3}\s?[-,，]?\s?)+\d?\s?\]\s?\*?)',
    r'删除14:<u>\1</u>'
],
[
    r'(\(\s?[IⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫa-zA-Z]?\s?[a-zA-Z]?\s?,\s?[a-zA-Z]\s?\)\s?)[。\.]',
    r'删除15:<u>\1</u>'
],
[
    r'([^\d][\.,])((\s{1,3}\d+[\s\n]{1,3}){1,5}\.?)(\s?[A-Z])',
    r'\1删除16:<u>\2</u>\4'
],
[
    r'([^\d][\.,]\s?)(\d{1,4}(\s{0,3}[\-–,\.\s]\s{0,3}\d{1,4}){0,20})(\n|\s?[A-Z]|$)',
    r'\1删除17:<u>\2</u>\4'
],
[
    r'(#{1,3})\n',
    r'删除18:<u>\1</u>'
],
[
    r'(\([^\(\)]{0,100}(\set[\s\xa0]{1,3}al|\d{4})[^\(\)]{0,100}\))',
    r'删除19:<u>\1</u>'
],
# [
#     r'([a-z\)])(---)(a-z)',
#     r'\1<u>\2替换为-</u>\3'
# ],
# [
#     r'^\s?(---)\s?$',
#     r'<u>\1替换为-</u>'
# ]
[
    r'(\^\d+(\s?,\s?\d+){0,5})',
    r'删除21:<u>\1</u>'
]
]

context_pattern = [
    [r'(¬\s*)', r''],
    [r'(\(\s*\))', r'']
]

# nlp = spacy.load("en_core_web_trf")
nlp = spacy.load("en_core_web_sm")
# 增加最大长度限制
# nlp.max_length = 10000000  # 将最大长度增加到200万字符（根据需要调整）

class speicalProces:
    def __init__(self):
        pass

    def is_not_upper(self, char):
        return not char.isupper()

    def step1_delete_photo_describe(self, duans):
        """
        用\n对段进行切分，切分成行，进行判断，以行为单位删除图片描述的
        """
        new_duans = []
        for duan in duans:
            lines = duan.split('\n')
            for line in lines:
                # print(line.strip())
                # print("*"*50)
                if re.search('^([#*]{0,5}).{0,5}\s?([Ff]igs?(ure)?s?|FIGS?(URE)?s?|图)',line.strip()) or re.search('\.(png|jpg|PNG|JPG)',line.strip()):
                    escaped_least_text = re.escape(line)
                    try:
                        duan = re.sub(rf'{escaped_least_text}', rf'删除图片描述:<u>{line}</u>', duan)
                    except re.error as e:
                        print(f"Regex error: {e}")
            new_duans.append(duan)
        return new_duans

    def get_score(self,sentence):
        tokenize_text = word_tokenize(sentence)
        final_text = " ".join(tokenize_text)
        score = model.score(final_text, bos=False, eos=False)
        length = len(tokenize_text)
        if length > 0:
            score = (10 ** (-score / length))
        return score

    def is_mulupage(self,text):

        label = fasttext_model.predict(text.strip().replace('\n', ''))
        print(label[0][0])
        if label[0][0] in ['__label__mulu', '__label__cankao']:
            text = "(本页删除)本页被模型判断为参考页或目录页" + text
        return text

    def step2_is_pagefoot(self, duans):
        # duans是一个列表，取第一段和最后一段进行if判断，判断页眉页脚
        if re.search("\n",duans[0]):
            first_line = duans[0].split("\n", 1)[1]  # 只以第一个换行符分割
        else:
            first_line = duans[0]
        if re.search("】",duans[-1]):
            last_paragraph = duans[-1].split("】")[1]
        else:
            last_paragraph = duans[-1]
        # print(first_line)
        # print(self.get_score(first_line))
        # print(last_paragraph)
        # print(self.get_score(last_paragraph))

        if self.get_score(first_line) > 5000 and not re.search("#",first_line) and not re.search('\|',first_line):
            duans[0] = "疑似页眉" + duans[0]
        elif self.get_score(first_line) > 10000 and not re.search('\|',first_line):
            duans[0] = "疑似页眉" + duans[0]

        if self.get_score(last_paragraph) > 3500:
            duans[-1] = "疑似页脚" + duans[-1]
        return duans

    def is_merge_ngram(self,text, next_text):
        """
        1.给text打分，next_text分别打分
        2.给marge_text打分
        3.判定marge_text满足分数小于text和next_text，且小于某个值 这个值可能是5000、3000、2000... 返回True
        :return:
        """
        text_score = self.get_score(text)
        next_text_score = self.get_score(next_text)
        merge_text = text + " " + next_text
        merge_text_sorce = self.get_score(merge_text)
        if (merge_text_sorce < text_score or merge_text_sorce < next_text_score) and merge_text_sorce < 5000:
            # print(merge_text)
            return True

    def is_merge_duannei(self, text, next_text):
        # 定义一个介词列表
        preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A']
        if re.search(r'\s\d+\.$', text): #
            # print("1")
            return True
        elif re.search(r'^([\d+A-Z][\.,]){1,3}$', text) and next_text.lstrip()[0].isupper():  # 匹配段落中只有序号且下一段是大写开头的情况
            # print("2")
            return True
        elif any(text.rstrip().endswith(" " + prep) for prep in preposition_list):  # 匹配同一段中介词结尾的
            # print("3")
            return True
        elif text.rstrip() and text.rstrip()[-1] in ['-','—']:
            # print("4")
            return True
        elif "#" not in text and "*" not in text and re.search(r'[^\.?!]$', text) and re.match(r'^[a-z]', next_text.lstrip()):
            # print("5")
            return True
        elif re.search(r'\([^\)]*$|\[[^\]]*$', text) and re.search(r'^[^\(\[]*[\)\]]',next_text):  # 前一行有一个未对应的左括号，下一行前面有一个与之对应的右括号
            # print("6")
            return True
        # 可以先注释掉
        # elif ((text.rstrip()[-1].islower() or text.rstrip()[-1] in [',']) and (next_text.lstrip()[0].isupper() or next_text.lstrip()[0] in ['(',')','"','”','“']) and "#" not in text and "#" not in next_text and self.is_merge_ngram(text, next_text)):   # 前一行小写或逗号结尾，下一行大写开头，且与标题无关，加入ngram判断
        #     return True
        elif re.search(r'^#{1,3}\s?[\d\.]{1,10}$',text) and next_text.lstrip()[0].isupper():
            # print("7")
            return True
        elif len(text.strip()) == 1 and text == '.' and next_text[0].isupper():
            # print(text, next_text)
            # print("8")
            return True
        elif re.search(r'^#',text) and next_text[0].isupper() and self.is_merge_ngram(text, next_text):
            return True
        return False
    def is_merge_duan(self,stripped_item,next_item):
        # 定义一个介词列表
        preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A']
         # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
        if any(stripped_item.rstrip().endswith(" " + prep) for prep in preposition_list):
            # print("1")
            return True
        elif stripped_item and stripped_item[-1] in ['-']:
            # print("2")
            return True
        elif re.search(r'Figs?\.$',stripped_item):
            # print("3")
            return True
        elif re.search(r'\([^\)]*$|\[[^\]]*$', stripped_item) and re.search(r'^[^\(\[]*[\)\]]',next_item):
            # print("4")
            return True
        elif len(stripped_item) == 1 and stripped_item in ['.','·']:
            # print("5")
            return True
        return False

    def step3_1_more_linefeed_duannei(self, context):
        # print(context)
        new_context = []
        for item in context:
            # 将 item 按 "\n" 分割
            item_sections = re.split(r'\n', item)
            section_index = 0
            while section_index < len(item_sections) - 1:  # 确保不会越界
                if self.is_merge_duannei(item_sections[section_index],item_sections[section_index + 1]):
                    item_sections[section_index] += "|删除段内换行|" + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]
                else:
                    section_index += 1  # 只有在不合并时才自增

            # 更新 item 以反映合并的段落
            item = '\n'.join(item_sections)
            new_context.append(item)
        return new_context
    def step3_2_more_linefeed_duan(self,context):
        index = 0
        while index < len(context):
            item = context[index]

            # 合并以小写字母或特定标点符号开头的段落
            stripped_item = item.strip()
            # print(stripped_item)
            if index >= 0:
                if index > 0 and stripped_item and context[index - 1][-1] not in ['.', '!', '?', '|',':'] and not re.search('#',stripped_item) and (
                        stripped_item[0].islower() or stripped_item[0] in ["(", "[", ")", "]", "."]) and not re.search('^[a-z]\s?\.',stripped_item.lstrip()):
                    """
                    遇到小写开头的段 1.上一段没有#直接连上去 2.上一段有#但是不止一行，切上一段的最后一行和当前的第一行，使用模型判断该不该连 3.上一段有#但是只有一行，去上上段切最后一行和当前的第一行，模型判断该不该连
                    """
                    # 上一段不能出现#，出现#证明是标题段
                    if not re.search(r'#', context[index - 1]):
                        # 合并到前一个 item
                        context[index - 1] = context[index - 1].rstrip() + "|删除段之间换行-1|" + item.lstrip()
                        # 删除当前 item
                        del context[index]
                        # 继续检查当前索引位置的元素
                        index = index - 1
                        continue
                    elif len(re.split(r'\n', context[index - 1])) >= 2:
                        # 上一段有标题也有正文，分割context[index-1]最后一行，分割stripped_item的第一行
                        previous_paragraph_lines = re.split(r'\n', context[index - 1])
                        last_line_of_previous = previous_paragraph_lines[-1].strip()
                        first_line_of_current = stripped_item.splitlines()[0].strip()
                        if self.is_merge_ngram(last_line_of_previous, first_line_of_current):
                            # 合并到前一个 item
                            context[index - 1] = context[index - 1].rstrip() + "|删除段之间换行-2|" + item.lstrip()
                            # 删除当前 item
                            del context[index]
                            # 继续检查当前索引位置的元素
                            index = index - 1
                            continue
                    elif len(re.split(r'\n', context[index - 1])) == 1:
                        if index - 2 and len(re.split(r'\n', context[index - 2])) > 1 and context[index - 2][-1] not in ['.', '!', '?']:
                            previous_paragraph_lines = re.split(r'\n', context[index - 2])
                            last_line_of_previous = previous_paragraph_lines[-1].strip()
                            first_line_of_current = stripped_item.splitlines()[0].strip()
                            if self.is_merge_ngram(last_line_of_previous, first_line_of_current):
                                # 合并context[index - 2]
                                context[index - 2] = context[index - 2].rstrip() + "|删除段之间换行-3|" + item.lstrip()
                                # 删除当前 item
                                del context[index]
                                # 继续检查当前索引位置的元素
                                index = index - 1
                                continue
                if index + 1 < len(context) and re.search(r'\([^\)]*$|\[[^\]]*$', stripped_item) and re.search(r'^[^\(\[]*[\)\]]',context[index + 1]):
                    if index + 1 < len(context) and "#" not in context[index + 1] and not re.search(r'^[Ff]ig', context[
                        index + 1].lstrip()):
                        # 合并到下一个 item
                        context[index] = item.rstrip() + "|删除段之间换行-6|" + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue
                elif index + 1 < len(context) and self.is_merge_duan(stripped_item,context[index + 1]) and stripped_item is not None:
                    if index + 1 < len(context) and "#" not in context[index + 1] and not re.search(r'^[Ff]ig', context[
                        index + 1].lstrip()):
                        # 合并到下一个 item
                        context[index] = item.rstrip() + "|删除段之间换行-4|" + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue

            index += 1
            # print(context)

        return context
def clean_text(text):
    sp = speicalProces()
    text = sp.is_mulupage(text)
    # print(text)
    split_token = "\n\n"
    # 切分一下数据
    duans = text.split(split_token)
    print(duans)
    result = []
    # 删除图片描述
    duans = sp.step1_delete_photo_describe(duans)
    duans = sp.step2_is_pagefoot(duans)
    duans = sp.step3_1_more_linefeed_duannei(duans)
    duans = sp.step3_2_more_linefeed_duan(duans)
    # 正则替换
    if duans and len(duans) > 0 and duans is not None:
        for item in duans:
            # if "## References" in item:
            #     continue
            for pattern_item in pattern_list:
                item = re.sub(pattern_item[0], pattern_item[1], item)
                item = item.strip()
            for pattern_item in context_pattern:
                item = re.sub(pattern_item[0], pattern_item[1], item)
            result.append(item)

    for item in result:
        print(item)
    text = split_token.join(result)
    # context = sp.step9_complete_sequence_number(context)
    return text


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)

    # context = re.sub("[li][\.,]" , '1.' ,context)
    return context

def process_line(items, sp):
    item = json.loads(items.strip())
    context = clean_text(item,  sp)
    context = post_process(context)
    if len(context) < 100:
        return
    item["text"] = context
    item = json.dumps(item, ensure_ascii=False)
    return item

fw = open("/pdf/clean_json/recleanB2_guidelines_ly_gptpdf.jsonl", "w", encoding="utf-8")
with open("/pdf/clean_json/recleanB_guidelines_ly_gptpdf_label.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        # if item["seq_id"] == "86005fe7-ca59-4115-860e-641b357f5f4c":
        # print(item)
        print(item["seq_id"])
        text = item['text']
        text = clean_text(text)
        text = post_process(text)
        # print(context)
        item["text"] = text
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")


