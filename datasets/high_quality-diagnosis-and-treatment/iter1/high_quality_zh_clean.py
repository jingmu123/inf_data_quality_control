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
                    [r'(［[\s\d,，\-‑]{1,20}］)',r''],      #［22，11-11］
                    [r'([^，。]{1,}(图\d+。图\d+|图\d+。图\d+)[^，。（）]{1,})',r'删除2:<u>\1</u>'],     # 固定形式   （血脂异常治疗随访流程见图2。图2 血脂异常治疗随访流程）
                    [r'([（\(][^）\)]{,10}(图\s?\d+|表\s?\d+|见\s?\d+|点击|参见|附录|详?见)[^（\(]{,50}([（\(]\d+[）\)][^（\(]){0,3}[）\)])',r''],  # （图</u>3）（点击文末“阅读原文”） （参见相关章节）   图、表前后有字符的冗余允许存在（\d+）
                     # 利益冲突所有作者声明不存在利益冲突
                    [r'([，。：])([^，。：（\(]{,20}(图\s?\d+|表\s?\d+|见\s?\d+)[^，。]{,30})([，。]|$)',r'\1删除4:<u>\2</u>\4'],    #。见表4、5 。
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
    context = re.sub(r'[。，\.](\s?[。，\.：；]){1,5}',r'。',context)
    context = re.sub(r'[,\.](\s+[,\.]){1,5}',r'.',context)
    return context



fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_high_quality-diagnosis-and-treatment_zh.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\high_quality-diagnosis-and-treatment_zh_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "e1b4d84a-06fb-4bf8-b56f-442e607230e4":
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
