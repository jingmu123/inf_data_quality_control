import json
import os
import re
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm


pattern_list_zh=['𬌗 /+.*',
              r'▶|●|©|®|(.*-\s↑.*)|(:-)',
              '(参考文献|来源|(摘自.*)|续表)',
              '(.*?)((\d+(．|\\.|\.))|[\d+])(.*)((\d{4}.*(：|:).*)|((：|:).*\d{4}))(.*)',
              '见表\s\d+-\d+-\d+',
              '(，|。)(参考|见|参见)(图|表)\d+-\d+(.*?)(，|。|；)',
              '(，|。)(.*?)(参考|见|参见)(图|表)\d+-\d+(.*?)(，|。|；)',
              '(.*?)见(图|表)\d+-\d+(，|。)',
              '\(?图\d+-\d+?\)',
              '（(表|图)\d+.*?）',
              '（\d+-.*?）',
              '［图\d+（\d+）(.*)］',
              '(.*)(图|表)\d+-\d+(.*?)(，|。)',
              '。(.*?)见(图|表)\d+-\d+(.*?)。',
              '(.*)(图|表)\d+-\d+(.*)*',
              '(.*)收藏(.*)已收藏(.*)',
              '(.*)(图|表)\d+(.*)',
              '图\d+-\d+',
              '.*第.*版.*' ]

def special(content):
    content=re.sub('\\\.','.',content,flags=re.IGNORECASE)
    return content

def process_cite(context,pattern_list):
    result = []
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    for item in context.split(split_token):
        item = item.strip(split_token)
        item = special(item)
        for pattern_item in pattern_list:
            item = re.sub(pattern_item, '', item, flags=re.IGNORECASE)
        result.append(item)
    for i in range(len(result) - 1):
        try:
            if '作者' in result[i]:
                result[i] = result[i].replace(result[i], '')
                result[i + 1] = result[i + 1].replace(result[i + 1], '')
                break
        except Exception as e:
            pass
    clean_text = split_token.join(result)
    # 消除空行问题
    context = re.sub(r'\n +\n',"\n\n",clean_text)
    context = re.sub(r'\n +\n',"\n\n",context)
    context = re.sub("\n{2,}","\n\n",context)
    return context

fw = open("../../../../full_data/renwei_linchuangzhushou/all_data_clean.jsonl","w",encoding="utf-8")
with open("../../../../full_data/renwei_linchuangzhushou/all_data_preformat.jsonl","r",encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        clean_text = process_cite(context,pattern_list_zh)
        item["text"] = clean_text.strip(" ").strip("\n").strip(" ").strip("\n")
        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")
        # break
