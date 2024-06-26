import json
import re
from tqdm import tqdm
import math
import spacy
import random

pattern_list_en = [

    [r'\s?(\d+,)+\d+$', r'删除2:<u>\1</u>'],
    [r'(?<=\.) \d+\.?\–?\,?(\d{0,3}\b|(?= ))',r'删除1:<u>\1</u>'],
    [r'(?<=\.\n)([A-Z])\n', r'删除3:<u>\1</u>'],

    [r'[^\。\.\"\?\n\d](\n) ?[A-Za-z\(]', r'删除4:<u>\1</u>']



 ]

context_pattern = [
    [r'(¬\s*)', r'删除16:<u>\1</u>'],
    [r'(\(\s*\))', r'删除17:<u>\1</u>']
]

# nlp = spacy.load("en_core_web_trf")
# nlp = spacy.load("en_core_web_sm")

class speicalProces:
    def __init__(self):
        pass

    def is_not_upper(self, char):
        return not char.isupper()
    def step1_drop_Pagefooter(self, item):
        down_max = 0
        text_boundary = []

        for dic in item["attr"]["raw_info"]:
            text_boundary.append(len(dic["raw_context"]))
        k = sorted(text_boundary)[int(len(text_boundary) // 2) - 1]

        for dic in item["attr"]["raw_info"]:
            if len(dic["raw_context"]) >= k and dic["full_blocks"][3] > down_max:
                down_max = dic["full_blocks"][3]
                # print(down_max)

        for dic in item["attr"]["raw_info"]:
            # len
            if dic["full_blocks"][1] > down_max:
                for dic_text in dic["raw_context"]:
                    item["text"] = item["text"].replace(dic_text["text"], "")
                    item["text"] = item["text"].replace(dic_text["text"].strip("-"), "")

        return item

    def step2_more_linefeed(self, context):
        index = 0
        while index < len(context):

            item = context[index]

            # 定义一个介词列表
            preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is']

            # 将 item 按 "\n" 分割
            item_sections = re.split(r'\n', item)
            section_index = 0

            while section_index < len(item_sections) - 1:  # 确保不会越界
                if re.search(r'\s\d+\.$', item_sections[section_index]):  # 匹配段落结尾是数字和句点
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]

                elif re.search(r'^(\d+\.){1,3}$', item_sections[section_index]) and item_sections[section_index + 1].lstrip()[0].isupper():  # 匹配段落中只有序号且下一段是大写开头的情况
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]

                elif any(item_sections[section_index].rstrip().endswith(" " + prep) for prep in preposition_list):   # 匹配同一段中介词结尾的
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]

                else:
                    section_index += 1  # 只有在不合并时才自增

            # 更新 item 以反映合并的段落
            item = '\n'.join(item_sections)
            context[index] = item

            # 合并以小写字母或特定标点符号开头的段落
            if index > 0:
                stripped_item = item.strip()
                if stripped_item and (stripped_item[0].islower() or stripped_item[0] in ["(", "[", ")", "]", "."]):
                    # 合并到前一个 item
                    context[index - 1] = context[index - 1].rstrip() + " " + item.lstrip()
                    # 删除当前 item
                    del context[index]
                    # 继续检查当前索引位置的元素
                    continue
                # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
                elif any(stripped_item.rstrip().endswith(" " + prep) for prep in preposition_list):
                    if index + 1 < len(context):
                        # 合并到下一个 item
                        context[index] = item.rstrip() + " " + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        continue

            index += 1
        return context

    def step3_lack_linefeed(self,context):
        new_context = []
        for item in context:
            # 查找 #•，并在其前后加换行符
            # parts = re.split(r'(?<=\s)([#•]{1,3}\s?[A-Z][^#•]*)', item)
            splitchar = r'([#•]{1,3}\s)'
            parts = re.split(splitchar, item)
            new_parts = []
            for part in parts:
                if part.strip() in ["#","•"]:
                    new_parts.append(part.strip())
                else:
                    new_parts.append(part.strip()+'\n')

            item = "".join(new_parts)
            # print(item)
            new_context.append(item)
        return new_context

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
        # patterns = [
        #     r'\.\s?\b\d{4}\b',  # 年份，比如 . 2010
        #     r'\b\d{4}\b\s?;',  # 年份，比如 2010;
        #     r'(?:Journal|Proceedings|Conference|Studies|Review|BMJ|JAMA|Pediatrics|Crit Care Med|Nurs Crit Care|Acad Emerg Med|Health Serv Res)',
        #     # 期刊或会议名的关键词
        #     r'(?:doi:\s*\S+)',  # DOI
        #     r'(?:vol\.?\s*\d+)',  # 卷号
        #     r'(?:no\.?\s*\d+)',  # 期号
        #     r'(?:pp\.?\s*\d+\s*-\s*\d+)',  # 页码范围
        #     r'\d+\s?:\d+\s?[–-]\s?\d+',  # 页码范围格式
        #     r'\set al\.'  # et al
        # ]
        cite_tag = []
        cite_index = 1 if len(re.findall(r'\[\d+\]', item)) > 0 else 0
        cite_year = 1 if len(re.findall(r'\[\d\d\d\d\]', item) or re.findall(r'\.\s?\b\d{4}\b',item) or re.findall(r'\b\d{4}\b\s?;',item)) else 0      # 年份，比如 . 2010 、 2010;
        cite_page = 1 if len(re.findall(r'\.\s?\b\d{4}\b',item) or re.findall(r'\d+\s?:\d+\s?[–-]\s?\d+',item)) else 0
        cite_J = 1 if len(re.findall(r'\[[Jj]\]', item)) else 0
        cite_doi = 1 if " doi " in item else 0
        cite_etal = 1 if " et al" in item else 0
        cite_vol = 1 if " vol. " in item else 0
        # cite_page = 1 if len(re.search(r'\.\s?\b\d{4}\b',item)) else 0
        cite_tag = [cite_index, cite_year, cite_J, cite_doi, cite_etal, cite_page, cite_vol]
        if sum(cite_tag) > 1:
            return "参考删除-0:<u>{}</u>".format(item)

        person_block, person_num = self.get_person_idx(item)
        # 超过5个人名
        person_block_lens = [block_item[1] - block_item[0] for block_item in person_block]
        person_lens = sum(person_block_lens)
        if person_lens / len(item) > 0.3:
            return "参考删除-1:<u>{}</u>".format(item)
        if person_num > 5:
            return "参考删除-2:<u>{}</u>".format(item)
        elif cite_index and person_num > 0:
            return "参考删除-3:<u>{}</u>".format(item)
        else:
            return item
    def step4_removepage(self, context):
        # context 是一个列表，每个 item 是一段内容
        context_lens = len(context)
        # 用于统计有多少个段落中出现了人名
        num = 0
        new_context = []
        for item in context:
            # 返回的item是已经被重写过的item
            item = self.step4_rm_cite(item)
            # 新的item重新加入一个新的列表
            new_context.append(item)
            # 判断item是否被判定未参考文献
            if re.search(r'参考删除',item):
                # 如果当前段落中有人名且符合参考文献的特征
                num += 1
        # 对整页的一个判断
        if num >= context_lens * 0.5:
            new_context.insert(0, "(本页删除)本页在超过一半的段落中发现人名且符合参考文献的特征")
        return new_context


    def step5_is_shortpage(self,context):
        duanluo_num = len(context)
        short_duanluo_num = 0
        if duanluo_num <= 3:
            for item in context:
                if len(item.strip()) < 100:
                    short_duanluo_num += 1
            if short_duanluo_num > 1:
                context.insert(0, "(本页删除)本页的段落数量小于等于3且至少段落长度有2条以上在100以下")
        elif duanluo_num <= 5:
            for item in context:
                if len(item.strip()) < 80:
                    short_duanluo_num += 1
            if short_duanluo_num > 3:
                context.insert(0, "(本页删除)本页的段落数量小于等于5且至少段落长度有4条以上80以下")
        else:
            # 段落短
            for item in context:
                if len(item.strip()) < 50:
                    short_duanluo_num+=1
            if short_duanluo_num > duanluo_num * 0.5:
                context.insert(0, "(本页删除)本页有超过一半的段落长度小于50字符")   # 如果有很多标题怎么办，一个标题一段文字
        return context


