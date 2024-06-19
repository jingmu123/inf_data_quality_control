import json
import os
import re
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm



pattern_list_zh = [
                   [r'(?:[^。]*\.\.\. )?登录', ''],
                   [r'[\\`^]',''],
                   ['图片来源：.*',''],
                   [r'<br/(><br/>)?',''],
                   ['(<sup>)?(\\\\)?(\\[|［)(\\d+|(\\d+[，,.、~～-]\\s*\\d+.*))(\\\\)?(\\]|］)(</sup>)?',''],
                   [r'[^(<sup>\d.*)] </sup>',''],
                   ['【.*日期.*】',''],
                   [r'\d{4}-\d{2}-\d{2}',''],
                   [r'（?图\s*\d+:.*?）?',''],
                   ['·',''],
                   ['。.*如下表.*(所示)?',''],
                   [r'([\u4e00-\u9fa5]+)\/+([\u4e00-\u9fa5]+)',r'\1\2'],
                   [r'、、','、'],
                   [r'\(见下表.*?\)',''],
                   [r'[，].*参照下表',''],
                   ['\(表\s*\d+.*?\)','']
                     ]

class speicalProces:
    def __init__(self):
        pass
    def step1_drop_login(self,content):
        split_token = "\n\n"
        pattern1 = r'录登\s*\.\.\.(.*?)。'
        pattern2 = r'录登\s*\.\.\..*'
        text = content.split(split_token)
        for i in range(len(text)):
            text[i] = re.sub(pattern1, '。', text[i][::-1])[::-1]
            text[i] = re.sub(pattern2, '', text[i][::-1])[::-1]
        for i in range(len(text)):
            pattern3 = r'[\u4e00-\u9fa5]/[\u4e00-\u9fa5]' #删除中文文本中多余的/，如医/院，但是不删除单位里的/，如kg/m2
            sq_list = re.findall(pattern3, text[i])
            for j in sq_list:
                if j in text[i]:
                    text[i] = text[i].replace(j, j.replace('/', ''))
        for i in range(len(text)):
            pattern4 = r'[\u4e00-\u9fa5]-[\u4e00-\u9fa5]' #删除中文文本中多余的-，治-疗低糖血症
            sq_list = re.findall(pattern4, text[i])
            for j in sq_list:
                if j in text[i]:
                    text[i] = text[i].replace(j, j.replace('-', ''))
        for i in range(len(text)):
            pattern5 = r'[\u4e00-\u9fa5]\s+[\u4e00-\u9fa5]' #删除中文文本中多余的空格，如医 院
            sq_list = re.findall(pattern5, text[i])
            for j in sq_list:
                if j in text[i]:
                    text[i] = text[i].replace(j, j.replace(' ', ''))
        text=split_token.join(text)
        return text

    def step2_repair_parentheses(self, context, lang):
        stack = []
        # 将文本转换为列表，方便对着索引删除
        list_text = list(context)
        for i, char in enumerate(context):
            if char == '(' or char == "（" or char == '[' or char == '{':
                stack.append(i)
            elif char == ')' or char == "）" or char == ']' or char == '}':
                if not stack:
                    # 没有出现左括号,右括号直接删除
                    list_text[i] = ''
                else:
                    stack.pop()
        # 不为空说明有多余括号存在
        while stack:
            index = stack.pop()
            # 去除的括号用逗号代替
            if lang == 'zh':
                list_text[index] = '。'
            else:
                list_text[index] = ','
        return ''.join(list_text)

    def step3_strip(self, context):
        split_token = "\n\n"
        if split_token not in context:
            split_token = "\n"
        new_context = []
        context = context.split(split_token)
        for item in context:
            item = item.lstrip().rstrip()
            context_s=item.split("\n")
            for i in range(len(context_s)):
                context_s[i] = context_s[i].lstrip().rstrip()
            item="\n".join(context_s)
            new_context.append(item)
        return split_token.join(new_context)


def clean_text(context):  # 原本第二个参数为输出文件名fw
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    result = []
    sp = speicalProces()
    context=sp.step1_drop_login(context)
    for item in context.split(split_token):
        item = item.strip(split_token)
        for pattern_item in pattern_list_zh:
            item = re.sub(pattern_item[0], pattern_item[1], item)
            item = sp.step2_repair_parentheses(item,"zh")
        result.append(item)

    context = split_token.join(result)
    context = sp.step3_strip(context)

    return context


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;

    # context = re.sub('\n\n-*', "", context)
    context = re.sub(r'\n-{3,}\n', "", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context


fw = open("../../../../full_data/dingxiangyuan/dingxiangyuan_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/dingxiangyuan/dingxiangyuan_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        lang = item["lang"]
        context = clean_text(context)
        sp = speicalProces()
        context = post_process(context)
        context = re.sub(r'(\n\n【[^】]* *】)+(\n\n【[^】]* *】)', r'\2', context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")





