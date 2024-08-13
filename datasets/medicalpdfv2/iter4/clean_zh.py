# coding:utf-8
# https://github.com/shibing624/pycorrector?tab=readme-ov-file
import itertools
import json
import re
import time
from collections import defaultdict

from tqdm import tqdm
import sys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import transformers
sys.path.append("../../../")
# from basic_tools import sentence_correct
import threading
# 线程安全的队列
from queue import Queue
import spacy
import jieba
import numpy as np
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer


pattern_list_zh = [
    # fig cite
    # [r"([见和]图\s?\d+\s?[。？！\.]?)", r"删除1：<u>\1</u>"],
    # 参考引用：数字类型，加入空格做泛化：[1,2 - 3, 4, 5]
    [r'(\[\s?(\d{1,3}\s?[-–,，\.]+\s?)+\d+\s?\]\s?\*?)', r"删除2:<u>\1</u>"],
    # 参考补充，一些缺少]的，以符号作为右边界
    [r"(\[\s?\"?\s?(\d{1,3}\s?[-–,\.]+\s?)+\d?\s*\*?)([。\.,，\u4e00-\u9fa5a-zA-Z\(（]\s?)", r"删除4:<u>\1</u>\3"],
    # [r"([\u4e00-\u9fa5]\s[^\u4e00-\u9fa5\d~。？！]*?)(\s?\d+\s*?)(。|\s\.)", r"\1删除5:<u>\2</u>\3"],
    # [r"([\u4e00-\u9fa5])(\s*?\.\s*?\d+\s*?)([\(\u4e00-\u9fa5。\n])", r"\1删除6:<u>\2</u>\3"],
    # [r'([\u4e00-\u9fa5》)])(\s?\d+\s?)(。|\s\.)', r"\1删除7:<u>\2</u>\3"],

    # # 参考应用的复杂格式：字母(Ia,\nb)
    [r'(\(\s?[IⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫa-zA-Z]?\s?[a-zA-Z]?\s?,\s?[a-zA-Z]\s?\)\s?)[。\.]', r"删除3:<u>\1</u>"],

    # 增加换行：两种概念情况，一种数字小标题，一种# 标题
    [r'([:：]\s?)(\d+[\.、]\s?[\u4e00-\u9fa5])', r'\1\n\2'],
    [r'^(?!\n)(\d\.(\d{1,2}\.){0,10}\d?)( ?[^\d])', r'\n\1\3'],
    [r'(\u4e00-\u9fa5\s{3,}|。|？|！)(\d\.(\d{1,2}\.){0,10}\d?)(\s{1,10}[^\da-zA-Z\|%])', r'\1\n增加换行6:\2\3'],
    # [r'^(?!\n)([#•]{1,4}\s{,4})', r'\n增加换行7:_\1_'],
    [r'([。:：;.?？!！"”>》\u4e00-\u9fa5A-Za-z]) *(\d{1,2}\.)(?!( ?\d+))',r'\1\n增加换行7:\2'],
    [r'[。\u4e00-\u9fa5A-Za-z] *(\d{1,2} *\.)(?! *[\d])', r'\n\1'],#序号换行
    [r'[。\u4e00-\u9fa50-9A-Za-z] *?([一二三四五六七八九十]+[\.、])', r'\n增加换行9:\1'],#[。\u4e00-\u9fa50-9A-Za-z] *?([一二三四五六七八九十]+[\.、])
    # -------增加换行：(7)
    [r'([ ;；。！，,\.] ?)([\(（] *\d+ *[）\)] ?)', r'\1\n\2'],
    [r'([。！？] ?)(【[\u4e00-\u9fa5]*?】)', r'\1\n增加换行2:\2'],
    [r'[^#\s] ?([\(（] ?[—一二三四五六七八九十-]+ ?[\)）][^。])', r'\n增加换行3:\1'],
    [r'([\u4e00-\u9fa5)）])([A-E] ?\. ?[\u4e00-\u9fa5])',r'\1\n\2'],

    [r'[，,。？！.?!]([【[〖] ?[\u4e00-\u9fa5]{2,5} ?(\d* )?[〗\]】])(.*)',r'\n\1\3'],
    [r'([【[〖] ?[\u4e00-\u9fa5]{2,5} ?(\d* )?[〗\]】])(.*)([【[〖] ?[\u4e00-\u9fa5]{2,5} ?(\d* )?[〗\]】])(.*)',r'\1\3\n\4\6'],


    # 增加参考错误的参考case:[....]
    [r'(\[[…\.\*\s‘’\"]*?\])', r"删除8:<u>\1</u>"],
    [r'([[【][…[\.\* ‘’\"]*?[\dA-Za-z]+ ?\])(?=\n|$)', r"删除9:<u>\1</u>"],
    [r'(\s?\d+\s\[\s?\d+\s?)', r"删除10:<u>\1</u>"],


    [r'(\s?(👍|▶|●|©|®|\(?↑\)?|†|¶|║|§|∧|™|■|◆|♕|ኤ|♦|ż|❏|□|✓|✔|❍|▲|⭐|◎|●|۞|\s__\s|￥|∩|‡|♂|¿|☞|⌒|�|\$|￼|भ|±|£|♀|œ|¾|ä|も|へ|\^|す|&|➪|Ø|「|\s…\s)\s?)', r'删除28:<u>\1</u>'],
    [r'((（|\(|〈|\[) ?(图|围|表|附|见|见表|困|参见|至图|附图) ?(\d+[-|–\.\/,\s、~]+)+(\d+)?([^\n.。\u4e00-\u9fa5\d]*(）|\)|〉|\])))',
     r'删除29:<u>\1</u>'],
    [r'(图|围|表|附|见表|困|参见|附图)( *(\d+[-|–\.\/, 、~]+)+(\d+)?([^\n.。\u4e00-\u9fa5\d]*))', r'\1删除30:<u>\2</u>'],
    [r'(?<!^)(?<!\n)([\[]( ?\d+[\s,\.\-\]）』]+)+)',r'删除31:<u>\1</u>'],#[26]
    [r'(\(\s?[\-–]\d+\s?\))',r'删除32:<u>\1</u>'],
    [r'([\(（]\s?\d{2,}\s?[\)）]\n)', r'删除33:<u>\1</u>'],
    [r'(\b([a-zA-Z] ){3,}[a-zA-Z]?\b)', r'删除34:<u>\1</u>'],
    [r'(?<=\n)((##)? ?[A-Za-z.\-@]{1,3}|[\u4e00-\u9fa5])(?=\n|$)|(?<=^)((##)? ?[A-Za-z.\-@]{1,3}|[\u4e00-\u9fa5])(?=\n|$)',r'删除35:<u>\1\3</u>'],
    [r'(?<=。|\.)( ?\(\d+\))(?=\n|$)',r'删除36:<u>\1</u>'],
    [r'(?<=^)([A-Za-z ]*[Ff]i[Gg](ures?)?[A-Za-z 0-9]*\.?[0-9 ]*?)(?=\n|$)|(?<=\n|。|\.)([A-Za-z ]*[Ff]i[Gg](ures?)?[A-Za-z 0-9]*\.?[0-9 ]*?)(?=\n|$)',r'删除37:<u>\1\3</u>'],
    [r'(?<=^)([\(（【\[]\d+[\.-]\d+[\)）】\]])(?=\n|$)|(?<=\n)([\(（【\[]\d+[\.-]\d+[\)）】\]])(?=\n|$)',r'删除38:<u>\1\2</u>'],#(15.52) (16-12)
    [r'(Chapter[ 0-9]*(\.\d)*[ \n])',r'删除39:<u>\1</u>'],#Chapter 3
    [r'(?<=^)([\(（] ?(引 *自 *)?[\u4e00-\u9fa5]( *[\u4e00-\u9fa5] *){1,2} ?[）\)]?)(?=\n|$)|(?<=\n)([\(（] ?(引 *自 *)?[\u4e00-\u9fa5]( *[\u4e00-\u9fa5] *){1,2} ?[）\)]?)(?=\n|$)',r'删除40:<u>\1\4</u>'],#（人名）
    [r'([,，:：;；。.~\-—])(( ?[,，:：;；。~] ?){2,})',r'\1删除多余符号：<u>\2<u>'],
    [r'((?:https?:\/\/)?(?:www\.)[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^\s]*)?)',r'删除网址：<u>\1<u>'],
    [r'([\(（][^\u4e00-\u9fa5\nA-Za-z%π//]*?( ?[–\-= ，,)] ?\d+){2,}[^\u4e00-\u9fa5\nA-Za-z%π//]*?[）\)])',r'删除无关数字2：<u>\1<u>'],#( 2 53-3-3 )
    [r'([(（][^\n()（）\\]*?参见[^\n()（）\\]*?[）)])',r'删除参见：<u>\1<u>'],






    # 图引用1
    [r'(^[。\n].*?见图[a-zA-Z\d]+.*?)[。\n]', r"删除11:<u>\1</u>"],
    # 图引用2
    [r'([\(（]\s?图\s?[a-zA-Z\d]\s?[和与,，、]?\s?图\s?[a-zA-Z\d]\s?[\)）])', r"删除12:<u>\1</u>"],
    # 图引用3
    [r'(\(图[a-zA-Z\d]+\))', r"删除13:<u>\1</u>"],
    # 图注1
    [r'(图[a-zA-Z\d]+\s{0,2}[。\n]?)', r"删除14:<u>\1</u>"],
    # 图注2
    [r'(Fig[\s\.\d]+[a-zA-Z]*?[。\n]?)', r"删除15:<u>\1</u>"],



    # 特殊case(背景|页眉|页脚)
    # [r'(小狗(科研|公开|究|课|设|程)+)', r"删除16:<u>\1</u>"],
    # [r'((小狗)?科研(公开|究)(课|设)？)', r"删除17:<u>\1</u>"],
    [r'^[。\n](.*?年第?\d+卷第?\d+期[。\n])', r"删除18:<u>\1</u>"],
    [r'((本文)?编辑: .*)', r"删除19:<u>\1</u>"],
    [r'(^[Aa]dd\s?[sS]?)', r"删除20:<u>\1</u>"],
    [r'(\.[Aa]dd[sS]\.?$)', r"删除21:<u>\1</u>"],
    # [r"(\s?[\xAC00-\xD7AF]\s?)",r"删除201:<u>\1</u>"],
    [r"([^\u4e00-\u9fa5。\n\]]*)(小[狗街].{0,3}[科研葡公开设讨社花究所课系心,\d\sa-zA-Z]+\s?)([^\u4e00-\u9fa5。\n]?)",
     r"\1删除23:<u>\2</u>\3"],
    # [r"(的?科研究*公*共*通*)", r"删除24:<u>\1</u>"],
    # [r"(\( *-* *\))", r"删除25:<u>\1</u>"],
    # 删除页码
    [r'(•?\s?\d{1,10}\s?•)', r"删除26:<u>\1</u>"],
    [r'(?<=^)([-.]* ?[\d①②③④⑤⑥⑦⑧⑨⑩]+[\.-]?\d* ?[-.]*)(?=\n|$)|(?<=\n|。)([-.]* ?[\d①②③④⑤⑥⑦⑧⑨⑩]+[\.-]?\d* ?[-.]*)(?=\n|$)',r'删除无关数字:<u>\1\2</u>'],

    # 删除英文开头和结尾的
    # [r"(^[a-zA-Z ]+)([\u4e00-\u9fa5])",r"删除26:<u>\1</u>\2"],
    # [r'([\u4e00-\u9fa5]+)\s?([a-zA-Z\s]+)$',r"\1删除22:<u>\2</u>"],
    [r"([^\u4e00-\u9fa5。\n]+下载.*?)([\s。\n][\u4e00-\u9fa5。\n])", r"删除27:<u>\1</u>\2"],

]

