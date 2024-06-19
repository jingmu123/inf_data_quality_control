import json
import os
import re
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

cite_other_sent = r".*?详见.*?(专题|上下文)"
url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"
pattern_list_zh = ['(<sup>)?(\\\\)?(\[|［)(\d+|(\d+[,-~～]\d+.*))(\\\\)?(\]|］)(</sup>)?',
                   '(.*?)((\d+(．|\\.|\.))|[\d+])?(.*)((\d{4}.*(：|:).*)|((：|:).*\d{4}))(.*)',
                   '(.*?)((\d+(．|\\.|\.))|[\d+])?(.*)\d+,.*(\d+-\d+)?(\d{4})?.*',
                   '.*(et al)?.*\d{4}.*(\.)?',
                   '.*(参考文献|出版社).*',
                   '.*((\d版)|出版社).*\d{4}.*',
                   r'\(参见.*?\)',
                   r'\[\d+([,，、-]\d+)*\]',
                   r'(\(.*?[图表]\s*.*?\d+\))|(\((表|图|图片)\s+\d+.*?\))|(\(\d+-\d+-\d+.*?\))',
                    '●|•',
                   r'(^\s*(–|—))|((-|–|—)\s*$)',
                   r'\((\[?)\s*#?((\d+-\s*\d+)|(\d+(,|，)\s*\d+.*)|(\d+))(\]?)\)',
                   '小荷医典内容仅供医学科普使用，不能作为诊断治疗依据，具体请遵医嘱。',
                   '【提示】.*'   #最后一次标记完新修正
                ]
def endding_filter(content):
    if "打印" in content or "邮件" in content or "致谢" in content or "感谢" in content:
        return True
    if "uptodate" in content.lower():
        return True
    if len(re.findall(url_pattern, content)) >= 1:
        return True
    return False


def sentence_filter(content):
    sentences = content.split("。")
    sent_list = []
    for sent in sentences:
        if len(re.findall(cite_other_sent, sent)) > 0:
            print(sent)
            # if "，" in sent:
            #     sent = ",".join(sent.split(",")[:-1])
            #     print("fix",sent)
            # else:
            continue
        sent_list.append(sent)
    return "。".join(sent_list)

def duplicat(content):
    split_token = "\n\n"
    text=content.strip('\n').split(split_token)
    for i in range(1,len(text)):
        try:
            # if text[i].split(' ')[1]==text[i-1].split(' ')[1]:
            if text[i]== text[i - 1]:
                del text[i]

        except Exception as e:
            pass
    text=split_token.join(text)
    return text


def process_cite(data, pattern_list_zh):  # 原本第二个参数为输出文件名fw
    # with open(file, "r", encoding="utf-8") as fs:
    #     data = fs.read()
    #     # print(data)
    #     lang = detect_language(data)
    #     print(lang)
    result = []
    data=duplicat(data)
    split_token = "\n\n"
    for item in data.split(split_token):
        # item = item.strip("\n")
        for pattern_item in pattern_list_zh:
            item = re.sub(pattern_item, '', item, flags=re.IGNORECASE)
        if "url:" not in item and endding_filter(item):
            # print(item)
            continue
        result.append(item)
    return split_token.join(result)

fw = open("../../../../full_data/xiaoheyidian/clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/xiaoheyidian/all_data_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        clean_text = process_cite(context, pattern_list_zh)
        clean_text = clean_text.strip(" ").strip("\n").strip(" ").strip("\n")
        #消除空格问题
        context = re.sub(r'\n +\n', "\n\n", clean_text)
        context = re.sub(r'\n +\n', "\n\n", context)

        # 消除分界符失效  --*- 前面需要有连续两个\n;
        context = re.sub('[^\n]\n    --', "\n\n    --", context)
        # 去掉过多\n的情况
        context = re.sub("\n{2,}", "\n\n", context)

        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")