import json
import os
import re
import random
import threading

import wordninja
import jieba
from tqdm import tqdm

pattern_list = [
    [r'。', r'\.'], [r'，', r','], [r'；', r';'],
    [r'\|', ''],

    [r'(<[\/\w]+>)+', ''],
    [r'([^,\.;\n] +)([\(（][\d\-,～~，;；–—、\s_]+[\)）])', r'\1删除1:<u>\2</u>'],
    [r'(\n[  \t]*(Author Information)[\w\W]*)', r'删除3:<u>\1</u>'],
    [r'([\(（][^\(\)（）\n]*(Figure|Table|Appendix|[Nn]o\.|\d{4})[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>'],
    [r'(\n[  \t]*\**(Figure|Table|Appendix)[^\n]*)', r'删除5:<u>\1</u>'],
    [r'([^\.\n]*(((Figure|Table|Appendix)[\d\-～~–—\. _]+shows?)|( in (Figure|Table|Appendix) \d))[^\.\n]*\.)', r'删除5-1:<u>\1</u>'],
    [r'([\w\W]*)(\n[  \t]*(Abstract|Background)\n(\-{7,}))', r'删除6:<u>\1</u>(以上都删除)\2'],
    [r'((Author contributions:|Author Affiliations:)[^\n]*)', r'删除7:<u>\1</u>'],
    [r'((Acknowledgments|References|Author Information)\n(\-{7,})[\w\W]*)', r'以下都删除1:<u>\1</u>'],
    [r'((Members of the CDC Brazil Investigation Team:|\n[  \t]*Top|\*+Public Health and pharmacy:|### Box\.|On This Page)[^\n]*)', r'删除8:<u>\1</u>'],  # 一些特定无关段落
    [r'((\n[  \t]*(Drs?|M[sr]|Prof|Col\. G|Hanna Y)\.? )[^\n]+)', r'删除9:<u>\1</u>'],  # 人物介绍
    [r'([^,\.;\n] +)(\\?\[[\d\-,～~，;；–—、\s\\_]+\])', r'\1删除10:<u>\2</u>'],
    [r'(\n[  \t]*(Related Pages)[\w\W]*)', r'以下都删除2:<u>\1</u>'],

    [r'([\-]{3,})', ''],
]


class speicalProces:
    def __init__(self):
        pass

    def step1_del_wuguan(self, context):
        patter2 = r'([\(（][^\(\)（）\n]*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?[^\(\)（）\n]*[\)）]|\s*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?)'
        # patter3 = r'(Dr\.? |[Pp]rofessor |[Uu]niversity | is a |research(er)? )' # (Dr\.? [A-Za-z’ ]+ is an? |[Pp]rofessor |[Uu]niversity |research(er)? )
        website_list = re.findall(patter2, context)
        for web in website_list:
            if len(re.findall(r'(\.|:|\/\/)', web[0])) >= 2:
                if re.findall(r'([\(\)（）])', web[0]):
                    context = re.sub(re.escape(web[0]), rf'删除2:<u>{web[0]}</u>', context)
                else:
                    context = re.sub(r'([^\n\.]*' + re.escape(web[0]) + r'[^\n\.]*\.?)', r'删除2-1:<u>\1</u>', context)
        # if len(re.findall(patter3, context)) >= 3:
        #     context = "(此段删除)无关文本-1:" + context
        #     # context = ""
        return context



def clean_text(context):
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    # 1.正则
    for pattern_item in pattern_list:
        src = pattern_item[0]
        tgt = pattern_item[1]
        context = re.sub(src, tgt, context)

    # 分解处理
    result = []
    context = context.split(split_token)
    for item in context:
        item = sp.step1_del_wuguan(item)

        result.append(item)
    # 整合
    context = split_token.join(result)

    return context

def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n\s+\n', "\n\n", context)
    context = re.sub(r'\n\s+\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub(r"\n{2,}", "\n\n", context)
    # 对多标点进行替换
    context = re.sub(r'([：、？\.,\?;:])(\s*[：、？．\.,\?;:])+', r'\1', context)
    return context

def wuguan_ye(context):
    exit_flag = False
    wuguan = ["COMMENTARY_PCD_ s First", "“Antimicrobial Resistance of _"]
    for txt in wuguan:
        if txt in context:
            # context = "(本页删除)本页文本质量太差:\n" + context
            exit_flag = True
            break
    return exit_flag

def run_process(context):
    if wuguan_ye(context):
        return ''
    context = post_process(context)
    context = clean_text(context)
    context = post_process(context)
    return context

def process_item(item, fw):
    # 去除可能的空白字符
    item = json.loads(item.strip())
    # 处理文本
    context = run_process(item["text"])
    # 更新字典
    item["text"] = context
    # 将字典转换回JSON字符串
    item = json.dumps(item, ensure_ascii=False) + "\n"
    # 写入文件
    fw.write(item)

def threaded_process(items, fw):
    # 创建线程列表
    threads = []
    # 为每个项目创建并启动一个线程
    for item in items:
        thread = threading.Thread(target=process_item, args=(item, fw))
        threads.append(thread)
        thread.start()
    # 等待所有线程完成
    for thread in threads:
        thread.join()

#读jsonl
fw = open("C:/Program Files/lk/projects/pdf/cdc/cdc_preformat_clean1.jsonl", "w", encoding="utf-8")
with open("C:/Program Files/lk/projects/pdf/cdc/cdc_preformat.jsonl", "r", encoding="utf-8") as fs:
    num = 2141
    lines = fs.readlines()#[num-1:num]
    new_list = random.sample(lines, 300)
    for items in tqdm(new_list):
        item = json.loads(items.strip())
        context = item["text"]
        # print(context, '\n-------------------')
        context = post_process(context)
        context = clean_text(context)
        context = post_process(context)
        # print(context)
        item["text"] = context
        # print(item["text"], "\n--------------------------------------------------")
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
fw.close()



