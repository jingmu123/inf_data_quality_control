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
    r''
],
[
    r'(\n\s*[a-zA-Z\.]\s*\n)',
    r''
],
[
    r'([^\n]*Copyright[^\n]*)',
    r''
],
[
    r'(ISBN\s*[A-Z0-9-]*)',
    r''
],
[
    r'(👍|▶|●|©|®|([^\n]*↑[^\n]*)|†|¶|║|§|∧|™|■|❏|□|✓|✔|❍|😃|�|∑|✦|❤️|❤|☆|★)',
    r''
],
[
    r'(\(\s?\b([Ff]igure[s]?|Section|diagram|Appendix|Box|[Ss]ource[s]?|[Ff]igs?|p|FIGURE)\b[^\)\n]*\))',
    r''
],

[
    r'((\([^\(]{0,20})\s[Ff]igures?[^\(\)]*.)',
    r''
],
[
    r'([\(]\s?[^\(]{0,50}([Tt]able|[sS]ee|见表|图)[^\)]*?[\)])',
    r''
],
[
    r'([\[]\s?[^\[]{0,50}([Tt]able|[sS]ee|见表|图)[^\]]*?[\]])',
    r''
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
    r''
],
[
    r'([^\d])(\[\s?[\dA-Za-z]{1,4}(\s{0,3}[\-–\^~—,\.]\s{0,3}[\dA-Za-z]{1,4}){0,20}\s?\])',
    r'\1'
],
[
    r'([^\d])([1-9][0-9]{1,4}(\s{0,3}[\-–,\.]\s{1,3}[1-9][0-9]{1,4}){1,20})([^\d\%]?)',
    r'\1\4'
],
[
    r'(\[\s?(\d{1,3}\s?[-,，]?\s?)+\d?\s?\]\s?\*?)',
    r''
],
[
    r'(\(\s?[IⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫa-zA-Z]?\s?[a-zA-Z]?\s?,\s?[a-zA-Z]\s?\)\s?)[。\.]',
    r''
],
[
    r'([^\d][\.,])((\s{1,3}\d+[\s\n]{1,3}){1,5}\.?)(\s?[A-Z])',
    r'\1\4'
],
[
    r'([^\d][\.,]\s?)(\d{1,4}(\s{0,3}[\-–,\.\s]\s{0,3}\d{1,4}){0,20})(\n|\s?[A-Z]|$)',
    r'\1\4'
],
[
    r'(#{1,3})\n',
    r''
],
[
    r'(\([^\(\)]*(\set[\s\xa0]{1,3}al|\d{4})[^\(\)]*\))',
    r''
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
    r'(\^\d+([\s,\-\d+]{0,6})+\^?)',
    r''
],
[
    r'(\$\^\{\d+\}\$)',
    r''
],
[
    r'([^m])(<sup>[\d+\s,a-z]{1,}</sup>)',
    r'\1'
],
[
    r'([*]{0,3}\[[^\[\]]{0,50}\d{4}[^\[\]]{0,50}\][*]{0,3})',
    r''
],
[
    r'(.*中国分类号.*)',
    r''
],
[
    r'([。！？]{1,3}\s?)(\d+([\-—，]\d+){0,3})([。！？\s]{0,3})$',   # 匹配在段落结尾出现的  \d+。或 。\d+
    r'\1\4'
],
# 27 28一定要分开只能一边有中文，否则会将中文中间的数字都删掉，且这里的标点只能是表示句子结束的标点，半句出现数字是常见的
[
    r'([。！？]\s?)(\d+([\-—，,]\d+){0,3})([。！？\u4e00-\u9fa5])',    # 匹配[。！？,]\d+[。！？,\u4e00-\u9fa5]
    r'\1\4'
],
[
    r'([。！？\u4e00-\u9fa5]\s?)(\d+([\-—，,]\d+){0,3})([。！？])',  # 匹配[。！？,\u4e00-\u9fa5]\d+[。！？,]
    r'\1\4'
],
[
    r'([\u2070-\u2079\u2080-\u2089¹]+)',
    r''
],
[
    r'([\(（] *(\d+[\-,]?[A-Za-z]+) *[\)）])',
    r''
],
[
    r'(^\d$)',
    r''
],
[
    r'((\\+\[\d+[ ,\-\d]*\\+\])|\*+)',
    r''
]


]

context_pattern = [
    [r'(¬\s*)', r''],
    [r'(\(\s*\))', r''],
]