context_pattern = [
    [r"[。，?!,]([。，?!,])", r"\1"],

]


# ner_pipeline = pipeline(Tasks.named_entity_recognition, 'damo/nlp_raner_named-entity-recognition_chinese-base-generic')
class speicalProces:
    def __init__(self):
        # self.sc = sentence_correct.SentenceCorrector()
        self.special_token = ["¶", ",", ".", "-", "|"]
        self.special_mapping = {
            "木": "术",
        }
        self.skip_token = ["論", "妄"]
        # self.en_nlp = spacy.load("zh_core_web_trf")
        # self.zh_nlp = spacy.load("zh_core_web_sm")
        self.zh_nlp = spacy.load("zh_core_web_sm")
        # self.ner_pipeline = pipeline(Tasks.named_entity_recognition, 'damo/nlp_raner_named-entity-recognition_chinese-base-generic')
        self.zeroshot_classifier = transformers.pipeline("zero-shot-classification", model="deberta-v3-large-zeroshot-v2.0")

        self.model = AutoModelForSequenceClassification.from_pretrained("autonlp-Gibberish-Detector-492513457",
                                                                   use_auth_token=True)
        self.tokenizer = AutoTokenizer.from_pretrained("autonlp-Gibberish-Detector-492513457", use_auth_token=True)

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

    def dict_merge(self,xy_num, set_x, flag=True):

        sorted_keys = sorted(xy_num.keys())
        # 初始化
        merged_dict = defaultdict(float)
        current_key_group = []
        current_value_sum = 0
        # 遍历排序后的 keys 并进行合并
        for key in sorted_keys:
            if not current_key_group:
                current_key_group.append(key)
                current_value_sum += xy_num[key]
            else:
                if key - current_key_group[-1] <= 18:
                    current_key_group.append(key)
                    current_value_sum += xy_num[key]
                else:
                    # 计算当前组的平均 key 和累加的 value
                    avg_key = sum(current_key_group) / len(current_key_group)
                    merged_dict[avg_key] = current_value_sum
                    # 重置组
                    current_key_group = [key]
                    current_value_sum = xy_num[key]
        # 最后一组的处理
        if current_key_group:
            avg_key = sum(current_key_group) / len(current_key_group)
            merged_dict[avg_key] = current_value_sum

        if flag:  # 左侧  按照值（value）的降序和键（key）的升序排序
            res_left = dict(sorted(merged_dict.items(), key=lambda x: (-x[1], x[0])))
            # print(res_left)
            if len(res_left) >= 2:
                keys = list(res_left.keys())
                values = list(res_left.values())
                if values[0] - values[1] <= 6 and keys[1] < keys[0]:
                    keys[0], keys[1] = keys[1], keys[0]
                    values[0], values[1] = values[1], values[0]
                    res_left = dict(zip(keys, values))
            # first_key = next(iter(res_left.keys()))
            for x in res_left.keys():
                if x < set_x / 3 and res_left[x] >= 4:
                    first_key = x
                    break
                else:
                    first_key = 0
            # print(res_left)
        else:  # 右侧  按照值（value）的降序和键（key）的降序排序
            res_right = dict(sorted(merged_dict.items(), key=lambda x: (x[1], x[0]), reverse=True))
            # print(res_right)
            if len(res_right) >= 2:
                keys = list(res_right.keys())
                values = list(res_right.values())
                if values[0] - values[1] <= 6 and keys[1] > keys[0]:
                    keys[0], keys[1] = keys[1], keys[0]
                    values[0], values[1] = values[1], values[0]
                    res_right = dict(zip(keys, values))
            # first_key = next(iter(res_right.keys()))
            for x in res_right.keys():
                if x > set_x * 2 / 3 and res_right[x] >= 4:
                    first_key = x
                    break
                else:
                    first_key = set_x
            # print(res_right)
        return first_key

    def is_page_foot(self,least_bbox, img_box, first_left, first_right):
        """
        左右边角，宽度差值小block[2]-block[0.]<=20，且更靠近盒子左右边界
        上下边角，高度差值小block[3]-block[1]<=20，且更靠近盒子上下边界
        """
        # 检测右测边角
        if least_bbox[0] >= first_right:
            return True
        # 检测下面边角
        elif img_box[3] - least_bbox[1] <= img_box[3] * 0.05:
            return True
        # 检测左侧边角
        elif least_bbox[2] <= first_left:
            return True
        # 上边角会遇到标题这个问题，要不要解决？
        elif least_bbox[3] - img_box[1] <= img_box[3] * 0.05:
            return True
        else:
            return False

    def is_fig(self,block_text):
        if re.search('^(\s?[如附]?[图表] ?[\dA-Za-z])', block_text):
            # print(block_text)
            return True
        return False

    def step1_drop_Pagefooter(self,item):
        # print(json.dumps(item, ensure_ascii=False))
        """
        1.遍历full_blocks判断是否为页边角
        2.在text中找到内容给删掉
        """
        raw_info = item['attr']['raw_info']
        img_box = item['attr']['img_box']

        if raw_info != []:
            set_x = img_box[2]
            x1_num = {}
            x2_num = {}
            for raw in raw_info:
                raw_context = raw['raw_context']
                for bb in raw_context:
                    bbox = bb["bbox"]
                    x1, y1, x2, y2 = bbox
                    x1_num[x1] = x1_num.setdefault(x1, 0) + 1
                    x2_num[x2] = x2_num.setdefault(x2, 0) + 1
            first_left = int(self.dict_merge(x1_num, set_x))
            first_right = int(self.dict_merge(x2_num, set_x, flag=False))
            # replace_num = 0
            for index, raw in enumerate(raw_info):
                full_blocks = raw['full_blocks']
                block_text = raw['block_text'].strip()
                if not block_text or len(block_text.strip()) <= 3:
                    continue
                if self.is_page_foot(full_blocks, img_box, first_left, first_right):

                    # replace_num += 1
                    # 对 least_text 进行正则转义
                    escaped_least_text = re.escape(block_text)

                    # 构建正则模式，匹配可能的前后空格、换行符和连字符
                    # pattern = re.compile(escaped_least_text + r'[\s\n-]{0,5}')

                    # 使用正则表达式替换匹配的文本
                    try:
                        item['text'] = re.sub(rf'{escaped_least_text}', rf'删除边角:<u>{block_text}</u>', item['text'])
                    except re.error as e:
                        print(f"Regex error: {e}")
                if self.is_fig(block_text):
                    escaped_least_text = re.escape(block_text)
                    # 构建正则模式，匹配可能的前后空格、换行符和连字符
                    # pattern = re.compile(escaped_least_text + r'[\s\n-]{0,5}')
                    # 使用正则表达式替换匹配的文本
                    try:
                        item['text'] = re.sub(rf'{escaped_least_text}', rf'删除图片描述:<u>{block_text}</u>', item['text'])
                        # item['text'] = re.sub(rf'{escaped_least_text}', rf'', item['text'])


                    except re.error as e:
                        print(f"Regex error: {e}")
            # if replace_num > 10:
            #     item['text'] = '(本页删除)本页中有超过10个边角的判断怀疑是目录页本页删除' + item['text']
            # print(item['text'])
        return item

    # def step1_correct_error_token(self, context):
    #     # 单词纠错
    #     rank_length = 480
    #     context_list = []
    #     for pos in range(0, len(context), rank_length):
    #         context_list.append(context[pos:pos + rank_length])
    #     if len(context_list) == 0:
    #         return ""
    #     sc_result = self.sc.process_text(context_list)
    #
    #     final_correct_list = []
    #     for item, sc_item in zip(context_list, sc_result):
    #         # 纠错内容后处理
    #         sc_details = self.fix_details(sc_item["details"])
    #         # 保证纠错的数量
    #         if len(sc_details) == 0 or len(sc_details) > 3:
    #             final_correct_list.append(item)
    #         else:
    #             final_content = ""
    #             pre_idx = 0
    #             for detail_item in sc_details:
    #                 [raw_token, new_token, detail_pos_start, detail_pos_end] = detail_item
    #                 final_content += "{}{}<u>纠错:{}</u>".format(item[pre_idx:detail_pos_start], new_token, raw_token)
    #                 pre_idx = detail_pos_end
    #             final_content += item[pre_idx:]
    #             final_correct_list.append(final_content)
    #     return "".join(final_correct_list)

    def step2_rm_kongge(self, context):
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
            return "本段删除1:<u>{}</u>".format(context)
            # return ""




    def get_person_idx(self, context):
        if re.findall(r'(#+|\d+ ?\.|[\(（] ?[0-9一二三四五六七八九十]+ ?[）\)])',context)!=[]:
            return [],[]
        doc = self.zh_nlp(context)
        person_block = []
        person_num = 0
        ent_dict = {
            "person": [],
            "org": [],
        }

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                key = "person"
            else:
                key = "org"
            if len(context[ent.start_char:ent.end_char])>1:
                ent_dict[key].append(context[ent.start_char:ent.end_char])
        return ent_dict["person"], ent_dict["org"]




    def step4_rm_cite(self,context_raw):
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
        # print(cite_tag)
        if sum(cite_tag) >= 3 and len(context) < 200:
            return "参考删除-0:<u>{}</u>".format(context_raw)
            # return ""
        if sum(cite_tag) >= 2 and len(context) < 100:
            return "参考删除-0:<u>{}</u>".format(context_raw)
            # return ""

        # 基于人名判定
        try:
            # print(context)
            name_list, ORG_list = self.get_person_idx(context)
            # print(name_list,ORG_list)
            name_num, name_lens = len(name_list), len(''.join(name_list) )

            if len(context) == 0:
                return ""
            if name_lens / len(context.replace(' ','')) >= 0.3:
                return "参考删除-1:<u>{}</u>".format(context_raw)

            if name_num > 2:  # 超过2个人名
                # print(123, context_raw)
                hypothesis_template = "The type of this text is {}"
                classes_verbalized = ["Text content", "reference","acknowledgments",'personage introduction']
                output = self.zeroshot_classifier(context_raw, classes_verbalized, hypothesis_template=hypothesis_template,
                                             multi_label=False)
                # print(output["labels"][0], output['scores'][0])
                # print(output)
                if output["labels"][0] != 'Text content' and output['scores'][0] > 0.7:
                    return "参考删除-2:<u>{}</u>".format(context_raw)
                else:
                    return context_raw
            # elif cite_index and person_num > 0 and len(context) < 150:
            #     return "参考删除-3:<u>{}</u>".format(context_raw)
            # return ""
            else:
                return context_raw
        except:
            return context_raw


    def is_complete(self, last_sentence, curr_sentence):

        last_sentence = last_sentence.lstrip(" ").rstrip(" ").strip("\n")
        curr_sentence = curr_sentence.lstrip(" ").lstrip("\n")
        conjunction=[r'\d{1,4}\.[^\d]',r'((?:\(|（) ?[0-9-一二三四五六七八九十]+ ?(?:）|\)))',r'([-一二三四五六七八九十]{1,2}[\.、])[^\d]',r'##','[A-E]\.','[【[〖] ?[\u4e00-\u9fa5]{2,4} ?(\d* )?[〗\]】]']
        No_closing_remarks=["、", "对", "与", "和", "及", "其", "但", "且", "乃", "~", "～","的", "由","于", "致","—","-",",","，"]
        formula_switch=True
        for word in conjunction:
            if re.findall(r'[\u4e00-\u9fa5]',last_sentence)==[]:
                if '+' in last_sentence or r'/' in last_sentence or '=' in last_sentence or "—" in last_sentence:
                    formula_switch=False
            if re.findall(word, last_sentence.replace(' ', '')[:6]) == []:
                last_sentence_switch=True
            else:
                last_sentence_switch=False
                break
        for word in conjunction:
            if re.findall(r'[\u4e00-\u9fa5]', curr_sentence) == []:
                if '+' in curr_sentence or r'/' in curr_sentence or '=' in curr_sentence or "—" in curr_sentence:
                    formula_switch = False
            if re.findall(word, curr_sentence.replace(' ', '')[:6]) == []:
                curr_sentence_switch=True
            else:
                curr_sentence_switch=False
                break

        # print(last_sentence)
        # print(last_sentence_switch)
        # print('--')
        # print(curr_sentence)
        # print(curr_sentence_switch)
        # print()
        if "|" in last_sentence and curr_sentence_switch or "|" in curr_sentence and last_sentence_switch:
            return True
        if len(last_sentence) == 0:
            return False
        if not formula_switch:
            return True
        if last_sentence.strip(" ")[-1] in ["。", "？", "！", ".", "?", "!", ")"]:
            return True
        elif last_sentence.strip(" ")[-1] in No_closing_remarks and last_sentence.strip(" ")[-2:] not in ['目的','总和'] and  curr_sentence_switch and len(last_sentence)>1 :
            return False
        # elif "#" in last_sentence or "#" in curr_sentence:
        elif len(re.findall(r'[^a-zA-Z] ?[Oo]\n',last_sentence))>0:
            return True
        elif len(re.findall(r'^#', last_sentence)) > 0 or len(re.findall(r'^#', curr_sentence)) > 0:
            return True
        elif len(re.findall(r'[-一二三四五六七八九十](\s\.|、)', last_sentence + curr_sentence)) > 0:
            return True
        elif len(re.findall(r'^[^#\d\(（](?:.*?)([a-zA-Z\d]$)(?<!g)', last_sentence)) > 0 and curr_sentence_switch  or len(re.findall(r'^[a-zA-Z\d][^\.][^\.]', curr_sentence)) > 0 and last_sentence_switch:
            # print(111)
            return False

        # try:
        #     if len(last_sentence) > 6:
        #         merge_sentence = last_sentence[-5:] + curr_sentence[0]
        #
        #     else:
        #         merge_sentence = last_sentence[-2:] + curr_sentence[0]
        # except:
        #     return True
        # # print(merge_sentence)
        # split_word = list(jieba.cut(merge_sentence, cut_all=False))
        # # print(split_word)
        # if len(split_word[-1]) > 1 and re.findall(r'([\u4e00-\u9fa5]{2})',split_word[-1])!=[]:
        #
        #     print(222)
        #
        #     return False
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
                # final_list[-1] = "{}删除换行1：{}".format(final_list[-1], context_list[idx])
                final_list[-1] = "{}{}".format(final_list[-1], context_list[idx])

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
                # final_list[-1] = "{}删除换行2：{}".format(final_list[-1], context_list[idx])
                final_list[-1] = "{}{}".format(final_list[-1], context_list[idx])

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
            return "整页删除\n\n{}".format(context)
            # return ""

    # def step7_rm_digital(self, context):
    #     res = re.findall(r"\d", context)
    #     no_digital = re.sub(r"\d", "", context)
    #     # print(res)
    #     # print(no_digital)
    #     # print(list(set(no_digital.split(" "))))
    #     context_lens = len(list(set(no_digital.split(" "))))
    #
    #     if len(res) > 8 and (context_lens) < 5:
    #         return "删除38:<u>{}</u>".format(context)
    #         # return ""
    #     return context
    def step7_judgment_connection(self,context):
        copy_target=[]

        while re.findall(r'(^[^#\d\n\(（第一二三四五六七八九十].*?[\u4e00-\u9fa5,，(（])( *\n{1,} *)([)）:：,，학\u4e00-\u9fa5])',context, flags=re.MULTILINE):
            target = re.findall(r'(^[^#\d\n\(（第一二三四五六七八九十].*?[\u4e00-\u9fa5,，(（])( *\n{1,} *)([)）:：,，학\u4e00-\u9fa5].*)',context, flags=re.MULTILINE)
            # print(copy_target,'---',target)
            if target!=copy_target:
                for single in target:
                    # if '删除换行' in single[0][0:5] or '删除换行' in single[2][0:5]:
                    #     continue
                    if len(single[0]) <= 9 and re.findall(r'[,，.。?？!！；;“"‘\']',single[0])==[]or len(single[2]) <= 9 and re.findall(r'[,，.。?？!！；;“"‘\']',single[2])==[]:

                        continue
                    totoly_word = single[0] + single[1] + single[2]
                    # ans = single[0] +'删除换行3：'+ single[2]
                    ans = single[0] + single[2]

                    context = context.replace(totoly_word, ans)
                copy_target=target
                    # print(context)
            else:
                return context
        return context


    def step9_remove_en_noise(self,text):
        common_elements = ["Na", "Mg", "Al", "Si", "Cl", "Ca", "CH", "Ag", "Hg", "Cu", "mol", "nm", "mm", "cm", "kg",
                           "Hz", "Hb", "xOy", "OH", "H 2 O","SO","RNA","DNA","Fe"]
        suspect_lis, origin_lis, same= [], [],set([])
        target = re.sub(r'\(.*?\)', '替', text)
        en_lis = re.findall(
            r'(([A-ZÀ-ÖØ-ßА-ЯŞĆĂÂĐÊÔƠƯÞÐÆØÅa-zà-öø-ÿа-яşćăâđêôơưþðæøåभयेर ]{1,}) ?[\d]* ?([*A-ZÀ-ÖØ-ßА-ЯŞĆĂÂĐÊÔƠƯÞÐÆØÅa-zà-öø-ÿа-яşćăâđêôơưþðæøåभयेर \d]+)[A-ZÀ-ÖØ-ßА-ЯŞĆĂÂĐÊÔƠƯÞÐÆØÅa-zà-öø-ÿа-яşćăâđêôơưþðæøåभयेर])',
            target)
        for i in en_lis:
            origin_lis.append(i[0])
        origin_lis=list(set(origin_lis))
        origin_lis.sort(key=lambda x: x.lstrip().rstrip())

        # print(origin_lis)
        for idx, str in enumerate(origin_lis):
            if idx + 1 == len(origin_lis):
                continue
            if len(str)>10:
                continue
            if str.replace(' ', '')[:2].lower() == origin_lis[idx + 1].replace(' ', '')[:2].lower():
                same.add(origin_lis[idx])
                same.add(origin_lis[idx + 1])
        for str in same:
            origin_lis.remove(str)
        # # print(origin_lis)
        # for key, group in itertools.groupby(origin_lis):
        #     if len(list(group)) == 1:
        #         suspect_lis.append(key)

        # print('原', origin_lis)
        for word in origin_lis:
            word_copy = word.lstrip().rstrip()
            if word_copy.isupper()  and len(word_copy)<5:
                continue
            elif any(substr in word_copy for substr in common_elements):
                continue

            # print(word)

            inputs = self.tokenizer(word, return_tensors="pt")
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            # print(probs[0])
            if probs[0][0] < 0.1 or probs[0][1] > 0.85 or probs[0][2] > 0.85 or probs[0][3] > 0.85:
                text = text.replace(word, ' 英文噪声删除：<u>' + word + '</u> ')
                # text = text.replace(word, '')

        return text

    def step10_Irrelevant_long_text(self,context):
        split_token = "\n\n"
        if split_token not in context:
            split_token = "\n"

        count= 0
        result,suspected = [],False
        key_words=['教材编写','前言','作者简介','作者介绍','版权所有','主编介绍','附录','参考文献']
        for word in key_words:
            if word in context:
                suspected=True
                break
        if suspected:
            # print(context)
            context_lis = context.split('\n')
            # print(context_lis)
            for paragraph in context_lis:
                if not paragraph:
                    result.append(paragraph)
                    continue
                # print(paragraph)
                hypothesis_template = "The type of this text is {}"
                classes_verbalized = ["Text content", "reference", "acknowledgments", 'personage introduction',
                                      'Guide book', ]
                output = self.zeroshot_classifier(paragraph, classes_verbalized, hypothesis_template=hypothesis_template,
                                             multi_label=False)
                # print(output["labels"][0], output['scores'][0])
                if output["labels"][0] != 'Text content':
                    paragraph = "参考删除-3:<u>{}</u>".format(paragraph)
                    count += 1
                result.append(paragraph)
            context_lis=set(context_lis)
            context_lis.discard('')

            if count >= len(context_lis) / 2:
                # return ''
                return '(本页删除)本页一半的段落中发现符合参考文献的特征' + '\n' + context
            else:
                return '\n'.join(result)
        else:
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
            if len(item)==0:
                continue
            if len(res) / len(item) > 0.5:
                # item = "删除0:<u>{}</u>".format(item)
                # result.append(item)
                continue
        item = sp.step4_rm_cite(item)

        # 1.正则
        # print(item)
        # print('----------------')
        for pattern_item in pattern_list:
            item = item.lstrip(" ").rstrip(" ")
            # print(pattern_item)
            item = re.sub(pattern_item[0], pattern_item[1], item)
        # print(item)

        # 2.替换 固定内容（非泛化）
        for replace_item in context_pattern:
            item = re.sub(replace_item[0], replace_item[1], item)

        # print(item)
        item = sp.step5_rm_english_noise(item)
        item = sp.step3_rm_noise_dig_alpha(item)
        # print('---')
        # print(item)

        item = sp.rm_lid_piece(item)


        item = sp.step2_rm_kongge(item)


        # print(item)
        # item = sp.step9_remove_en_noise(item)


        result.append(item)

    # 整合

    # print(context)
    context = split_token.join(result)
    while re.findall(r'(#?#? *第[—一二三四五六七八九十-]+[章节] *\.?)(\n+)#?#?( *[\u4e00-\u9fa5]{3,10})',context):
        # print(1)
        context=re.sub(r'(#?#? *第[—一二三四五六七八九十-]+[章节] *\.?)(\n+)#?#?( *[\u4e00-\u9fa5]{3,10})',r'\1\3',context)
    # print(context)
    context = sp.step9_remove_en_noise(context)
    context=sp.step7_judgment_connection(context)

    context = sp.rm_lid_context(context)
    context = sp.step10_Irrelevant_long_text(context)

    context = sp.step6_rm_short_context(context)
    # print(context)
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
        item=sp.step1_drop_Pagefooter(item)

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
sp=speicalProces()
fw = open(r'F:\zeroshots\reclean7_medicalpdfv2__preformat_zh.jsonl', 'w', encoding='utf-8')
with open(r'F:\zeroshots\medicalpdfv2_0724_preformat_zh.jsonl', "r", encoding="utf-8") as file:
    for item in tqdm(file.readlines()):

        item=process_line(item,sp)
        # with open(r'F:\zeroshots\reclean7_medicalpdfv2__preformat_zh.jsonl', 'a', encoding='utf-8') as f:
        fw.write(item+'\n')


