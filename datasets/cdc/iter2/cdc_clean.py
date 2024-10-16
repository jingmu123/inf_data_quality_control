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
    # [r'\|', ''],

    [r'(<[\/\w]+>)+', ''],
    [r'([^,\.;\n] +)([\(（][\d\-,\\～~;–—、−\s_]+[\)）])', r'\1删除1:<u>\2</u>'],
    [r'(et al\.|spp\.)( *[\(（][\d\-,\\～~;–—、−\s_]+[\)）])', r'\1删除1-1:<u>\2</u>'],
    [r'([\(（][\d\-,～~;–—、−\s_]+[\)）])([\.,;])', r'删除1-2:<u>\1</u>\2'],
    [r'(\d[\d\-,～~;–—、_]*)(\n)', r'删除1-3:<u>\1</u>\2'],
    # [r'(\n[  \t]*(Author Information)[\w\W]*)', r'删除3:<u>\1</u>'],
    [r'([\(（][^\(\)（）\n]*(strain|TOX|comm\.|Figure|Table|Appendix|[Nn]o\.|[Ss]ee|Video)[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>'],
    [r'(\n[  \t\*#]*(Figure|Table|Appendix|Footnotes|Video)[^\n]*)', r'删除5:<u>\1</u>'],
    [r'(^\**(Figure|Table|Appendix)[^\n]*)', r'删除5-2:<u>\1</u>'],
    [r'([^\n\.]*?((\d\.\d)[^\n\.]*?)*((Figures?|Tables?|Appendix)[\d\-～~–—\. _]+(shows?|reports?)| (in|from)[\w ]+(Figures?|Tables?|Appendix) \d)[^\n]*?\.)([ \n])', r'删除5-1:<u>\1</u>\9'],
    [r'([\w\W]*)(\n[  \t]*(Abstract|Background)\n(\-{7,}))', r'删除6:<u>\1</u>(以上都删除)\2'],
    [r'(\n[  \t\*#]*(Author contributions:|Author Affiliations:|COVID-19 Registries Study Group members:|Sources:)[^\n]*)', r'删除7:<u>\1</u>'],
    [r'((Acknowledgments|References|Author Information)\n(\-{7,})[\w\W]*)', r'以下都删除1:<u>\1</u>'],
    [r'(\n[  \t\*#]*(Members of the CDC Brazil Investigation Team:|Top|Public Health and pharmacy:|Box\.|On This Page|Dial |CAS#:|Image source:)[^\n]*)', r'删除8:<u>\1</u>'],  # 一些特定无关段落
    [r'([^\n]*(\n[  \t\*]*(Drs?|M[sr][sr]?|Prof|Col\. G|Hanna Y|Carmen C.H)\.?[^,\.]* is )[^\n]+)', r'删除9:<u>\1</u>'],  # 人物介绍
    [r'([^,\.;\n] +)(\\?\[[\d\-,～~，;；–—、\s\\_]+\])', r'\1删除10:<u>\2</u>'],
    [r'(\n[  \t\*#]*(Fast Facts\n\nFirearm|[a-z]+ icon\n|Bibliography|Appendix\n|ADDITIONAL RESOURCES|Safety & Health Outcomes)[\w\W]*)', r'以下都删除2:<u>\1</u>'],
    [r'(\n[  \t#]*(Acknowledgments|References?|Author Information)[  \t]*\n[\w\W]*)', r'以下都删除3:<u>\1</u>'],
    [r'([\w\W]*\n[  \t]*(Author\(s\):|Pages:|_Suggested citation for this article:_|Price:)[^\n]+)', r'<u>\1</u>\n(以上都删除2)'],
    [r'(Back to top)', r'删除11:<u>\1</u>'],
    [r'([^\n]*((was|are) supported (in part )?by )[^\n]*)', r'删除12:<u>\1</u>'],
    [r'(\\?\[[^\[\]]*(Source:|[Ff]igure)[^\[\]]*\])', r'删除13:<u>\1</u>'],
    [r'(It is almost worth buying[^\n]*)',  r'删除14:<u>\1</u>'],
    # [r'([\-]{3,})', ''],
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
    wuguan = ["COMMENTARY_PCD_ s First", "“Antimicrobial Resistance of _", "\n_CDC Yellow Book:", "In the article “Identifying Supports","Several test orders", "Two funding sources were inadvertently"]
    for txt in wuguan:
        if txt in context:
            context = "(本页删除)本页文本质量太差:\n" + context
            exit_flag = True
            break
    return context

def run_process(context):
    # if wuguan_ye(context):
    #     return ''
    context = wuguan_ye(context)
    context = clean_text(context)
    context = post_process(context)
    return context

def process_item(item):
    item = json.loads(item.strip())
    context = run_process(item["text"])
    # print(context, "\n--------------------------------------------------")
    item["text"] = context
    return json.dumps(item, ensure_ascii=False) + "\n"


def main(lines, fw):
    with Pool(6) as pool:
        # 创建一个用于存储AsyncResult对象的列表
        results = []
        # 使用tqdm显示进度
        for item in tqdm(lines, desc="Processing"):
            # 异步地将 process_item 函数应用到每个数据项上
            async_result = pool.apply_async(process_item, (item,))
            # 将AsyncResult对象添加到结果列表中
            results.append(async_result)

        # 使用tqdm显示写入进度
        with tqdm(total=len(lines), desc="Writing") as pbar:
            # 等待所有任务完成并写入结果
            for async_result in results:
                result = async_result.get()  # 获取任务结果
                fw.write(result)
                pbar.update()


if __name__ == "__main__":
    #读jsonl
    fw = open("C:/Program Files/lk/projects/pdf/cdc/cdc_preformat_clean2.jsonl", "w", encoding="utf-8")
    with open("C:/Program Files/lk/projects/pdf/cdc/cdc_preformat.jsonl", "r", encoding="utf-8") as fs:
        num = 2141
        lines = fs.readlines()#[num-1:num]
        start_time = time.time()
        new_list = random.sample(lines, 300)
        main(new_list, fw)
        end_time = time.time()
        print(end_time - start_time)
        # for items in tqdm(new_list):
        #     item = json.loads(items.strip())
        #     context = item["text"]
        #     # print(context, '\n-------------------')
        #     context = post_process(context)
        #     context = clean_text(context)
        #     context = post_process(context)
        #     # print(context)
        #     item["text"] = context
        #     # print(item["text"], "\n--------------------------------------------------")
        #     item = json.dumps(item, ensure_ascii=False)
        #     fw.write(item + "\n")
    fw.close()