# nlp = spacy.load("en_core_web_trf")
nlp = spacy.load("en_core_web_sm")

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
                duan = re.sub(rf'{escaped_least_text}', r'', duan)
            lines = duan.split('\n')
            for line in lines:
                # print(line.strip())

                if re.search('^([#*]{0,5}).{0,5}\s?([Ff]igs?(ure)?s?|FIGS?(URE)?s?|图)[\s\d\.]',line.strip()) or re.search('\.(png|jpg|PNG|JPG)',line.strip()):
                    escaped_least_text = re.escape(line)
                    # print(escaped_least_text)
                    try:
                        duan = re.sub(rf'{escaped_least_text}', r'', duan)
                    except re.error as e:
                        print(f"Regex error: {e}")
                # print("*" * 50)
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
                duans[0] = ''
            elif first_line_score > 8000 and not re.search("#",first_line) and not re.search('\|',first_line) and len(first_line) < 150 and re.search(r'[A-Z][a-z]{1,}\s[A-Z][a-z]{1,}',first_line):
                duans[0] = ''

            if last_paragraph_score > 4000 and not re.search('\|',last_paragraph) and len(last_paragraph) < 150 and re.search(r'[A-Z][a-z]{1,}\s[A-Z][a-z]{1,}',last_paragraph):
                duans[-1] = ''
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
        if re.search(r'^#{0,5}\s?(\d+[\.,\s]?){0,5}$', text) and re.search(r'^#{0,5}\s?[A-Z]',next_text):  # 匹配段落中只有序号且下一段是大写开头的情况 都可以带#
            return True
        preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A', 'with', '&',
                            'And', 'their', 'his', 'her','that']
        # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
        if any(text.rstrip().endswith(" " + prep) for prep in preposition_list) and not re.search("^#",next_text.strip()):
            return True
        if text and text[-1] in ['-', '"', ',']:
            return True
        if text.strip() and next_text.strip() and text.strip()[-1].islower() and next_text.strip()[0].islower():
            return True
        return False

    def is_merge_duan(self, stripped_item, next_item):
        # 定义一个介词列表
        if re.search(r'^#{0,5}\s?(\d+[\.,\s]?){0,5}$', stripped_item) and re.search(r'^#{0,5}\s?[A-Z]',next_item):  # 匹配段落中只有序号且下一段是大写开头的情况 都可以带#
            return True
        preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A', 'with', '&',
                            'And', 'their', 'his', 'her','that']
        # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
        if any(stripped_item.rstrip().endswith(" " + prep) for prep in preposition_list) and not re.search("^#", next_item.strip()):
            return True
        if stripped_item and stripped_item[-1] in ['-', '"', ',']:
            return True
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
                if self.is_merge_duannei(item_sections[section_index],item_sections[section_index + 1]):
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
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
            if index >= 0:
                if index + 1 < len(context) and self.is_merge_duan(stripped_item,context[index + 1]) and stripped_item is not None:
                    if index + 1 < len(context) and not re.search(r'^[Ff]ig', context[
                        index + 1].lstrip()):
                        # 合并下一个 item
                        context[index] = item.rstrip() + " " + context[index + 1].lstrip().lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue
            index += 1
            # print(context)

        return context


    def get_person_idx(self, item):
        doc = nlp(item)
        person_block = []
        person_num = 0
        # print(doc.ents)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if len(person_block) == 0:
                    person_block.append([ent.start_char, ent.end_char])
                elif ent.end_char - person_block[-1][-1] > 5:
                    person_block.append([ent.start_char, ent.end_char])
                else:
                    person_block[-1][-1] = ent.end_char
                person_num += 1
        return person_block, person_num

    def step4_rm_cite(self, item):
        cite_tag = []
        cite_index = 1 if len(re.findall(r'\[\d+\]', item)) > 0 else 0
        cite_year = 1 if len(
            re.findall(r'\[\d\d\d\d\]', item) or re.findall(r'\.\s?\b\d{4}\b', item) or re.findall(r'\b\d{4}\b\s?[;\.]',
                                                                                                   item)) else 0  # 年份，比如 . 2010 、 2010;
        cite_page = 1 if len(re.findall(r'\d+\s?:\d+\s?[–-]\s?\d+', item)) else 0
        cite_page2 = 1 if len(re.findall(r'[\.,]\s?\d+\s?[–-]\s?\d+[\.,]', item)) else 0
        cite_J = 1 if len(re.findall(r'\[[Jj]\]', item)) else 0
        cite_doi = 1 if " doi " in item else 0
        cite_etal = 1 if (" et al" in item or 'et\u00A0al' in item or 'et al' in item) else 0
        cite_vol = 1 if (" vol. " in item or " Vol " in item or " Vol. " in item or " vol " in item) else 0
        cite_pp = 1 if (re.search("\s[Pp]{1,2}(\.)?\s",item)) else 0
        # cite_page = 1 if len(re.search(r'\.\s?\b\d{4}\b',item)) else 0
        cite_phonenum = 1 if re.search(r" [Pp]hone:|Fax:", item) else 0
        mulu = 1 if re.search(r'[\.\s]{15,}', item) and not re.search("|",item) else 0
        cite_tag = [cite_index, cite_year, cite_J, cite_doi, cite_etal, cite_page, cite_vol, cite_phonenum, cite_pp,cite_page2]
        # if sum(cite_tag) > 1 and '|' not in item:
        #     return "参考删除-0:<u>{}</u>".format(item)
        person_block, person_num = self.get_person_idx(item)
        # 超过5个人名
        person_block_lens = [block_item[1] - block_item[0] for block_item in person_block]
        person_lens = sum(person_block_lens)
        if len(item) > 0 and person_lens / len(item) > 0.5 and len(item) > 100 and len(item) < 400:
            return "参考删除-1:<u>{}</u>".format(item)
        # 只有个名字数量
        elif person_num > 5 and '|' not in item and len(item) < 200:
            return "参考删除-2:<u>{}</u>".format(item)
        elif sum(cite_tag) > 0 and person_num > 0 and len(item) < 400:
            # print(item)
            return "参考删除-3:<u>{}</u>".format(item)
        elif mulu:
            return "目录删除:<u>{}</u>".format(item)
        else:
            return item

    def step4_removepage(self, context):
        # context 是一个列表，每个 item 是一段内容
        context_lens = len(context)
        # 用于统计有多少个段落中出现了人名
        num = 0
        mulu_num = 0
        new_context = []
        references_started = False
        for item in context:
            # 返回的item是已经被重写过的item
            # if item.strip() in ["##References","## References","## Suggested Readings","##Suggested Readings"]:
            if re.search(r'^#{1,3}\s?(Reference|Suggested Reading|参考文献|Acknowledgment|致谢)s?',item.strip()):
                references_started = True
            if references_started:
                item = "参考删除-4:<u>{}</u>".format(item)
            elif not re.search("[\u4e00-\u9fa5]",item):
                item = self.step4_rm_cite(item)
            # 新的item重新加入一个新的列表
            new_context.append(item)
            # 判断item是否被判定未参考文献
            if re.search(r'参考删除',item):
                # 如果当前段落中有人名且符合参考文献的特征
                num += 1
        # print(new_context)
        # 对整页的一个判断
        if context_lens >= 4 and num >= context_lens * 0.5 and not references_started:
            new_context.insert(0, "(本页删除)本页在超过一半的段落中发现人名且符合参考文献的特征")
            return []
        return new_context

    def is_cankaopage(self,duans,lang):
        if lang == "en":
            text = "\n\n".join(duans)
            text = re.sub(r'【\d+】', '', text)
            label = fasttext_model.predict(text.strip().replace('\n', ''))
            if label[0][0] in ['__label__cankao'] and not re.search(r'参考删除-4', text):
                # duans.insert(0, "(本页删除)本页被模型判断为参考页")
                return []
            if label[0][0] in ['__label__mulu']:
                # duans.insert(0, "(本页删除)本页被模型判断为目录页")
                return []

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
    step4:页判断
    step5:正则替换
    step6:参考页判断
    """
    # 删除图片描述
    duans = sp.step1_delete_photo_describe(duans)
    duans = sp.step2_is_pagefoot(duans,lang)
    duans = sp.step3_1_more_linefeed_duannei(duans)
    duans = sp.step3_2_more_linefeed_duan(duans)
    duans = sp.step4_removepage(duans)

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
    duans = sp.is_cankaopage(result, lang)
    deleted_context = []
    for item in duans:
        if re.search(r"(目录|参考)删除",item):
            continue
        deleted_context.append(item)

    text = split_token.join(deleted_context)



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
    context = re.sub(r'[。，\.](\s?[。，\.：；]){1,5}',r'。',context)
    context = re.sub(r'[,\.](\s+[,\.]){1,5}',r'\.',context)
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

# fw = open("C:/pycharm/orc识别pdf清洗数据/pdf/clean_json/reclean3_guidelines_ly_gptpdf.jsonl", "w", encoding="utf-8")
with open("C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\guidelines_ly_gptpdf_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    sampled_lines = random.sample(lines, 2000)
    for items in tqdm(sampled_lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "9194c2a8-809d-4632-ab5a-6358c172cb02":
        # print(item)
        # print(detect(item['text']))
        # if detect(item['text']) == "zh-cn":
        #     lang = "zh"
        # else:
        lang = item['lang']

        page_num = item['attr']['page_num']
        text = item['text']
        text = clean_text(text,lang)
        text = post_process(text)
        # print(context)
        item["text"] = text
        item = json.dumps(item, ensure_ascii=False)
        print(item)
        # print("*" * 100)
        # fw.write(item + "\n")


