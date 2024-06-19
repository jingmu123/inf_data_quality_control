import json
import os
import re
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

pattern_list_en = [
                        [r'\b(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b', ''],
                        ['(.*Case\s\d+)|(cs:.*|it:.*|sr:.*|ISBN(:?).*|de:.*)|(Copyright)|(.*copyright.*)|.*IU\.S\..*', ''],# ...case 1、cs:13442112、it:1132313、ISBN2321311、...copyright...、...IU.S...
                        ['\.(.*?)for detailed recommendations(.*?)\.', ''],
                        ['(Return to top)|(Adapted from the FDA Package Insert)|(Loading. Please wait.)', ''],
                        ['\(go to Results in Section \d+\)|(\(Recommendation.*?\))', ''],
                        ['(\(\d\s*References)?(\(See)?.*\.\.\.\sread more\s*\)\.', ''],  # 1 References See...sread more.
                        [r'(\((see|See)\s*(Table|table|Figure|figure|Section)?.*?\))', ''],
                        [r'(\()?(Table|table|Figure|figure|Section|diagram|Appendix)\s*(\d+)?(\.?).*?(\))?', ''],
                        [r'Additional information.*', ''],
                        [r'# (Table|Price|((Re)?(S|s)ource(s?))|Notes)', ''],  ## Table、# Resource
                        [r'.*Fig\.\d+\sPubic.*', ''],
                        [r'\bOR\b|(.*\.{{Cite)|(.*further details.*)', ''],  # OR、...{{Cite、...further details...
                        [r'((\.)?(.*?)(See|(see also)|also)(:?)(.*?)(\.)?)|(\.(.*?)can be found in(.*?)\.)', ''],# See:...、...can be found in...
                        [r'.*\b(R|r)eference(s?)\b.*', ''],
                        [r'.*§.*-\s*-\s*-.*', ''],  # §...- - -...
                        [r'.*Cavernous\ssinus\saneurysm.*', ''],
                        [r'(.*Image Gallery.*)|(\(.*?MRI.*?\))', ''],  # ...Image Gallery...、(...MRI...)
                        [r'(\(Images.*of.*?\)|(.*M1\s4BT.*)|Contact NICE)', ''],  # (Images...of...)、...M1 4BT...、Contact NICE
                        ['(.*\d{4}.*(ISBN|Retrieved).*)', ''],  # ...1970...ISBN...、...1970...Retrieved...
                        [r'\(\s*#?((\d+-\s*\d+)|(\d+(,|，)\s*\d+.*)|(\d+))\)', ''],  # ( #(12-44))、( #(12.asdf))
                        [r'(via:.*)|(el ta(\(\d+.*?\))?)', ''],  # via:...、el ta(66english)
                        [r'\(\d{4}-\d{4}\s*update.*?et al.\)?', ''],  # (1980-1998 update in et al
                        [r'\([a-zA-Z]+\s*.*et\sal.*\d{4}(.*?\))?', ''],  # (today et al 1980 ,1999)
                        ['(F|f)or information about this.*', ''],
                        [r'(\..*?http://.*\.)|\(.*?http://.*?\)|((\()?www\..*((/.*?\))|(g?)))', ''],
                        ['\.\.\.', '\.'],
                        ['\(DO NOT EDIT\)', ''],
                        ['▶|●|©|®|(.*-\s↑.*)|(:-)|❑|†|¶|║|§|∧|™|☒', ''],
                        ['American Samoa.*', ''],
                        ['(\(\s*\))|(\d+\s*\))', ''],
                        # new
                        [r'-?.*,\s*\b(19|20)\d{2}\b.*?(\.)?', ''],  # - Copi, Irving. Symbolic Logic.  MacMillan, 1979, fifth edition.
                        [r'#?\s*References and notes.*', ''],  # References and notes
                        [r'.*(M\.D\.)?,\s*Ph\.\D.', ''],  # Steven C. Campbell, M.D., Ph.D.
                        [r'(For more information,)?\s*call\s*\d+-\d+-\d+-\d+.*?\.', '']# For more information, call 1-800-445-3235 or go to .
                    ]


class speicalProces:
    def __init__(self):
        pass


def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    if lang == 'en':
        pattern_list = pattern_list_en

    result = []
    sp = speicalProces()

    for item in context.split(split_token):
        item = item.strip(split_token)
        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)
        result.append(item)
        # 整合
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
    return context


fw = open("../../../../full_data/guidelines/guidelines_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/guidelines/guidelines_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        lang = item["lang"]
        context = clean_text(context, lang)
        context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")

