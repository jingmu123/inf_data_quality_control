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
    [r'(.*Related Topics[^$]*)',r'删除1:<u>\1</u>'],     # 相关话题...
    [r'(^For more information.*)',r'删除2:<u>\1</u>']   # 欲了解更多

]



class speicalProces:
    def __init__(self):
        pass
    def step1_wuguantext_following(self, context):
        new_context = []
        references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(
                    r'^(Article Resources)s?',
                    item.strip()) :   # 付费下载...  拨打电话...  后面直接都删掉
                references_started = True
            if references_started:
                item = "无关删除-1:<u>{}</u>".format(item)
                # item = ''
            new_context.append(item)

        return new_context
    def step2_wuguanpage(self, context):
        new_context = []
        Related_Topics = False
        for item in context:
            if re.search('^Related Topics',item):
                Related_Topics = True
                item = "无关删除-2:<u>{}</u>".format(item)
                new_context.append(item)
                continue
            if re.search(r'\n\s{4}Related Topics',item):
                # print(item)
                # exit(0)
                Topic_in_item = False
                new_item = []
                splited_item = item.split('\n')
                for i in splited_item:
                    if re.search(r'^\s{4}Related Topics',i):
                        Topic_in_item = True
                        i = "无关删除-4:<u>{}</u>".format(i)
                        new_item.append(i)
                        continue
                    if Topic_in_item and (re.search(r'^\s{4}[^\s]',i) or re.search(r'^\s{1,5}$',i)):
                        i = "无关删除-4:<u>{}</u>".format(i)
                    else:
                        Topic_in_item = False
                    new_item.append(i)
                item = '\n'.join(new_item)
            if Related_Topics and (re.search(r'^[\*\s]{2,10}$',item) or re.search(r'\?$',item.strip())):
                item = "无关删除-3:<u>{}</u>".format(item)
            else:
                Related_Topics = False

            new_context.append(item)
        return new_context
    def step3_more_linefeed(self,context):
        index = 0
        while index < len(context):
            item = context[index]

            # 合并以小写字母或特定标点符号开头的段落
            stripped_item = item.strip()
            # print(stripped_item)
            if index >= 0:
                if index + 1 < len(context) and re.search(r'^#+\s?(\*+)?\d+\.(\*+)?$',stripped_item):
                    context[index] = stripped_item +"删除换行"+re.sub("#+\s",r'',context[index+1])
                    # 删除下一个 item
                    del context[index + 1]
                    index = index - 1
                    continue
            index += 1
        return context

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
    print(context)
    context = sp.step1_wuguantext_following(context)
    context = sp.step2_wuguanpage(context)
    context = sp.step3_more_linefeed(context)
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



fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_icliniq_article_preformat.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\icliniq_article_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "18678899-4ff8-443d-9b0a-a83e7e11dcc1":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
