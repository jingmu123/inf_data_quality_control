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
                 'Return to top','Adapted from the FDA Package Insert.','Loading. Please wait.',
                 '\(go to Results in Section \d+\)|(\(Recommendation.*?\))',
                 '(\(\d\s+References)?(\(See)?.*\.\.\.\sread more\s+\)\.',
                 r'(\(see|See\s*(Table|table|Figure|figure|Section)?.*?\))',
                 r'(\()?(Table|table|Figure|figure|Section|diagram|Appendix)\s*(\d+)?(\.?).*?(\))?',
                 r'Additional information.*',
                 r'# (Table|Price|((Re)?(S|s)ource(s?))|Notes)',
                 r'.*Fig\.\d+\sPubic.*',
                 r'\bOR\b|(.*\.{{Cite)|(.*further details.*)',
                 r'((\.)?(.*?)(See|(see also)|also)(:?)(.*?)(\.)?)|(\.(.*?)can be found in(.*?)\.)'
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
    return split_token.join(result)

fw = open("../../../../full_data/guidelines/guidelines_clean.jsonl","w",encoding="utf-8")
with open("../../../../full_data/guidelines/guidelines_preformat.jsonl","r",encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        clean_text = process_cite(context, pattern_list_en)
        clean_text = clean_text.strip(" ").strip("\n").strip(" ").strip("\n")
        # 消除空格问题
        context = re.sub(r'\n +\n', "\n\n", clean_text)
        context = re.sub(r'\n +\n', "\n\n", context)

        # 消除分界符失效  --*- 前面需要有连续两个\n;
        context = re.sub('[^\n]\n    --', "\n\n    --", context)
        # 去掉过多\n的情况
        context = re.sub("\n{2,}", "\n\n", context)

        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
