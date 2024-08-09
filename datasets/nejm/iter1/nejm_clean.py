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
    # [r'(^([Ff]igs?(ure)?s?|F\s?IGS?(URE)?s?|Ref|DOI|Table)\s\d+[^\n]*)',r'删除1:<u>\1</u>'],    # 固定形式  Figure|Table|DOI|REF 开头  删除整行
    [r'(\(pages?\s[^\(\)]*\))',r'删除1:<u>\1</u>'],   # 固定格式 （page ...）
    [r'(\(\s?([Ff]igs?(ure)?s?|F\s?IGS?(URE)?s?|Table|Details|Appendix)\s[^\(\)]*\))',r'删除2:<u>\1</u>'],   # 固定格式  带有（）的图片表格描述 附录描述 协议描述
    [r'(<sup>(<a>)?[\d\s\-—,]{1,10}(</a>)?</sup>)',r'删除3:<u>\1</u>'],   # 特殊格式的数字引用删除
    [r'(\([^\(\)]{,40}[\s,]\d{4}[^\(\)]{,40}\))',r'删除4:<u>\1</u>'],     # 带有括号的引用 例(N Engl J Med 300:9–13, 1979)
    [r'§',r'']    # 一个特殊符号

]


class speicalProces:
    def __init__(self):
        pass

    def step1_reference(self, context):
        new_context = []
        first_paragraph = context[0]
        references_started1 = False  # 初始化 references_started 变量
        references_started2 = False
        CitingArticles_started1 = False  # 初始化 CitingArticles_started 变量
        CitingArticles_started2 = False
        if re.search(r'\*[^\n]*References?', first_paragraph):
            references_started1 = True  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
            context[0] = "参考删除-0" + context[0]
        elif re.search(r'\*[^\n]*Citing Articles', first_paragraph):
            CitingArticles_started1 = True  # CitingArticles_started开关   定义CitingArticles_started是因为他和有References出现的页开始删除的地方有所不同
            context[0] = "参考删除-0" + context[0]
        for index, item in enumerate(context):
            if re.search(r'^(References?|Funding and Disclosures)\s', item.strip()):
                references_started2 = True
            if references_started1 and references_started2:
                item = "参考删除-1:<u>{}</u>".format(item)
            if re.search(r'\.D\.', item.strip()):
                CitingArticles_started2 = True
            if CitingArticles_started1 and CitingArticles_started2:
                item = "参考删除-2:<u>{}</u>".format(item)
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
    # 分解处理
    result = []
    sp = speicalProces()

    # special_process：
    # context = sp.step1_drop_sentenc(context)
    context = context.split(split_token)
    # context = sp.step1_cankaoyinyongpage(context)
    # 7/24uptodata_new修改
    context = sp.step1_reference(context)

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



fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_nejm_preformat.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\nejm_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "75d087df-893d-406b-a0c4-6e87a0c312a2":
        context = item["text"]
        lang = item["lang"]
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        print(item)
        fw.write(item + "\n")
