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
pattern_list_zh = [
    [r'([［【][\s\d,，\-‑]{1,25}[】］])',r''],      #［22，11-11］
    [r'([^，。（）：]{1,}(图\d+。图\d+|表\d+。表\d+)[^，。（）(\d\.)]{1,})',r''],     # 固定形式   （血脂异常治疗随访流程见图2。图2 血脂异常治疗随访流程）
    [r'([（\(][^）\)]{,10}(图\s?\d+|表\s?\d+|见\s?\d+|点击|参见|附录|详?见)[^（\(]{,50}([（\(]\d+[）\)][^（\(]){0,3}[）\)])',r''],  # （图</u>3）（点击文末“阅读原文”） （参见相关章节）   图、表前后有字符的冗余允许存在（\d+）
     # 利益冲突所有作者声明不存在利益冲突
    [r'((图\s?\d+|表\s?\d+|见\s?\d+)\s[A-Z\u4e00-\u9fa5/、]{,20})([^A-Z\u4e00-\u9fa5/、])',r'\3'],   # 固定形式  图|表|见\d+ 到非中文
    [r'(流程)(见?图\s?[\d+\.]{1,4})',r'\1'],    # 只选中流程后的见图   只删见图1
    [r'([，。：》；）])([^，。：；（\(]{,40}(见?图\s?\d+|见\s?\d)[^，。\s]{,40})([，。\s]|$)',r'\1\4'],    #见图表述到前后的标点。
    [r'(见?表\s?[\d+\.、，]{1,4})',r''],    # 表只删除见表
    [r'.*利益冲突所有作者声明不存在利益冲突.*',r''],
    [r'（来源于《神经病学与神经康复学杂志》 2012年第9卷第3期）',r''],
    [r'图1 与头晕/眩晕相关的传入、传出通路示意图',r''],
    [r'本指南适用于全科医生和县级及以下皮肤专科医生。关于文中未提及的其他适用于银屑病的治疗手段可参考《中国银屑病诊疗指南（2018完整版）》。',r'']
    # [],
]


class speicalProces:
    def __init__(self):
        pass
    def step3_reference(self, context):
        new_context = []
        references_started = False   #定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(r'^(志 谢|References|参考文献|见参考文献|致谢|REFERENCES|ACKNOWLEDGMENT|The following organizations also provide reliable health information|More on this topic|Topic[^\.]*Version|For country code abbreviations|ACKNOWLEGMENT|WHERE TO GET MORE INFORMATION)', item.strip()):
                references_started = True
            if references_started:
                item = ""
            new_context.append(item)
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



    pattern_list= pattern_list_zh


    # 分解处理
    result = []
    sp = speicalProces()

    # special_process：
    # context = sp.step1_drop_sentenc(context)
    context = context.split(split_token)
    # 7/24uptodata_new修改
    context = sp.step3_reference(context)

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
    context = re.sub(r'[。，：\.、](\s?[、。，\.：；]){1,5}',r'。',context)
    context = re.sub(r'[,\.](\s+[,\.]){1,5}',r'.',context)
    return context



fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean3_high_quality-diagnosis-and-treatment_zh.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\high_quality-diagnosis-and-treatment_zh_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "99e3854f-8575-4e3b-a320-feaf1f29f45e":
        context = item["text"]
        lang = item["lang"]
        if lang == "zh":
            context = clean_text(context, lang)
            context = post_process(context)
            # print(context)
            item["text"] = context
            item = json.dumps(item, ensure_ascii=False)
            print(item)
            fw.write(item + "\n")
