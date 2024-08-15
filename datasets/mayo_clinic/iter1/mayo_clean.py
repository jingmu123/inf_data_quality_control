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
    [r'(^By Mayo.*)',r'删除1:<u>\1</u>'],

]


class speicalProces:
    def __init__(self):
        pass
    def step1_wuguantext_following(self, context):
        new_context = []
        references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(
                    r'^(To read this article in full you will need to make a payment|Call your doctor)',
                    item.strip()) :   # 付费下载...  拨打电话...  后面直接都删掉
                references_started = True
            if references_started:
                item = "无关删除-1" + item
            new_context.append(item)

        return new_context
    def step2_wuguanpage(self, context):
        new_context = []
        line_num = 0    # 定义一个变量记录行数
        wuguanline_num = 0   # 定义一个变量记录无关行数
        select = False   # 定义一个开关寻找本页是否有选择题的存在
        for item in context:
            if item.strip():
                line_num += 1
            if len(re.findall("[\da-z]\.\n", item.strip())) >= 4:   # 判断业内是否有选择题的存在   如果有打开开关
                select = True
            if re.search('[\.\s][A-Z]\.\n',item) or re.search('\d+-\d+$',item.strip()) or re.search(r'\*\s+(Google|View Large Image|Download)',item):   # 匹配到无关行的特征打标签
                wuguanline_num += 1
                item = "无关删除-2" + item

            new_context.append(item)
        print(len(new_context))
        print(line_num)
        print(wuguanline_num)
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
    context = re.sub(r'[,\.](\s+[,\.]){1,5}',r'\.',context)
    return context



fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_mayo_clinic_preformat.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\mayo_clinic_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "f67efdd0-090e-4b82-bd61-8e6cd39725b9":
        context = item["text"]
        lang = item["lang"]
        if re.search(r'^(_?To the Editor)',context):   # 过滤掉To the Editor当页内容里面都是一些编辑信息
            continue
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        print(item)
        fw.write(item + "\n")
