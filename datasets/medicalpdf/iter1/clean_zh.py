# coding:utf-8
# https://github.com/shibing624/pycorrector?tab=readme-ov-file

import json
import re
import time

from tqdm import tqdm
import sys

from inf_data_quality_control.basic_tools import sentence_correct

sys.path.append("../../../")
# from basic_tools import sentence_correct
import threading
# 线程安全的队列
from queue import Queue
import spacy
import jieba

pattern_list_zh = [
    # fig cite
    [r"([见和]图\s?\d+\s?[。？！\.]?)", r"删除1：<u>\1</u>"],
    # 参考引用：数字类型，加入空格做泛化：[1,2 - 3, 4, 5]
    [r'(\[\s?(\d{1,3}\s?[-–,，\.]+\s?)+\d+\s?\]\s?\*?)', r"删除2：<u>\1</u>"],
    # 参考补充，一些缺少]的，以符号作为右边界
    [r"(\[\s?\"?\s?(\d{1,3}\s?[-–,\.]+\s?)+\d?\s*\*?)([。\.,，\u4e00-\u9fa5a-zA-Z\(（]\s?)", r"删除4：<u>\1</u>\3"],
    [r"([\u4e00-\u9fa5]\s[^\u4e00-\u9fa5\d~。？！]*?)(\s?\d+\s*?)(\n|。|\s\.)", r"\1删除5：<u>\2</u>\3"],
    [r"([\u4e00-\u9fa5])(\s*?\.\s*?\d+\s*?)([\(\u4e00-\u9fa5。\n])", r"\1删除6：<u>\2</u>\3"],
    [r'([\u4e00-\u9fa5》)])(\s?\d+\s?)(。|\s\.)', r"\1删除7：<u>\2</u>\3"],

    # # 参考应用的复杂格式：字母(Ia,\nb)
    [r'(\(\s?[IⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫa-zA-Z]?\s?[a-zA-Z]?\s?,\s?[a-zA-Z]\s?\)\s?)[。\.]', r"删除3：<u>\1</u>"],

    # 增加换行：两种概念情况，一种数字小标题，一种# 标题
    [r'^(?!\n)(\d\.(\d{1,2}\.){0,10}\d?)(\s?[^\d])', r'\n增加换行5:_\1\3_'],
    [r'(\u4e00-\u9fa5\s{3,}|。|？|！)(\d\.(\d{1,2}\.){0,10}\d?)(\s{1,10}[^\da-zA-Z\|%])', r'\1\n增加换行6:_\2\3_'],
    [r'^(?!\n)([#•]{1,4}\s{,4})', r'\n增加换行7:_\1_'],
    [r'。\s+(\d{1,2}\.)', r'\n增加换行8:_\1_'],
    [r'。\s?\s*?([一二三四五六七八九十]+[\.、])', r'\n增加换行9:_\1_'],
    # -------增加换行：(7)
    [r'([;；。！，,]\s?)([\(（]?\d+[）\)]\s?)', r'\1\n增加换行1:_\2_'],
    [r'([。！？]\s?)(【[\u4e00-\u9fa5]*?】)', r'\1\n增加换行2:_\2_'],
    [r'(\(\s?[一二三四五六七八九十-]+\s?\))', r'\n增加换行3:_\1_'],
    [r'([:：]\s?)(\d+[\.、]\s?[\u4e00-\u9fa5])', r'\1\n增加换行4:_\2_'],

    # 增加参考错误的参考case:[....]
    [r'(\[[…\.\*\s‘’\"]*?\])', r"删除8：<u>\1</u>"],
    [r'(\[[…\.\*\s‘’\"]*?\d+\])', r"删除9：<u>\1</u>"],
    [r'(\s?\d+\s\[\s?\d+\s?)', r"删除10：<u>\1</u>"],

    # 图引用1
    [r'(^[。\n].*?见图[a-zA-Z\d]+.*?)[。\n]', r"删除11：<u>\1</u>"],
    # 图引用2
    [r'([\(（]\s?图\s?[a-zA-Z\d]\s?[和与,，、]?\s?图\s?[a-zA-Z\d]\s?[\)）])', r"删除12：<u>\1</u>"],
    # 图引用3
    [r'(\(图[a-zA-Z\d]+\))', r"删除13：<u>\1</u>"],
    # 图注1
    [r'(图[a-zA-Z\d]+\s{0,2}[。\n]?)', r"删除14：<u>\1</u>"],
    # 图注2
    [r'(Fig[\s\.\d]+[a-zA-Z]*?[。\n]?)', r"删除15：<u>\1</u>"],

    [r'(👍|▶|●|©|®|([^\n]*↑[^\n]*)|†|¶|║|§|∧|™|■|❏|□|✓|✔|❍|▲|⭐|◎|●|۞|\s__\s|￥)', r' 特殊符号删除<u>\1</u>'],
    [r'((（|\(|〈|\[)? ?(图|表|见表|困|参见|至图|附图) ?(\d+[-|–\.\/,\s、~]+)+(\d+)?([^\n.。\u4e00-\u9fa5\d]*(）|\)|〉|\])|))',r' 图片索引删除<u>\1</u>'],
    [r'([\[](\s?\d+[\s,\.\-\]）』]+)+) ',r' 删除角标一<u>\1</u>'],
    [r'\(\s?[\-–]\d+\s?\)',r'删除角标二<u>\1</u>'],
    [r'(\b([a-zA-Z] ){3,}[a-zA-Z]?\b)',r' 删除英文噪声<u>\1</u>'],

    # 特殊case(背景|页眉|页脚)
    [r'(小狗(科研|公开|究|课|设|程)+)', r"删除16：<u>\1</u>"],
    [r'((小狗)?科研(公开|究)(课|设)？)', r"删除17：<u>\1</u>"],
    [r'^[。\n](.*?年第?\d+卷第?\d+期[。\n])', r"删除18：<u>\1</u>"],
    [r'((本文)?编辑: .*)', r"删除19：<u>\1</u>"],
    [r'(^[Aa]dd\s?[sS]?)', r"删除20：<u>\1</u>"],
    [r'(\.[Aa]dd[sS]\.?$)', r"删除21：<u>\1</u>"],
    # [r"((¶)\s?)",r"删除21:<u>\1</u>"],
    [r"(\s?[×∩‡♂¿☞®⌒�¶♀「…]\s?)", r"删除22：<u>\1</u>"],
    # [r"(\s?[\xAC00-\xD7AF]\s?)",r"删除201:<u>\1</u>"],
    [r"([^\u4e00-\u9fa5。\n\]]*)(小[狗街].{0,3}[科研葡公开设讨社花究所课系心,\d\sa-zA-Z]+\s?)([^\u4e00-\u9fa5。\n]?)",
     r"\1删除23：<u>\2</u>\3"],
    [r"(的?科研究*公*共*通*)", r"删除24：<u>\1</u>"],
    [r"(\( *\))", r"删除25：<u>\1</u>"],
    # 删除页码
    [r'(•?\s?\d{1,10}\s?•)', r"删除26：<u>\1</u>"],

    # 删除英文开头和结尾的
    # [r"(^[a-zA-Z ]+)([\u4e00-\u9fa5])",r"删除26:<u>\1</u>\2"],
    # [r'([\u4e00-\u9fa5]+)\s?([a-zA-Z\s]+)$',r"\1删除22:<u>\2</u>"],
    [r"([^\u4e00-\u9fa5。\n]+下载.*?)([\s。\n][\u4e00-\u9fa5。\n])", r"删除27：<u>\1</u>\2"],

]

