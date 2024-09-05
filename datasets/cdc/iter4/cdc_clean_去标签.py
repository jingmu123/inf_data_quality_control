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

    [r'(<[\/\w]+>)+', ''],
    [r'([^,\.;\n] +)([\(（][\d\-,\\～~;–—、−\s_]+[\)）])', r'\1'],
    [r'(et al\.|spp\.)( *[\(（][\d\-,\\～~;–—、−\s_]+[\)）])', r'\1'],
    [r'([\(（][\d\-,～~;–—、−\s_]+[\)）])([\.,;])', r'\2'],
    [r'( \d[\d_]*)(\n)', r'\2'],
    [r'([\(（][^\(\)（）\n]*(TOX|comm\.|[Nn]o\.|Video|\.gov )[^\(\)（）\n]*[\)）])', r''],
    [r'([\(（][  \t\*]*(E\. |online|http:|toll|[Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|Technical)[^\(\)（）\n]*[\)）])', r''],
    [r'([\(（][^\(\)（）\n]*?)(([,;] *([Ss]ee |[Ff]ig|[Tt]able|[Aa]ppendix|Technical)[^\(\)（）\n,;]*)+)([^\(\)（）\n]*[\)）])', r'\1\5'],
    # [r'([\(（][^\(\)（）\n]*?)(([,;] *([Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|Technical)[^\(\)（）\n,;]*)+)([^\(\)（）\n]*[\)）])', r'\1删除4-2:<u>\2</u>\5'],

    # [r'(\n[  \t\*#]*(Figure|Table|Appendix|Footnotes|Video)[^\n]*)', r'删除5:<u>\1</u>'],
    [r'(^\**(On This Page|Figure|Table|Appendix)[^\n]*)', r''],
    # [r'([^\n\.]*?((\d\.\d)[^\n\.]*?)*((Figures?|Tables?|Appendix)[\d\-～~–—\. _]+(shows?|reports?)| (in|from)[\w ]+(Figures?|Tables?|Appendix) \d)[^\n]*?\.)([ \n])', r'删除5-1:<u>\1</u>\9'],
    [r'([\w\W]*)(\n[  \t#]*(Abstract|(LTAS )?Background)\n)', r'\2'],
    [r'(\n[  \t\*#]*(Author contributions:|Author Affiliations:|COVID-19 Registries Study Group members:|Sources:)[^\n]*)', r''],
    # [r'((Acknowledgments|References|Author Information)\n(\-{7,})[\w\W]*)', r'以下都删除1:<u>\1</u>'],
    [r'(\n[  \t\*#]*(Of 107 manuscripts|Members of the CDC Brazil Investigation Team:|Top[ \n$]|Public Health and pharmacy:|On This Page|Dial |CAS#:|Image source:|Members of the Spanish Fusariosis|94\\. Flexner S . Experimental)[^\n]*)', r''],  # 一些特定无关段落
    [r'([^\n]*(\n[  \t\*]*(Drs?|M[sr][sr]?|Miss|Prof|Col\. G|Hanna Y|Carmen C\.H|S\.C\.A\.C)\.? (\w+\.)?[^\.]* ?(is|received|[Rr]esearch(ers)?|works?|qualified|directs) )[^\n]+)', r''],  # 人物介绍
    [r'(\\?\[[\d\-,～~，;\*–—、\s\\_]+\])', r''],
    [r'(\n[  \t\*#]*(Fast Facts\n\nFirearm|[a-z]+ icon\n|Bibliography|Appendix\n|ADDITIONAL RESOURCES|Safety & Health Outcomes)[\w\W]*)', r''],
    [r'(\n[  \t#]*(Acknowledgments|References?|Author Information|More Information|Diagnostic References:|Additional Resources)[  \t]*\n[\w\W]*)', r''],
    [r'([\w\W]*\n[  \t]*(Author\(s\):|Pages:|_Suggested citation for this article:_|Price:)[^\n]+)', r''],
    [r'(Back to top)', r''],
    [r'([^\n\.]*((was|are) supported (in part )?by )[^\n\.]*)', r''],
    [r'(\\?\[[^\[\]]*(Source:|[Ff]igure)[^\[\]]*\])', r''],
    [r'(It is almost worth buying[^\n]*)',  r''],
    [r'(CHC \d+, team leader)', r''],
    [r'(\nTop$)', r''],
    [r'([^\n]*\(4 5\/16 × 3 7\/16 in\/11 × 8\.7 cm\)[^\n]*)', r''],
    [r'(\()([\d\-,\\～~;–—、−\s_\*]+)([^\(\)]+\))', r'\1\3']

]


