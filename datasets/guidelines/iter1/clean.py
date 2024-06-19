import json
import os
import re
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm


pattern_list_en=[
                 r'\b(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b',
                 '(.*Case\s\d+)|(cs:.*|it:.*|sr:.*|ISBN:.*|de:.*)|(Copyright)|(.*copyright.*)|.*IU\.S\..*',
                 '\.(.*?)for detailed recommendations(.*?)\.',
                 # '(.*?)((\d+(．|\\.|\.))|[\d+])(.*)((\d{4}.*((;|：|:)?).*)|(((;|：|:)?).*\d{4}))(.*)',
                 # '(.*?)((\d+(．|\\.|\.))|[\d+])?(.*)(\d(\s?)\d(\s?)\d(\s?)\d(\s?).*((;|：|:)?).*)',
                 '\(go to Results in Section \d+\)|(\(Recommendation.*?\))',
                 '(\(\d\s+References)?(\(See)?.*\.\.\.\sread more\s+\)\.',
                 r'(\(see|See\s+(Table|table|Figure|figure|Section).*?\))',
                 r'(Table|table|Figure|figure|Section)\s+\d+(\.?)',
                 r'\((Table|table|Figure|figure|Section).*?\)',
                 r'Additional information.*',
                 r'# (Table|Price|((Re)?(S|s)ource(s?))|Notes)',
                 r'(See|see also|also):?',
                 r'.*Fig\.\d+\sPubic.*',
                 r'\bOR\b|(.*\.{{Cite)|(.*further details.*)',
                 r'(\.(.*?)(See|see) also(.*?)\.)|(\.(.*?)can be found in(.*?)\.)'
                 r'.*\b(R|r)eference(s?)\b.*',
                 r'.*§.*-\s-\s-.*',
                 r'.*Cavernous\ssinus\saneurysm.*',
                 r'(.*Image Gallery.*)|(\(.*?MRI.*?\))',
                 r'(\(Images.*of.*?\)|(.*M1\s4BT.*)|Contact NICE)',
                 '(.*\d{4}.*(ISBN|Retrieved).*)',
                 r'\(\s*#?((\d+-\s*\d+)|(\d+(,|，)\s*\d+.*)|(\d+))\)',
                 '(via:.*)|(el ta\(\d+.*?\))',
                 '\(\d{4}-\d{4}\s+update.*?et al.\)?',
                 '\([a-zA-Z]+\s+et\sal.*\d{4}.?',
                 '(et\sal.\s+?)|(\([a-zA-Z]+.*et\sal.*\d{4}.*?\))',
                 '(F|f)or information about this.*',
                 r'(\..*?http://.*\.)|\(.*?http://.*?\)|((\()?www\..*((/.*?\))|(g?)))',
                 '\.\.\.',
                 '\(DO NOT EDIT\)',
                 '▶|●|©|®|(.*-\s↑.*)|(:-)|❑|†|¶|║|§|∧|™',
                 'American Samoa.*',
                 '(\(\s*\))|(\d+\s*\))'
                 ]


def detect_language(content):
    #print("context",content)
    lang = detect(content)
    if lang == "zh-cn":
        return "zh"
    if lang == "en":
        return "en"
    return "None"

def mv_ngram_repeat(content):
    content=re.sub('\\\.','.',content,flags=re.IGNORECASE)
    return content

def process_cite(context,pattern_list):
    result = []
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    for item in context.split(split_token):
        item = item.strip(split_token)
        for pattern_item in pattern_list:
            item = re.sub(pattern_item, '', item)
        result.append(item)
    return result

fw = open("guidelines_clean.jsonl","w",encoding="utf-8")
with open("full_data/guidelines.jsonl","r",encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        # lang = detect_language(item["text"])
        clean_text = process_cite(context,pattern_list_en)
        clean_text = [line for line in clean_text if line.strip()]
        # print(clean_text)
        clean_text = ('\n'.join(clean_text)).strip('\n')
        # print(clean_text)
        item["text"] = clean_text
        # item["lang"] = lang
        del item['tokens']
        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")