context_pattern = [
    [r"[。，?!,]([。，?!,])", r"\1"],

]


class speicalProces:
    def __init__(self):
        self.sc = sentence_correct.SentenceCorrector()
        self.special_token = ["¶", ",", ".", "-", "|"]
        self.special_mapping = {
            "木": "术",
        }
        self.skip_token = ["論", "妄"]
        # self.en_nlp = spacy.load("zh_core_web_trf")
        self.zh_nlp = spacy.load("zh_core_web_sm")

    def fix_details(self, ditail_list):
        new_detail_list = []
        for detail_item in ditail_list:
            detail_pos_start = detail_item[2]
            detail_pos_end = detail_item[3]
            raw_token = detail_item[0]
            new_token = detail_item[1]
            if raw_token in ["論", "妄"]:
                continue
            if len(re.findall("\d", raw_token)) > 0:
                continue
            if len(re.findall(r"[^\u4e00-\u9fa5]", raw_token)) > 0:
                continue
            if raw_token in self.special_mapping:
                new_token = self.special_mapping[raw_token]
            new_detail_list.append([raw_token, new_token, detail_pos_start, detail_pos_end])
        return new_detail_list

    def step1_correct_error_token(self, context):
        # 单词纠错
        rank_length = 480
        context_list = []
        for pos in range(0, len(context), rank_length):
            context_list.append(context[pos:pos + rank_length])
        if len(context_list) == 0:
            return ""
        sc_result = self.sc.process_text(context_list)

        final_correct_list = []
        for item, sc_item in zip(context_list, sc_result):
            # 纠错内容后处理
            sc_details = self.fix_details(sc_item["details"])
            # 保证纠错的数量
            if len(sc_details) == 0 or len(sc_details) > 3:
                final_correct_list.append(item)
            else:
                final_content = ""
                pre_idx = 0
                for detail_item in sc_details:
                    [raw_token, new_token, detail_pos_start, detail_pos_end] = detail_item
                    final_content += "{}{}<u>纠错:{}</u>".format(item[pre_idx:detail_pos_start], new_token, raw_token)
                    pre_idx = detail_pos_end
                final_content += item[pre_idx:]
                final_correct_list.append(final_content)
        return "".join(final_correct_list)

    def step2_rm_kongge(self, context):
        context = context.lstrip().rstrip()
        content = context.split(" ")
        first_content = content[0]
        last_content = " ".join(content[1:])
        final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', last_content)
        # 多执行一次，弥补正则边界重叠问题；
        final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', final_content)
        if len(final_content) == 0:
            return final_content

        merge_piece = first_content + final_content.lstrip()[0]

        split_word = list(jieba.cut(merge_piece, cut_all=False))
        if len(split_word[-1]) > 1:
            return first_content + final_content
        return first_content + " " + final_content

    def step3_rm_noise_dig_alpha(self, context):
        # 删除单独的零碎（字母+数字）
        import numpy as np
        # 有汉字
        if len(re.findall(r'[\u4e00-\u9fa5]', context)) > 0:
            return context

        # 如果是序号
        if len(re.findall(r'[\da-zA-Z]+\.', context)) == 0:
            return context

        # # 没有数字
        # if len(re.findall(r'\d',context)) == 0:
        #     return context

        if len(context.split(" ")) == 1 or len(context.split(" ")) > 5:
            return context

        if "." in context and len(re.findall(r'[A-Z]', context)) == 0:
            return context

        split_word = [len(word) for word in context.split(" ")]
        mean_word_len = np.mean(split_word)
        if mean_word_len > 3:
            return context
        else:
            # return "本段删除1:<u>{}</u>".format(context)
            return ""

    def get_person_idx(self, context):
        doc = self.zh_nlp(context)
        person_block = []
        person_num = 0
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

    def step4_rm_cite(self, context_raw):
        context = str(context_raw)
        cite_index = 1 if len(re.findall(r'\[\d+\]', context)) > 0 else 0
        cite_year = 1 if len(re.findall(r'\d\d\d\d', context)) > 0 else 0
        cite_J = 1 if len(re.findall(r'\[[Jj]\]', context)) > 0 else 0

        cite_doi = 1 if len(re.findall(r'[dD][oO][iI]', context)) > 0 else 0
        cite_cip = 1 if len(re.findall(r'[cC][iI][pP]', context)) > 0 else 0

        cite_etal = 1 if "et al" in context else 0
        za_zhi = 1 if "杂志" in context else 0
        cite_vol = 1 if len(re.findall(r'[vV][oO][lL]', context)) > 0 else 0
        cite_jan = 1 if len(re.findall(r'[jJ][aA][nN]', context)) > 0 else 0
        cite_email = 1 if "mail" in context else 0
        cite_com = 1 if "com" in context else 0
        cite_fix = 1 if "修订" in context else 0
        cite_comm = 1 if "委员会" in context else 0
        cite_auth = 1 if "作者" in context or "主编" in context else 0
        cite_zhuanjia = 1 if "专家" in context else 0
        cite_chuban = 1 if "出版" in context else 0
        cite_rexian = 1 if "热线" in context else 0
        cite_ISBN = 1 if len(re.findall(r'[iI][sS][bB][nN]', context)) > 0 else 0

        cite_tag = [cite_index, cite_year, cite_J, cite_doi, cite_cip, cite_etal,
                    za_zhi, cite_vol, cite_jan, cite_email, cite_com,
                    cite_fix, cite_comm, cite_auth, cite_zhuanjia, cite_chuban, cite_rexian, cite_ISBN]
        if sum(cite_tag) >= 3 and len(context) < 500:
            return ""
        if sum(cite_tag) >= 2 and len(context) < 300:
            # return "参考删除-0:<u>{}</u>".format(context_raw)
            return ""

        # 基于人名判定
        person_block, person_num = self.get_person_idx(context)
        person_block_lens = [block_item[1] - block_item[0] for block_item in person_block]
        person_lens = sum(person_block_lens)

        if person_lens / len(context) > 0.3:
            # return "参考删除-1:<u>{}</u>".format(context_raw)
            return ""
        if person_num > 5:  # 超过5个人名
            # return "参考删除-2:<u>{}</u>".format(context_raw)
            return ""
        # elif cite_index and person_num > 0 and len(context) < 150:
        #     return "参考删除-3:<u>{}</u>".format(context_raw)
        #     # return ""
        else:
            return context_raw

    def is_complete(self, last_sentence, curr_sentence):
        if "|" in last_sentence or "|" in curr_sentence:
            return True
        last_sentence = last_sentence.lstrip(" ").rstrip(" ").strip("\n")
        curr_sentence = curr_sentence.lstrip(" ").lstrip("\n")

        if len(last_sentence) == 0:
            return False
        if last_sentence.strip(" ")[-1] in ["。", "？", "！", ".", "?", "!", ")"]:
            return True
        elif last_sentence.strip(" ")[-1] in ["、", "对", "与", "和", "及", "其", "但", "且", "乃", "~", "的", "由",
                                              "于", "致"]:
            return False
        # elif "#" in last_sentence or "#" in curr_sentence:
        elif len(re.findall(r'^#', last_sentence)) > 0 or len(re.findall(r'^#', curr_sentence)) > 0:
            return True
        elif len(re.findall(r'[-一二三四五六七八九十](\s\.|、)', last_sentence + curr_sentence)) > 0:
            return True
        elif len(re.findall(r'[a-zA-Z\d]$', last_sentence)) > 0 or len(re.findall(r'^[a-zA-Z\d]', curr_sentence)) > 0:
            return False

        try:
            if len(last_sentence) > 6:
                merge_sentence = last_sentence[-5:] + curr_sentence[0]

            else:
                merge_sentence = last_sentence[-2:] + curr_sentence[0]
        except:
            return True
        # print(merge_sentence)
        split_word = list(jieba.cut(merge_sentence, cut_all=False))
        # print(split_word)
        if len(split_word[-1]) > 1:
            return False
        return True

    def rm_lid_piece(self, context):
        context_list = context.split("\n")
        final_list = []
        final_list.append(context_list[0])
        idx = 1
        while idx < len(context_list):
            if self.is_complete(final_list[-1], context_list[idx]):
                final_list.append(context_list[idx])
            else:
                # print("换行删除1", final_list[-1], "-----------",context_list[idx])
                final_list[-1] = "{} {}".format(final_list[-1], context_list[idx])
            idx += 1
        return "\n".join(final_list)

    def rm_lid_context(self, context):
        context_list = context.split("\n\n")
        final_list = []
        final_list.append(context_list[0])
        idx = 1
        while idx < len(context_list):
            sent_complete = self.is_complete(final_list[-1], context_list[idx])
            if sent_complete:
                final_list.append(context_list[idx])
            else:
                # print("换行删除2",final_list[-1],context_list[idx])
                final_list[-1] = "{} {}".format(final_list[-1], context_list[idx])
            idx += 1
        return "\n\n".join(final_list)

    def step5_rm_english_noise(self, context):
        find_pattern = [
            [r"(^[a-zA-Z ]+)([\u4e00-\u9fa5])", 0],
            [r'([\u4e00-\u9fa5]+)\s?([a-zA-Z\s]+)$', -1]
        ]
        pattern = [
            [r"(^[a-zA-Z ]+)([\u4e00-\u9fa5])", r"\2"],
            [r'([\u4e00-\u9fa5]+)\s?([a-zA-Z\s]+)$', r"\1"],
        ]

        for idx, item in enumerate(find_pattern):
            [p_item, p_index] = item
            result = re.findall(p_item, context)
            # print(result)
            if len(result) == 0:
                continue
            elif len(result[0][p_index].strip().split(" ")) == 1:
                continue
            else:
                # print(result[0][p_index].strip().split(" "))
                context = re.sub(pattern[idx][0], pattern[idx][1], context)
        return context

    def step6_rm_short_context(self, context):
        context_list = context.split("\n\n")
        context_lens = [len(item) for item in context_list]
        if context.count("|") >= 3:
            return context
        if len(context_list) >= 5:
            return context
        if max(context_lens) > 100:
            return context
        elif len(context_list) > 2 and max(context_lens) >= 50:
            return context
        else:
            # print(context)
            # print("="*20)
            # return "整页删除\n\n{}".format(context)
            return ""

    def step7_rm_digital(self, context):
        res = re.findall(r"\d", context)
        no_digital = re.sub(r"\d", "", context)
        context_lens = len(list(set(no_digital.split(" "))))

        if len(res) > 8 and (context_lens) < 5:
            # return "删除32:<u>{}</u>".format(context)
            return ""
        return context