class speicalProces:
    def __init__(self):
        pass

    def step1_del_wuguan(self, context):
        patter2 = r'([\(（][^\(\)（）\n]*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \-@]{2,})\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?[^\(\)（）\n]*[\)）]|\s*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \-@]{2,})\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?)'
        # patter3 = r'(Dr\.? |[Pp]rofessor |[Uu]niversity | is a |research(er)? )' # (Dr\.? [A-Za-z’ ]+ is an? |[Pp]rofessor |[Uu]niversity |research(er)? )
        website_list = re.findall(patter2, context)
        for web in website_list:
            if len(re.findall(r'(\.|:|\/\/)', web[0])) >= 2:
                if re.findall(r'([\(\)（）])', web[0]):
                    context = re.sub(re.escape(web[0]), r'', context)
                else:
                    context = re.sub(r'([^\n\.]*' + re.escape(web[0]) + r'[^\n\.]*\.?)', r'', context)

        return context

    def step2_del_paragraph(self, context):
        patter1 = r'(\n[  \t#]*(Acknowledgments|References?|Author Information|More Information|Diagnostic References:|Additional Resources)[  \t]*\n[\w\W]*)(\n[  \t#]*Tables[  \t]*\n)'
        patter2 = r'(\n[  \t\*#]*(Fast Facts\n\nFirearm|[a-z]+ icon\n|Bibliography|Appendix\n|ADDITIONAL RESOURCES|Safety & Health Outcomes)[\w\W]*)(\n[  \t#]*Tables[  \t]*\n)'
        patter3 = r'(\n[  \t\*#]*(Figure|Appendix|Footnotes|Video)[^\n]*)'
        patter4 = r'(\n[  \t\*#]*(Figure|Table|Appendix|Footnotes|Video)[^\n]*)'
        if len(re.findall(r'\|', context)) >= 7 and re.search(r'(\n[  \t#]*Tables[  \t]*\n)', context):
            context = re.sub(patter1, r'\3', context)
            context = re.sub(patter2, r'\3', context)
            context = re.sub(patter3, r'', context)
        else:
            context = re.sub(patter4, r'', context)

        return context


def clean_text(context):
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    context = sp.step2_del_paragraph(context)

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
    item = json.loads(item.strip())
    context = item["text"]

    wuguan = ["COMMENTARY_PCD_ s First", "“Antimicrobial Resistance of _", "\n_CDC Yellow Book:",
              "In the article “Identifying Supports", "Several test orders", "Two funding sources were inadvertently",
              "The author list was incorrect in the article", "The name of author Anne", "The article Hendra Virus", "The name of author Beth Feingold", "A second affiliation for"]
    for txt in wuguan:
        if txt in context:
            # context = "(本页删除)本页文本质量太差:\n" + context
            # break
            return None

    context = run_process(context)
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
                if result:
                    fw.write(result)
                pbar.update()


if __name__ == "__main__":
    #读jsonl
    fw = open("C:/Program Files/lk/projects/pdf/cdc/cdc_preformat_clean4.jsonl", "w", encoding="utf-8")
    with open("C:/Program Files/lk/projects/pdf/cdc/cdc_preformat.jsonl", "r", encoding="utf-8") as fs:
        num = 6795
        lines = fs.readlines()#[num-1:num]
        start_time = time.time()
        new_list = random.sample(lines, 300)
        main(new_list, fw)
        end_time = time.time()
        print(end_time - start_time)
    fw.close()



