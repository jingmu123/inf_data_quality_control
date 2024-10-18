import json
import os
import re
import random

import inflect
import jieba
import kenlm
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm
inflect = inflect.engine()
import kenlm
from nltk.tokenize import word_tokenize
from collections import defaultdict
model = kenlm.LanguageModel(r"C:\Users\Administrator\Desktop\4k_gram.klm")




url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"



pattern_list = [
    [r'([\.,]\s)(\d{1,3}[\s–,\d{1,3}]{0,20})([A-Z]|$)',r'\1\3'],   # 无关数字

    [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www|p\.|N[oO]\.)s?[\s\.][^\(\)]*\))', r''],
    [r'(\(\s?[^\(\)]*)([\.,;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.][^\(\)]*)(\))', r'\1)'],# 固定格式  带有（）的图片表格描述 附录描述 协议描述
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version)s?[^\(\)]*\))',r''],

    [r'(Disclaimer.*)',r''],
    [r'(\d+\s([–,]\s\d+\s){1,20})[^nm]',r''],  # 删除内容中出现的无关数字 可能会造成误删

    [r'(^\s{0,3}\(\s?\d+\s?\)\s?($|\n))',r''],
    [r'(\*\*Notes?:\*\*[^\|]*(http|www)[^\|]*)',r''],

    [r'( et al )([\s–,\d{1,3}]{1,20})',r'\1'],  # dovepress文件中的数字较难删除，添加比较固定的特殊格式的无关数字
    [r'[^\n]*Trial Registration[^\n]*',r''],    # 句子Trial Registration   注册信息

    [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|p\.|N[oO]\.|Participant \d+|Provider \d+|version)s?[^\[\]]*(\\)?\])', r''],  # 方括号

]


