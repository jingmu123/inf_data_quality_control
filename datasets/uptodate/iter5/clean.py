import json
import os
import re
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

cite_other_sent = r".*?详见.*?(专题|上下文)"
url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"
pattern_list_zh = [
                   r'文中有.*具体指导。',
                   r'\((基础篇|高级篇|Beyond the Basics|见下文)\)',
                   r'\(参见.*\)',
                   r"(((基础|高级)篇)?(\(参见.*\))?)|(患者教育\s*[：—-].*(\(基础篇\))?)|(Patient education:.*)",
                   '\((流程图|figure|NCT|Grade|视频|计算器|波形|表|表格|图|图片)(\s+)?\d+.*?\)',
                   '\(图.*?\)',
                   r'\[\d+([,，、-]\d+)*\]',
                   r'\(参见\s*[^（]+(\([^)]*\))?[^)]*\)',
                   '参见网页\(here\)',
                   r'关于.*参见.*(\n.*[：:].*)*',
                   r'(\(.*?[图表]\s*.*?\d+\))|(\(\d+-\d+-\d+.*?\))',
                   r'(.*)学会指南链接(.*)',
                   r'(.*)见(.*)专题(.*)',
                   r'.*相应专题中讨论.*',
                   r'(.*)或其他专题(.*)',
                   r'更多|总结与推荐|总结|(\(影像.*?\))|在线资源和支持组织|信息参见网站：', '●|•',
                   r'(^\s*(–|—))|((-|–|—)\s*$)',
                   '(\\\\)?\[(\d+|(\d+,\d+.*))(\\\\)?\]',
                   r'\((\[?)\s*#?((\d+-\s*\d+)|(\d+(,|，)\s*\d+.*)|(\d+))(\]?)\)',
                   '.*(参见附图|详见).*','.*见参考文献.*','.*the website.*','致谢.*'
                     ]
pattern_list_en = [
                   r'\s*●\(See.*',
                   r'\[\d+([,，、-]\d+)*\]',
                   r'\*\s\s\s*urn:lims:\w+:\w+\s.*?No\s',
                   r'\*\s\s\s*urn:lims:\w+:\w+\s.*?•\s',
                   r'Yes',
                   ' ?View Patient Education ',
                   r'\((picture|figure|table)\s.*\)',
                   r'\((See|see).*?\)',
                   r'\(show table.*\)',
                   r'\*\s+[a-zA-Z]+-[a-zA-Z]+;',
                   r'\*\s*[a-zA-Z]+;',
                   r'(.*)(for|For) additional information(.*)',
                   r'(.*)See individual agents(.*)',
                   r'(.*)Reference Range(.*)',
                   r'(.*)Consumer Information Use and Disclaimer(.*)',
                   r'(.*Last Reviewed Date.*)|(SUMMARY AND RECOMMENDATIONS)|SUMMARY|ACKNOWLEDGMENTS|(SOCIETY GUIDELINE LINKS)',
                   r'(.*\(第\d+版\))|(.*专家共识)|(.*(临时|防控)指南)|(学会指南链接：.*)|(Society guideline links:.*)|(.*指南专题)',
                   r'(More on this topic)|(Patient education:.*)',
                   r'●|•|❑',
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

def drop_sentenc(content):
    pattern3=r'。?.*见.*详.*?[。，]'
    pattern1=r'。?.*题专.*见.*?[。，]'
    pattern2=r'。.*表附见.*?[。，]'
    text=content.strip('\n').split("\n")
    for i in range(len(text)):
        text[i] = re.sub(pattern3, '。', text[i][::-1])[::-1]
        text[i]=re.sub(pattern1,'。',text[i][::-1])[::-1]
        text[i] = re.sub(pattern2, '。', text[i][::-1])[::-1]
    text='\n'.join(text)
    return text

def process_cite(data, pattern_list_zh, pattern_list_en):  # 原本第二个参数为输出文件名fw
    # with open(file, "r", encoding="utf-8") as fs:
    #     data = fs.read()
    #     # print(data)
    #     lang = detect_language(data)
    #     print(lang)
    result = []
    if lang == 'zh':
        data=drop_sentenc(data)
        for item in data.split("\n"):
            item = item.strip("\n")
            item = re.sub('，。','。',item)
            for pattern_item in pattern_list_zh:
                item = re.sub(pattern_item, '', item, flags=re.IGNORECASE)
            if "url:" not in item and endding_filter(item):
                # print(item)
                continue
            result.append(item)

            # fw.write(item + "\n")
    elif lang == 'en':
        data = re.sub(r'\\-', "-", data)
        for item in data.split("\n"):
            item = item.strip("\n")
            if len(item.split()) < 4:
                item = re.sub(r'\*\s+[a-zA-Z]+.*', "", item)
            for pattern_item in pattern_list_en:
                item = re.sub(pattern_item, '', item, flags=re.IGNORECASE)
            if "url:" not in item and endding_filter(item):
                # print(item)
                continue
            result.append(item)

            # fw.write(item + "\n")
    else:
        for item in data.split("\n"):
            item = item.strip("\n")
            for pattern_item in (pattern_list_zh + pattern_list_en):
                item = re.sub(pattern_item, '', item, flags=re.IGNORECASE)
            if "url:" not in item and endding_filter(item):
                # print(item)
                continue
            result.append(item)

    return result
    # fw.write(item + "\n")

#读txt
# for file in os.listdir("C:/Users/ThinkPad/Downloads/re_quality_eval/re_quality_eval/output/clean_cn/"):
#     if not file.endswith("txt"): continue
#     file = os.path.join("C:/Users/ThinkPad/Downloads/re_quality_eval/re_quality_eval/output/clean_cn", file)
#     fw = open(f"{file}.clean", "w", encoding="utf-8")
#     process_cite(file, fw)

#读jsonl
fw = open("../../../../full_data/uptodate/uptodate_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/uptodate/uptodate_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        # lang = detect_language(item["text"])
        lang = item["lang"]
        clean_text = process_cite(context, pattern_list_zh, pattern_list_en)
        clean_text = [line for line in clean_text if line.strip()]
        # print(clean_text)
        clean_text = ('\n'.join(clean_text)).strip('\n')
        #print(clean_text)
        item["text"] = clean_text
        # print(item)
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