def clean_text(context, lang):
    split_token = "\n\n"

    if lang == 'en':
        pattern_list = pattern_list_en

    result = []

    sp = speicalProces()
    """
    目前的顺序
    1.删除页脚
    2.解决换行的问题包括多于换行、缺少换行
    3.判定参考文献
    4.正则替换
    5.判断整页长短问题
    """
    context = sp.step1_drop_Pagefooter(context)
    context = post_process(context["text"])
    # context是一个以两个换行符为切割条件的列表
    context = context.split(split_token)
    # 多余换行
    context = sp.step2_more_linefeed(context)
    # 缺少换行
    context = sp.step3_lack_linefeed(context)
    # 判定参考文献
    # context = sp.step4_removepage(context)
    for item in context:
        item = item.strip(split_token).strip()

        if "## References" in item:
            continue
        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)
            item = item.strip()
        for pattern_item in context_pattern:
            item = re.sub(pattern_item[0], pattern_item[1], item)
        result.append(item)
    # 使用NLP模型判断参考文献


    # 判断整页短路长短
    context = sp.step5_is_shortpage(result)
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
    return context



fw = open("C:\inf_data_quality_control-main\datasets\medical_stage4_surya\iter5\sample\medical_stage4_surya_clean.jsonl", "w",encoding="utf-8")
with open("C:\inf_data_quality_control-main\datasets\medical_stage4_surya\iter5\sample\medical_stage4_surya_preformat.jsonl", "r",encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        # if item["seq_id"] == "7152ecc4-3754-46ed-a13d-7bc34c34b326":
        #     print(item)
        context = item
        # lang = item["lang"]

        context = clean_text(context, "en")
        context = post_process(context)
        if len(context) < 100:
            continue
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")




# 文件路径
# input_file_path = "C:\\pycharm\\orc识别pdf清洗数据\\pdf\\clean_json\\guidelines_liangyong_surya_preformat.jsonl"
# output_file_path = "C:\\pycharm\\orc识别pdf清洗数据\\pdf\\clean_json\\guidelines_liangyong_surya_preformat_en_1.jsonl"
#
# # 读取所有记录
# with open(input_file_path, "r", encoding="utf-8") as fs:
#     lines = fs.readlines()
# # # 随机抽取5000条记录
# # sampled_lines = random.sample(lines, 5000)
# # 处理并保存抽取的记录
# # with open(output_file_path, "w", encoding="utf-8") as fw:
#     for items in tqdm(lines):
#         item = json.loads(items.strip())
#         if item["seq_id"] == "f89beed0-6a1f-4084-94e3-04c998a788ff":
#             context = item
#
#             # 清洗和处理文本
#             context = clean_text(context, "en")
#             context = post_process(context)
#
#             if len(context) < 100:
#                 continue
#
#             item["text"] = context
#             item = json.dumps(item, ensure_ascii=False)
#             print(item)
#         # fw.write(item + "\n")



