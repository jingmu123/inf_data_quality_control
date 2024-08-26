import json
import os
import re
import random

import jieba
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm




import json
import os
import re
import random

import jieba
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"
# pattern_list = [
#     [r'(^By Mayo.*)',r'删除1:<u>\1</u>'],
#
#     [r'(\([^\(\)]*(https?:|www\.|WWW\.)[^\)\(]*\))',r''],  # 无关链接网址带括号
#     [r'(.*(https?:|www\.|WWW\.).*)',r'删除2:<u>\1</u>'],   # 无关链接网址的整句删除
#     [r'(\\\[[^\[\]]*\d{4};[^\[\]]*\\\])', r'删除5:<u>\1</u>'],  # 带有方括号的引用
#     [r'(.*\s((1|2)\d{3};|Vol \d\.?)(\s.*|$))',r'删除3:<u>\1</u>'],  # 带有年份特征的句子  ( 2000; )
#     [r'(\(\s?[^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more)s?[\s\.][^\(\)]*\))',r'删除4:<u>\1</u>'],  # 固定格式  带有（）的图片表格描述 附录描述 协议描述
#     # [r'(^.{1,100}\set[\s\xa0]{1,3}al.{1,100}$)',r'删除6:<u>\1</u>'], # et al
#     [r'([\(\[][^\(\)\[\]]*\set[\s\xa0]{1,3}al[^\(\)\[\]]*[\)\]])',r'删除6:<u>\1</u>'],
#     [r'.*,\s?et[\s\xa0]{1,3}al.*',r'删除6:<u>\1</u>'],
#     [r'(^(FDA |Date accessed:).*)',r'删除7:<u>\1</u>'], # 固定格式描述开头FDA或Date accessed:
#     [r'(^\s?[;,])',r'删除8:<u>\1</u>'], # 多余标点开头是;
#
#     [r'(Drug information provided by: Merative, Micromedex.*)',r'删除9:<u>\1</u>'],   # 描述出版信息，删除8和删除9一起用
#     [r'(#{1,3} US Brand Name)',r'删除10:<u>\1</u>'],
#     [r'(^US Food & Drug Administration.*\n.*)',r'删除11:<u>\1</u>'],
#     [r'(Date:.*)',r'删除12:<u>\1</u>'],
#     [r'(^Warning letter to.*)',r'删除13:<u>\1</u>'],
#     [r'(^Public Health Service.*)',r'删除14:<u>\1</u>'],
#     [r'(^Cerebyx.*)',r'删除15:<u>\1</u>'],
#     [r'(.*(doi|DOI)\s?:)',r'删除16:<u>\1</u>'],
# ]
pattern_list = [
    [r'(^By Mayo.*)',r''],

    [r'(\([^\(\)]*(https?:|www\.|WWW\.)[^\)\(]*\))',r''],  # 无关链接网址带括号
    [r'(.*(https?:|www\.|WWW\.).*)',r''],   # 无关链接网址的整句删除
    [r'(\\\[[^\[\]]*\d{4};[^\[\]]*\\\])', r''],  # 带有方括号的引用
    [r'(.*\s((1|2)\d{3};|Vol \d\.?)(\s.*|$))',r''],  # 带有年份特征的句子  ( 2000; )
    [r'(\(\s?[^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more)s?[\s\.][^\(\)]*\))',r''],  # 固定格式  带有（）的图片表格描述 附录描述 协议描述
    # [r'(^.{1,100}\set[\s\xa0]{1,3}al.{1,100}$)',r'删除6:<u>\1</u>'], # et al
    [r'([\(\[][^\(\)\[\]]*\set[\s\xa0]{1,3}al[^\(\)\[\]]*[\)\]])',r''],
    [r'.*,\s?et[\s\xa0]{1,3}al.*',r''],
    [r'(^(FDA |Date accessed:).*)',r''], # 固定格式描述开头FDA或Date accessed:
    [r'(^\s?[;,])',r''], # 多余标点开头是;

    [r'(Drug information provided by: Merative, Micromedex.*)',r''],   # 描述出版信息，删除8和删除9一起用
    [r'(#{1,3} US Brand Name)',r''],
    [r'(^US Food & Drug Administration.*\n.*)',r''],
    [r'(Date:.*)',r''],
    [r'(^Warning letter to.*)',r''],
    [r'(^Public Health Service.*)',r''],
    [r'(^Cerebyx.*)',r''],
    [r'(.*(doi|DOI)\s?:)',r''],            # 存在有DOI描述的句子
    [r'(\([^\(\)]*Mayo Clin(ic)? Proc[^\(\)]*(\([^\)]*\)[^\(]){0,3}\))',r''],    # 带有括号( _Mayo Clin Proc_ . 2005;80:657-666)
    [r'.*Mayo Clin(ic)? Proc.*',r''],      # Mayo Clin Proc 梅奥医院...

    [r'([^\dm]+\s?|^)(<sup>(<a>)?[\d\s\-—,]{1,20}(</a>)?</sup>)',r'\1删除19:<u>\2</u>'],
    [r'(\\\[[^\[\]]*\d{4}[^\[\]]*\\\])',r'删除20:<u>\1</u>'],   #结尾是一个年份的句子
    [r'(^\*   US Pharmacopeia.*)',r''],     # 固定的句子
    [r'(.*[\s\.]\d{4}\.?$)',r'删除21:<u>\1</u>'],  # 删除末尾为年份的句子
    [r'(\*   Kaiser Family Foundation Health Research and Educational Trust)',r''],   # 固定的句子
    [r'(^\*{0,4}_?To the Edito.*)',r'删除22:<u>\1</u>'],   # 开头是To the Editor是一个致编辑的文本  这里的内容基本没用
    [r'\(data from Siscovick et al',r''],  # 固定的句子
    [r'The study by Khan et al',r''], # 固定的句子

]


