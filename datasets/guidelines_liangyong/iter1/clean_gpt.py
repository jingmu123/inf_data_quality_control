import json
import re
from langdetect import detect
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
# -*- coding: utf-8 -*-
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import transformers
import re
from transformers import AutoTokenizer
# ner_pipeline = pipeline(Tasks.named_entity_recognition, 'damo/nlp_raner_named-entity-recognition_chinese-base-generic')
# zeroshot_classifier = transformers.pipeline("zero-shot-classification", model="../model/deberta-v3-large-zeroshot-v2.0")

import signal
from tqdm import tqdm
from contextlib import contextmanager


# 带标签版
pattern_list = [
# 带特殊符号的无关内容
[
    r'(\([^\(\)]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(http)|(\.html))[^\)\(]*\))',
    r''
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
],
[
    r'(\$\^\{\d+\}\$)',
    r'删除22:<u>\1</u>'
],
[
    r'(<sup>[\d+\s,a-z]{1,5}</sup>)',
    r'删除23:<u>\1</u>'
]
]

context_pattern = [
    [r'(¬\s*)', r''],
    [r'(\(\s*\))', r''],
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
            if re.search(r'[A-Z]{5,}\*\*[\s\n]{0,5}[a-z]',duan):
                escaped_least_text = re.escape(duan)
                duan = re.sub(rf'{escaped_least_text}', rf'删除图片描述:<u>{duan}</u>', duan)
            lines = duan.split('\n')
            for line in lines:
                # print(line.strip())
                # print("*"*50)
                if re.search('^([#*]{0,5}).{0,5}\s?([Ff]igs?(ure)?s?|FIGS?(URE)?s?|图)[\s\d]',line.strip()) or re.search('\.(png|jpg|PNG|JPG)',line.strip()):
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

    def is_cankaopage(self,text,lang):
        if lang == "en":
            text = re.sub(r'【\d+】', '', text)
            label = fasttext_model.predict(text.strip().replace('\n', ''))
            print(label[0][0])
            if label[0][0] in ['__label__mulu', '__label__cankao']:
                text = "(本页删除)本页被模型判断为参考页或目录页" + text

        return text

    def step2_is_pagefoot(self, duans,lang):
        # duans是一个列表，取第一段和最后一段进行if判断，判断页眉页脚
        if lang == "en":
            first_line = duans[0]
            last_paragraph = duans[-1]
            # 提取中间段落
            middle_duans = duans[1:-1]
            middle_content = " ".join(middle_duans)
            middle_content = re.sub(r"【\d+】",r'',middle_content)
            first_line_score = self.get_score(first_line)
            last_paragraph_score = self.get_score(last_paragraph)
            middle_content_score = self.get_score(middle_content)
            # print(first_line_score,first_line)
            # print(middle_content_score,middle_content)
            # print(last_paragraph_score,last_paragraph)
            if first_line_score > 4000 and not re.search('\|',first_line) and len(first_line) < 150 and re.search(r'[A-Z][a-z]{1,}\s[A-Z][a-z]{1,}',first_line):
                duans[0] = "疑似页眉" + duans[0]
            elif first_line_score > 8000 and not re.search("#",first_line) and not re.search('\|',first_line) and len(first_line) < 150 and re.search(r'[A-Z][a-z]{1,}\s[A-Z][a-z]{1,}',first_line):
                duans[0] = "疑似页眉" + duans[0]

            if last_paragraph_score > 4000 and not re.search('\|',last_paragraph) and len(last_paragraph) < 150 and re.search(r'[A-Z][a-z]{1,}\s[A-Z][a-z]{1,}',last_paragraph):
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
        preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A', 'with', '&']
        if re.search(r'\s\d+\.$', text):  #
            return True
        if re.search(r'^([\d+A-Z][\.,]){1,3}$', text) and next_text.lstrip()[0].isupper():  # 匹配段落中只有序号且下一段是大写开头的情况
            return True
        if any(text.rstrip().endswith(" " + prep) for prep in preposition_list) and not re.search(r'^\d+\.',next_text.strip()):  # 匹配同一段中介词结尾的
            return True
        if text.strip() and text[-1] in ['-', '—']:
            return True
        if "#" not in text and "*" not in text and re.search(r'[^\.?!]$', text) and re.match(r'^[a-z]',
                                                                                             next_text.lstrip()):
            return True
        if re.search(r'\([^\)]*$|\[[^\]]*$', text) and re.search(r'^[^\(\[]*[\)\]]',
                                                                 next_text):  # 前一行有一个未对应的左括号，下一行前面有一个与之对应的右括号
            return True
        # 可以先注释掉
        # if ((text.rstrip()[-1].islower() or text.rstrip()[-1] in [',']) and (next_text.lstrip()[0].isupper() or next_text.lstrip()[0] in ['(',')','"','”','“']) and "#" not in text and "#" not in next_text and self.is_merge_ngram(text, next_text)):   # 前一行小写或逗号结尾，下一行大写开头，且与标题无关，加入ngram判断
        #     return True
        if re.search(r'^#{1,3}\s?[\d\.]{1,10}$', text) and next_text.lstrip()[0].isupper():
            return True
        if len(text.strip()) == 1 and text.strip() in ['.', '·', '•', '○', '.']:
            return True
        if text and next_text and re.search(r'^#', text) and next_text[0].isupper() and len(next_text) < 20:
            return True
        return False

    def is_merge_duan(self, stripped_item, next_item):
        # 定义一个介词列表
        preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A', 'with', '&']
        # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
        if any(stripped_item.rstrip().endswith(" " + prep) for prep in preposition_list):
            return True
        if stripped_item and stripped_item[-1] in ['-', '"', ',']:
            return True
        if re.search(r'Figs?\.$', stripped_item):
            return True
        if re.search(r'\([^\)]*$|\[[^\]]*$', stripped_item) and re.search(r'^[^\(\[]*[\)\]]', next_item):
            return True
        if len(stripped_item) == 1 and stripped_item in ['.', '·', '•', '○']:
            return True
        if re.search(r'^#', stripped_item) and next_item[0].isupper() and len(next_item) < 20 and next_item.strip():
            return True
        # if next_item[0].islower() and self.is_merge_ngram(stripped_item, next_item):
        #     return True
        return False

    def step3_1_more_linefeed_duannei(self, context):
        # print(context)
        new_context = []
        for item in context:
            # 将 item 按 "\n" 分割
            item_sections = re.split(r'\n', item)
            # print(item_sections)
            section_index = 0
            while section_index < len(item_sections) - 1:  # 确保不会越界
                if self.is_merge_duannei(item_sections[section_index], item_sections[section_index + 1]) and item_sections[section_index] and item_sections[section_index + 1]:
                    item_sections[section_index] += "|删除段内换行|" + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]
                else:
                    section_index += 1  # 只有在不合并时才自增

            # 更新 item 以反映合并的段落
            item = '\n'.join(item_sections)
            new_context.append(item)
        return new_context

    def step3_2_more_linefeed_duan(self, context):
        index = 0
        while index < len(context):
            item = context[index]

            # 合并以小写字母或特定标点符号开头的段落
            stripped_item = item.strip()
            # print(stripped_item)
            if index >= 0:
                if index > 0 and stripped_item and context[index - 1][-1] not in ['.', '!', '?', '|',
                                                                                  ':'] and not re.search('#',
                                                                                                         stripped_item) and (
                        stripped_item[0].islower() or stripped_item[0] in ["(", "[", ")", "]", "."]) and not re.search(
                    '^[a-z]\s?\.', stripped_item.lstrip()):
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
                        if index - 2 and len(re.split(r'\n', context[index - 2])) > 1 and context[index - 2][
                            -1] not in ['.', '!', '?']:
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
                if index + 1 < len(context) and re.search(r'\([^\)]*$|\[[^\]]*$', stripped_item) and re.search(
                        r'^[^\(\[]*[\)\]]', context[index + 1]):
                    # 前一段有左半边括号，后一段有右半边括号，连接两段
                    if index + 1 < len(context) and "#" not in context[index + 1] and not re.search(r'^[Ff]ig', context[
                        index + 1].lstrip()):
                        # 合并到下一个 item
                        context[index] = item.rstrip() + "|删除段之间换行-6|" + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue
                elif index + 1 < len(context) and re.search(r'\([^\)]*$|\[[^\]]*$', stripped_item) and not re.search(
                        r'^[^\(\[]*[\)\]]', context[index + 1]):
                    # 前一段有左半边括号，后一段没有与之对应的括号，说明左括号后半段不完整，直接把左括号以后删掉
                    context[index] = re.sub(r'[^\(\)\[\]]\(.*$', r'', item)
                    index = index - 1
                    continue
                elif index + 1 < len(context) and self.is_merge_duan(stripped_item,
                                                                     context[index + 1]) and stripped_item is not None:
                    if index + 1 < len(context) and "#" not in context[index + 1] and not re.search(r'^[Ff]ig', context[
                        index + 1].lstrip()):
                        # 合并下一个 item
                        context[index] = item.rstrip() + "|删除段之间换行-4|" + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue

                elif index + 1 < len(context) and re.search(r'^[\d\.]{1,10}$', stripped_item) and re.search(r'#',
                                                                                                            context[
                                                                                                                index + 1].lstrip()):
                    # 上一段只有一个序号下一段是标题    例  【1】1.  【2】 ## 标题     把序号插在 #和标题中间 形成 ## 1.标题
                    match = re.match(r"(#+)\s+(.*)", context[index + 1].lstrip())
                    if match:
                        part1 = match.group(1)  # 获取 ## 部分
                        part2 = match.group(2)  # 获取标题内容部分
                        # 合并下一个 item
                        context[index] = "删除段之间换行-7" + part1 + " " + stripped_item + " " + part2
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue
            index += 1
            # print(context)

        return context
    def step4_is_mulupage(self,duans):
        """
        目录页的特点:
        1.文章前几页
        2.可能存在多个\.的情况(参考文献处理中已经把\.多的页给删掉了)
        3.循环context，item长度短数量多
        :param context: 文本信息
        :param page_num: 页码
        :return: context
        """
        # 对文本进行分类判断
        # hypothesis_template = "The format of this text belongs to {}"
        # classes_verbalized = ["Text content", "catalogue"]

        short_item_num = 0
        lines_num = 0
        catalogue1_num = 0
        catalogue2_num = 0
        for item in duans:
            # if len(item.strip()) <= 200:
            #     short_item_num += 1
            lines = re.split(r"\n", item.strip())
            for line in lines:
                lines_num+=1
                if re.search('\.{8,10}',line) or re.search('^([·]|[\d\.\s]{1,10})',line.strip()):
                    catalogue1_num += 1

                # if zeroshot_classifier(line,classes_verbalized,hypothesis_template=hypothesis_template,multi_label=False)["labels"][0] == "catalogue":
                #     catalogue2_num += 1

        # print(catalogue1_num,catalogue2_num,lines_num)
        if catalogue1_num > lines_num * 0.5:
            duans.insert(0, "(本页删除)本页使用特征判断为目录页")
        # if catalogue2_num > lines_num * 0.5:
        #     duans.insert(0, "(本页删除)本页使用模型判断为目录页")
        return duans