class speicalProces:
    def __init__(self):
        pass
    def step1_wuguantext_following(self, context):
        new_context = []
        references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(
                    r'^(Disclosure|Acknowledgment|Disclaimer|Institutional Disclaimer|Data [Ss]haring [Ss]tatement|Informed Consent|Informed Consent for Publication|Data-Sharing Statement|Author contributions)s?',
                    item.strip()) :   # 付费下载...  拨打电话...  后面直接都删掉
                references_started = True

            if re.search(r'^(Ethics Statement|Ethics?|Ethics Approval|Ethical Approval|Statement of Ethics|Ethics Approval and Informed Consent|Funding|Consent for publication|Author Contributions|Compliance with Ethical Standards|Study Approval Statement|Ethical Consideration|Data availability|Supporting Documents|Registration|Data sharing statement)[$\n]', item.strip()):
                references_started = True

            if re.search(r'Consent Statement',item.strip()):
                references_started = True
            if references_started:
                # item = "无关删除-1:<u>{}</u>".format(item)
                item = ''

            new_context.append(item)

        return new_context

    def step2_Spaced_delete(self, context):


        before_introduction = 0
        before_introduction_index = []

        for index,item in enumerate(context):

            if re.search('^\*\s+',item) and index <= 3:
                before_introduction_index.append(index)
                before_introduction += 1

            if re.search('^([\*#]{0,5}Introduction|[\*#]{0,5}(Background|Abstract)|Dear editor)',item):
                before_introduction_index.append(index)
                before_introduction -= 1
            elif re.search(r'[\*#]{0,5}(Background|Purpose)',item):
                before_introduction_index.append(index+1)
                before_introduction -= 1
                break


        if before_introduction <= 0 and len(before_introduction_index) >= 2:
            start_index = before_introduction_index[0]
            end_index = before_introduction_index[-1]
            # print(start_index, end_index)
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index-1):
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                # context[i] = "间距删除-1:<u>{}</u>".format(context[i])
                context[i] = ""
            # 对于匹配到的最后一段有不同的情况，需要针对不同的情况进行去删除
            if re.search(r'\n\*\*',context[end_index - 1]):
                split_content = context[end_index - 1].split('\n**', 1)
                # context[end_index-1] = "间距删除-2:<u>{}</u>".format(split_content[0]) + '\n**' + split_content[1]
                context[end_index - 1] = '\n**' + split_content[1]
            else:
                # context[end_index-1] = "间距删除-3:<u>{}</u>".format(context[end_index-1])
                context[end_index-1] = ""

        return context

    def get_score(self, sentence):
        tokenize_text = word_tokenize(sentence)
        final_text = " ".join(tokenize_text)
        if len(tokenize_text) == 0:  # 检查分词后是否为空
            return float('inf')  # 或者返回其他适当的值，如 0 或者某个高分
        score = model.score(final_text, bos=False, eos=False)
        length = len(tokenize_text)
        score = (10 ** (-score / length))
        return score
    def step3_ngram_deletenum(self, context):
        """
        循环 context 里面每个 item, 切分 item, 切分后每个最小单位就是一行内容，使用 ngram 判定数字
        :param context:
        :return: new_context
        """
        new_context = []

        for item in context:
            item_sections = re.split(r'\n', item)
            new_item_sections = []
            for section in item_sections:
                # print(section)

                section = section.strip()
                if len(section) == 0:
                    new_item_sections.append(section)
                    continue
                else:
                    pattern = r'\s\d+(\s?[\-–\.,]?(to|and)?\s?\d+){0,10}\s'
                    best_score = self.get_score(section)

                    while True:
                        matches = list(re.finditer(pattern, section))
                        if not matches:
                            break

                        # 找到所有匹配的数字及其位置
                        numbers_with_positions = [(match.group(), match.start(), match.end()) for match in matches]

                        # 标记是否更新了文本
                        updated = False

                        for num, start, end in numbers_with_positions:
                            # print(num,start,end)
                            # 如果是开头的数字，他可能是序号直接跳过
                            if start >= 0 and start < 4:
                                continue
                            # 特殊符号后面的数字也都是合理了 不用检查直接跳过
                            elif start > 0 and (
                                    section[start - 1] in ['$', '>', '<', '='] or section[start - 2] in ['$', '>', '<','=']):
                                continue
                            # 使用位置进行替换
                            modified_text = section[:start] + section[end:]
                            modified_score = self.get_score(modified_text)

                            if modified_score < best_score:
                                best_score = modified_score  # 更新当前最优分数
                                section = modified_text  # 将分数低的文本重新赋给text
                                updated = True
                                break

                        # 如果没有更新文本，跳出循环
                        if not updated:
                            break
                    new_item_sections.append(section)

            new_context.append('\n'.join(new_item_sections))

        return new_context
    def step4_rm_kongge(self, context):
        context = context.lstrip().rstrip()
        content = context.split(" ")
        first_content = content[0]
        last_content = " ".join(content[1:])
        final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', last_content)
        # 多执行一次，弥补正则边界重叠问题；
        final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', final_content)
        if len(final_content) == 0:
            return first_content

        merge_piece = first_content + final_content.lstrip()[0]

        split_word = list(jieba.cut(merge_piece, cut_all=False))
        if len(split_word[-1]) > 1:
            return first_content + final_content
        return first_content + " " + final_content

def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    # 分解处理
    result = []
    sp = speicalProces()
    context = context.split(split_token)
    if len(context) <= 25:
        context = ""
        return context

    context = sp.step1_wuguantext_following(context)
    context = sp.step2_Spaced_delete(context)
    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)
        if lang == "zh":
            item = sp.step4_rm_kongge(item)
        result.append(item)
    context = sp.step3_ngram_deletenum(result)
    for index,item in enumerate(context):
        print(index,item)

    context = split_token.join(context)

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
    # 对多标点进行替换
    context = re.sub(r'[。，](\s?[。，：；]){1,5}',r'。',context)
    context = re.sub(r'([,\.?])(\s?[?,\.]){1,5}',r'\1',context)
    return context

fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean_dovepress_preformat_sample.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\dovepress_preformat_sample.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "64826a6a-4ace-4019-92e1-e37c127bd884":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0',r' ',context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