def clean_text(context, lang, sp):
    # print("-"*10)
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    pattern_list = pattern_list_zh

    # 分解处理
    result = []

    for idx, item in enumerate(context.split(split_token)):
        if idx == 0:
            item = item.lstrip().rstrip()
            res = re.findall(r"\d+", item)
            if len(res) / len(item) > 0.5:
                # item = "删除0:<u>{}</u>".format(item)
                # result.append(item)
                continue

        item = sp.step4_rm_cite(item)
        # 1.正则
        for pattern_item in pattern_list:
            item = item.lstrip(" ").rstrip(" ")
            item = re.sub(pattern_item[0], pattern_item[1], item)

        # 2.替换 固定内容（非泛化）
        for replace_item in context_pattern:
            item = re.sub(replace_item[0], replace_item[1], item)
        item = sp.step5_rm_english_noise(item)
        item = sp.step3_rm_noise_dig_alpha(item)
        item = sp.rm_lid_piece(item)
        item = sp.step2_rm_kongge(item)
        # item = sp.step1_correct_error_token(item)
        item = sp.step7_rm_digital(item)
        result.append(item)

    # 整合
    context = split_token.join(result)
    context = sp.rm_lid_context(context)
    context = sp.step6_rm_short_context(context)

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


def process_line(items, sp):
    try:
        item = json.loads(items.strip())
        context = item["text"]
        # if item["seq_id"] != "87231848-4d52-4de0-ab9c-84ec43bb7acc":
        #     return
        # if need
        lang = item["lang"]

        context = clean_text(context, lang, sp)
        context = post_process(context)
        item["text"] = context
    except:
        print("error")
        exit(0)
    item = json.dumps(item, ensure_ascii=False)
    return item


# save_file = "C:/Users/Administrator/Desktop/333.json"
input_file = "C:/Users/Administrator/Desktop/222.json"
with open(input_file, "r", encoding="utf-8") as file:
    sp = speicalProces()
    items = file.readlines()
    for item in items:
        item = json.loads(item.strip())
        context = item["text"]
        print(context)
        lang = item["lang"]
        context = clean_text(context, lang, sp)
        context = post_process(context)
        item["text"] = context
        print("------------------------------------------------")
        print(context)