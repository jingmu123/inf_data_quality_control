import json
import os
import re
import random
import threading
import time
from multiprocessing import Pool
import wordninja
import jieba
from tqdm import tqdm

pattern_list = [

    # [r'。', r'\.'], [r'，', r','], [r'；', r';'],
    [r'(<[\/\w]+>,? ?)+', ''],
    [r'(\n[  \t\*\.\w#]*([Ff]unding)[\w ]*\n[\w\W]*?\n)([^\n]+\n(\-{7,})|To read this article in full|This article is available free)', r'删除5:<u>\1</u>\n\3'],
    [r'(\n[  \t\*#]*(This article is available free|To read this article in full|Authors?’? [Cc]ontributions?|Contributors|Article info|Appendix|The following are the supplementary|GBD 2016 Neurology Collaborators|Supplementary Material|Conflict of interest statement|Author statement|Declaration of Interests)[\w\W]*)', r'以下都删除1:<u>\1</u>'],
    [r'([\(（][  \t]*([Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|[Nn]o\.|pp? \d+|panel|[Ss]upplementary|[Ll]ink)[^\(\)（）\n]*[\)）])', r'删除2:<u>\1</u>'],
    [r'([\(（][^\(\)（）\n]*?)(([,;] *([Ff]ig|[Tt]able|[Aa]ppendix|[Nn]o\.|pp? \d+|panel|[Ss]upplementary|[Ll]ink)[^\(\)（）\n,;]*)+)([^\(\)（）\n]*[\)）])', r'\1删除2-1:<u>\2</u>\5'],
    # [r'([\(（][^\(\)（）\n]*?)(([,;] *([Ff]ig|[Tt]able|[Aa]ppendix)[^\(\)（）\n,;]*)+)([^\(\)（）\n]*[\)）])', r'\1删除2-1:<u>\2</u>\5'],

    [r'(\\?\[[\d\-,～~;–—、\s\\_]+\])', r'删除3:<u>\1</u>'],
    [r'(\n[  \t\*•]*(This online publication|Copyright|View|Fig(ure)?|Download|Show full caption|Open table)[^\n]*)', r'删除4:<u>\1</u>'],
    [r'(^[  \t\*]*(This online publication|Copyright|View|Fig(ure)?|Download|Show full caption|Open table)[^\n]*)', r'删除4-1:<u>\1</u>'],
    [r'(\\?\[(see|e\.g\.)[^\[\]]+\])', r'删除6:<u>\1</u>'],
    [r'([\(（][ ,]*[\)）])', r'删除7:<u>\1</u>'],
    [r'((This trial is registered|Please submit your paper|Bill Hayes\. Random House|EA has received fellowship funding)[^\n]*)', r'删除8:<u>\1</u>'],
    [r'([^\n]*(declare[\w ]*no|no[\w ]*declare)[^\n]*)', r'删除9:<u>\1</u>'],
    [r'(^[  \t\*]*Sir\n\n)', r'删除10:<u>\1</u>'],
    [r'([,;] see Fig\.[^\.]+)', r'删除11:<u>\1</u>'],
    [r'([\(（][^\(\)（）\n]*(\d+;[ \d\*]{2,}:[ –\-\d\*]{2,})[^\(\)（）\n]*[\)）])', r'删除12:<u>\1</u>'],
]


class speicalProces:
    def __init__(self):
        pass

    def step1_del_wuguan(self, context):
        count = 0
        patter2 = r'([\(（][^\(\)（）\n]*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?[^\(\)（）\n]*[\)）]|\s*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?)'
        website_list = re.findall(patter2, context)
        for web in website_list:
            if len(re.findall(r'(\.|:|\/\/)', web[0])) >= 2:
                count += 1
                if re.findall(r'([\(\)（）])', web[0]):
                    context = re.sub(re.escape(web[0]), rf'删除1:<u>{web[0]}</u>', context)
                else:
                    context = re.sub(r'([^\n\.]*' + re.escape(web[0]) + r'[^\n\.]*\.?)', r'删除1-1:<u>\1</u>', context)
            elif re.findall(r'(\.gov)', web[0]):
                count += 1
                context = re.sub(r'([^\n\.]*' + re.escape(web[0]) + r'[^\n\.]*\.?)', r'删除1-2:<u>\1</u>', context)
        if count >= 3:
            context = "(此段删除)无关文本-1:" + context
            # context = ""
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


def run_process(context):
    context = clean_text(context)
    context = post_process(context)
    return context

def process_item(item):
    # 去除可能的空白字符
    item = json.loads(item.strip())
    # 处理文本
    context = item["text"]
    title = item["title"]
    if title == "Department of Error":
        context = "(本页删除)本页文本质量太差:\n" + context
        # return None
    context = run_process(context)
    print(context, "\n--------------------------------------------------")
    # 更新字典
    item["text"] = context
    # 将字典转换回JSON字符串
    return json.dumps(item, ensure_ascii=False) + "\n"

def main(lines, fw):
    # 设置进程池大小
    with Pool(6) as pool:
        # 使用tqdm显示进度
         results = pool.map(process_item, lines)

    # 将结果写入文件
    for item in results:
        if item:
            fw.write(item)


if __name__ == "__main__":
    #读jsonl
    fw = open("C:/Program Files/lk/projects/pdf/lancet/lancet_preformat_clean2.jsonl", "w", encoding="utf-8")
    with open("C:/Program Files/lk/projects/pdf/lancet/lancet_preformat.jsonl", "r", encoding="utf-8") as fs:
        start_time = time.time()
        num = 30113
        lines = fs.readlines()#[num-1:num]
        new_list = random.sample(lines, 300)
        main(new_list, fw)
        end_time = time.time()
        print(end_time - start_time)
    #     for items in tqdm(lines):
    #         item = json.loads(items.strip())
    #         context = item["text"]
    #         # print(context, '\n-------------------')
    #         context = post_process(context)
    #         context = clean_text(context)
    #         context = post_process(context)
    #         # print(context)
    #         item["text"] = context
    #         print(item["text"], "\n--------------------------------------------------")
    # #         item = json.dumps(item, ensure_ascii=False)
    # #         fw.write(item + "\n")
    fw.close()



