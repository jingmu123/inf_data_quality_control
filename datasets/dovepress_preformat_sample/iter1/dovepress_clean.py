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

pattern_list = [
    [r'([^\d]\s?[\.,]\s?)(\d+[\s–,\d+]{0,20})([A-Z]|$)',r'\1删除1:<u>\2</u>\3'],   # 无关数字
    [r'(\(\s?[^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more)s?[\s\.][^\(\)]*\))', r'删除2:<u>\1</u>'],# 固定格式  带有（）的图片表格描述 附录描述 协议描述
    [r'(Disclaimer.*)',r'删除3:<u>\1</u>'],
    [r'(\d+\s([–,]\s\d+\s){1,20})',r'删除4:<u>\1</u>'],  # 删除内容中出现的无关数字 可能会造成误删
]


class speicalProces:
    def __init__(self):
        pass
    def step1_wuguantext_following(self, context):
        new_context = []
        references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(
                    r'^(Ethics?\s|Disclosure|Acknowledgment|Disclaimer|Institutional Disclaimer)s?',
                    item.strip()) :   # 付费下载...  拨打电话...  后面直接都删掉
                references_started = True
            if references_started:
                item = "无关删除-1:<u>{}</u>".format(item)
                # item = ''
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

        before_introduction = 0
        before_introduction_index = []

        for index,item in enumerate(context):


            if re.search('^\*\s+',item) and index <= 3:
                before_introduction_index.append(index)
                before_introduction += 1

            if re.search('^[\*#]{0,5}Introduction',item):
                before_introduction_index.append(index)
                before_introduction -= 1

            new_context.append(item)

        if before_introduction <= 0 and len(before_introduction_index) >= 2:
            start_index = before_introduction_index[0]
            end_index = before_introduction_index[-1]
            print(start_index, end_index)
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index-1):
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                new_context[i] = "间距删除-1:<u>{}</u>".format(new_context[i])
                # new_context[i] = ""

            new_context[end_index-1] = re.sub(r'(^[^\*]*)(\n\*\*)', r'间距删除-2:<u>\1</u>\2',new_context[end_index-1])

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
    if len(context) <= 20:
        context.insert(0,"内容太短有用信息较少直接删除")
        context = split_token.join(context)
        return context

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

fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_dovepress_preformat_sample.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\dovepress_preformat_sample.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "380160f1-e0fe-440a-a5b6-14cceb8d0516":
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