class speicalProces:
    def __init__(self):
        pass
    def step1_wuguantext_following(self, context):
        new_context = []
        references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(
                    r'^(To read this article in full you will need to make a payment|Call your doctor for|Other side effects not listed may also occur in some|Supplemental Online Material|### Footnotes|Article info|Acknowledgments?|[#\*]{0,4}\s?Trial Registration|[#\*]{0,4}\s?Files in this Data Supplement)',
                    item.strip()) :   # 付费下载...  拨打电话...  后面直接都删掉
                references_started = True
            if references_started:
                # item = "无关删除-1:<u>{}</u>".format(item)
                item = ''
            new_context.append(item)

        return new_context
    def step2_wuguanpage(self, context):
        print(context)
        new_context = []
        num = False
        for index,item in enumerate(context):
            if re.search(r'^<sup><a>\d+</a></sup>',item):
                num = True
                num2Google = 0
                num2Google += 1
                num2Google_index = index
                num2Google_index_line = []
                num2Google_index_line.append(index)
            if num and re.search(r'\*\s+(Google|View Large Image|Download|et al\.|Open table in a new tab)',item):
                num2Google -= 1
                if index - num2Google_index <= 5 and num2Google == 0:
                    new_context.append(item)
                    num2Google_index_line.append(index)
                    start_index = num2Google_index_line[0]
                    end_index = num2Google_index_line[-1]
                    # 循环遍历需要替换的片段
                    for i in range(start_index, end_index+1):
                        # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                        # new_context[i] = "无关删除-3:<u>{}</u>".format(new_context[i])
                        new_context[i] = ""

                    continue
            if re.search('^\*[^\n]*[\.\s][A-Z]\.(\n|$)',item) or re.search('[a-zA-Z]?\d+-[a-zA-Z]?\d+\.?$',item.strip()) or re.search(r'\*\s+(Google|View Large Image|Download|et al\.|Open table in a new tab)',item) or re.search(r'^\*\s+[^\n]*[A-Z](\n|$)',item):   # 匹配到无关行的特征打标签
                # wuguanline_num += 1
                # item = "无关删除-2:<u>{}</u>".format(item)
                item = ''
            new_context.append(item)
        # print(new_context)
        return new_context

    def step3_Spaced_delete(self, context):
        new_context = []
        question = 0
        question_index = []


        for index,item in enumerate(context):
            if re.search('\.\s?In their editorial and administrative roles',item):
                question_index.append(index)
                question += 1
            if re.search(r'^In their editorial and administrative roles',item):
                question_index.append(index)
                question += 1
            if re.search(r'^\*\*Question',item):
                question_index.append(index)
                question -= 1

            new_context.append(item)
        # print(question_index)
        if question <= 0 and len(question_index) >= 2:
            start_index = question_index[0]
            end_index = question_index[-1]
            print(start_index, end_index)
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index + 1):
                if re.search('\.\s?In their editorial and administrative roles',new_context[start_index]):
                    new_context[start_index] = re.sub('(\.\s?)(In their editorial and administrative roles.*)',r'\1间距删除-1:<u>\2</u>',new_context[start_index])
                    continue
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                # new_context[i] = "间距删除-1:<u>{}</u>".format(new_context[i])
                new_context[i] = ""
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
    # context = sp.step1_reference(context)
    context = sp.step1_wuguantext_following(context)
    context = sp.step2_wuguanpage(context)
    context = sp.step3_Spaced_delete(context)
    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)
        if lang == "zh":
            item = sp.step4_rm_kongge(item)
        result.append(item)
    for item in result:
        print(item)

    # deleted_context = []
    # for item in result:
    #     if re.search(r"(参考|无关)", item):
    #         continue
    #     deleted_context.append(item)
    # 整合
    # deleted_context = []
    # for item in context:
    #     if re.search(r"(目录|参考)", item):
    #         continue
    #     deleted_context.append(item)
    context = split_token.join(result)

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


# fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean3_mayo_clinic_preformat.jsonl", "w", encoding="utf-8")
# with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\mayo_clinic_preformat.jsonl", "r", encoding="utf-8") as fs:
fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean2_mayo_clinic_proceeding_preformat.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\mayo_clinic_proceeding_preformat.jsonl", "r", encoding="utf-8") as fs:

    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "2e845522-c621-4025-bc43-3a1115f94bba":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        if re.search(r'(Highlights from the Current Issue|CORRECTIONS?|The History of Otorhinolaryngology at Mayo Clinic|Minimally Disruptive Medicine|Welcomes New Staff Members)',title):
            continue
        if re.search(r'^(_?To the Edito\s?r|CORRECTION)',context):   # 过滤掉To the Editor当页内容里面都是一些编辑信息
            continue
        context = re.sub(r'\xa0',r' ',context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