def clean_text(text,lang):
    sp = speicalProces()

    split_token = "\n\n"
    # 切分一下数据
    duans = text.split(split_token)
    result = []
    """
    step1:删除图片的描述
    step2:页眉页脚的判断
    step3_1:多于换行
    step3_2:缺少换行
    step4:目录页判断
    step5:正则替换
    step6:参考页判断
    """
    # 删除图片描述
    duans = sp.step1_delete_photo_describe(duans)
    duans = sp.step2_is_pagefoot(duans,lang)
    # duans = sp.step3_1_more_linefeed_duannei(duans)
    # duans = sp.step3_2_more_linefeed_duan(duans)
    duans = sp.step4_is_mulupage(duans)
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
    # duans = sp.step4_is_shortpage(result)
    text = split_token.join(result)
    text = sp.is_cankaopage(text, lang)
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

fw = open("C:/pycharm/orc识别pdf清洗数据/pdf/clean_json/reclean1_guidelines_ly_gptpdf.jsonl", "w", encoding="utf-8")
with open("C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\guidelines_ly_gptpdf_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    sampled_lines = random.sample(lines, 2000)
    for items in tqdm(sampled_lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "c9a5fcf2-4373-46f2-b910-bc2b87a20154":
            # print(item)
            # print(detect(item['text']))
            # if detect(item['text']) == "zh-cn":
            #     lang = "zh"
            # else:
        lang = item['lang']

        page_num = item['attr']['page_num']
        print(page_num)
        text = item['text']
        text = clean_text(text,lang)
        text = post_process(text)
        # print(context)
        item["text"] = text
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        print("*" * 100)
        fw.write(item + "\n")


