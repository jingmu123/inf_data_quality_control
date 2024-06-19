import json
import os
import re
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

cite_other_sent = r".*?详见.*?(专题|上下文)"
url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"
pattern_list_zh = ['(<sup>)?(\\\\)?\[(\d+|(\d+[,-]\d+.*))(\\\\)?\](</sup>)?',
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
                   r'\((\[?)\s*#?((\d+-\s*\d+)|(\d+(,|，)\s*\d+.*)|(\d+))(\]?)\)'
                     ]


def detect_language(content):
    # print("context",content)
    lang = detect(content)
    if lang == "zh-cn":
        return "zh"
    if lang == "en":
        return "en"
    return "None"


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
    text=content.strip('\n').split("\n\n")
    for i in range(1,len(text)):
        try:
            # if text[i].split(' ')[1]==text[i-1].split(' ')[1]:
            if text[i]== text[i - 1]:
                del text[i]

        except Exception as e:
            pass
    text='\n'.join(text)
    return text


def process_cite(data, pattern_list_zh):  # 原本第二个参数为输出文件名fw
    # with open(file, "r", encoding="utf-8") as fs:
    #     data = fs.read()
    #     # print(data)
    #     lang = detect_language(data)
    #     print(lang)
    result = []

    data=duplicat(data)
    for item in data.split("\n"):
        item = item.strip("\n")
        for pattern_item in pattern_list_zh:
            item = re.sub(pattern_item, '', item, flags=re.IGNORECASE)
        if "url:" not in item and endding_filter(item):
            # print(item)
            continue
        result.append(item)
    return result
    # fw.write(item + "\n")


# for file in os.listdir("C:/Users/ThinkPad/Downloads/re_quality_eval/re_quality_eval/output/clean_cn/"):
#     if not file.endswith("txt"): continue
#     file = os.path.join("C:/Users/ThinkPad/Downloads/re_quality_eval/re_quality_eval/output/clean_cn", file)
#     fw = open(f"{file}.clean", "w", encoding="utf-8")
#     process_cite(file, fw)

fw = open("xiaoheyidian_clean.jsonl", "w", encoding="utf-8")
with open("full_data/xiaoheyidian.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        seq_id = item["_id"]["$oid"]
        # item=item['source_info']
        context = item["text"]
        # lang = detect_language(item["text"])
        # lang = item["lang"]
        clean_text = process_cite(context, pattern_list_zh)
        clean_text = [line for line in clean_text if line.strip()]
        # print(clean_text)
        clean_text = ('\n'.join(clean_text)).strip('\n')
        # print(clean_text)
        item["text"] = clean_text
        item["id"] = seq_id
        # print(item)
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")