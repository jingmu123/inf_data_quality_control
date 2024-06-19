import json
import os
import re
from pprint import pprint

from tqdm import tqdm

log = open('../../../../full_data/dingxiangyuan/log.txt', 'w', encoding="utf-8")
# pattern_list_zh = [
#                    [r'\\|`|^',''],# 匹配文本中多余符号\、`、^
#                    ['图片来源：.*',''],#图片来源：visualdx
#                    [r'<br/><br/>',''],
#                    ['(<sup>)?(\\\\)?(\\[|［)(\\d+|(\\d+[,.、~～-]\\s*\\d+.*))(\\\\)?(\\]|］)(</sup>)?',''],#<sup>[1]</sup>
#                    ['<sup>',''],
#                    ['【.*日期.*】',''],#【 核准日期 】【 修改日期 】
#                    [r'\d{4}-\d{2}-\d{2}',''],#2008-07-23
#                    [r'（?图\s*\d+:.*?）?','']#图 2：医疗器械）
#                      ]
pattern_list_zh = [
    [r'(?:[^。]*\.\.\. )?登录', ''],  # 删除登录
    [r'\\+\[[^\u4e00-\u9fa5]*?\\+\]', ''],
    [r'\\+[\[\]]', ''],
    [r'\\|`|\^', ''],  # 匹配文本中多余符号\、`、^   #new 增加了\^
    [r'.*图片来源：.*', ''],  # 图片来源：visualdx  #new 在前面增加了范围
    [r'<br/>+', '\n'],  # 替换成\n  禁用<br/><br/>7、难治
    [r'<sup>.*?</sup>', ''],  # 去除sup
    [r'【[^【]*(?:日期| 药品图片 )[^】]*】', ''],  # 【 核准日期 】【 修改日期 】
    [r'\d{4}-\d{2}-\d{2}', ''],  # 2008-07-23
    [r' *<\/?sub> *', ''],  # 删除sub
    # 搬的丁香医生代码
    [r'（如?上?下?面?左?[^（]*图[ ，示]*?片? ?[\d\w]?\d? ?）', ''],#删除带图的内容
    [r'图中：[\u4e00-\u9fa5，]*', ''],  # 简单数据匹配
    [r'(?:具体)?如图：', ''],# 简单数据匹配
    [r'.*更多内容.*?。', ''],# 简单数据匹配
    [r'动作链接：[\u4e00-\u9fa5\w\.\d ]*', ''],#带动作链接
    [r'\*\*.*?(?:高能预警 ?↓?)\*\*|高能预警↓|👇', ''],#无关文本删除
    [r'(?:https?://|网站：|[^\n]*(?:图 \d\，)?图片来源：?:?\xa0?|图 1，来源：)(?:www)?[^\n]*|www.g6pd.*org', ''],#删除特定内容，部分可能多余
    [r'(?:(?:（?图 ?\d .*)?来源：自?|多余毛发的去除 )UpToDate(?: ?临床顾问）?)?', ''],#删除特定内容，部分可能多余
    [r'.*(?:图 ?\d\.|图源|图 \d：|图\W\.|皮肤性病诊断图谱|图片：).*', ''],#删除无关文本
    [r'\*\*\d\. (?:头部控制|腹部悬吊|垂直悬吊)试验，?(?:\*\*)?', ''],#匹配特定的文本
    [r'（[^（）人海以]*(?:[参详]|点击|见[下])[^（）加]*）', ''],#删除（参看禁忌一栏） 必须有中文括号
    [r'关于[^。！？]*?详见[^。！？]*?内容。?', ''],#匹配单个内容
    [r'(?:[^。？(?:\n\n)]|(?:可点击))*详情[^。\n\*]*[\n。]?', ''],#匹配无关文本

    [r'\[\d+\]', ''],  # 删除数字角标等
    [r'参考资料[\s\S]*', ''],  # 简单数据匹配
    [r'数据来源：', ''],  # 简单数据匹配
    ['.*见下图：', ''],  # 简单数据匹配
    ['。[^。]*tbody[^。]*。', ''],  # 简单数据匹配
    ['\x80-\x9e¢®¿£¬©¨¸\xad¶¡¦§]+', ''],  # 删除特殊符号
    [r'\([详参]见[^\)）]*[）\)]', '']  # 删除带括号的参见详见等内容

]
pattern_jiance=[
    [r'.*(?:图 ?\d\.|图源|图 \d：|图\W\.|皮肤性病诊断图谱|图片：).*', ''],

]#检测表达式列表

class speicalProces:
    def __init__(self):
        pass

    # 去除 ...登录 问题
    def step1_drop_login(self, content):
        split_token = "\n\n"
        if split_token not in context:
            split_token = "\n"
        pattern = r'录登\s*\.\.\.(.*?)[。，,、：:；(]'
        text = content.strip(' ').split(split_token)
        for i in range(len(text)):
            text[i] = re.sub(pattern, '。', text[i][::-1])[::-1]
        for i in range(len(text)):
            pattern1 = r'[\u4e00-\u9fa5]/[\u4e00-\u9fa5]'  # 删除中文文本中多余的/，如医/院，但是不删除单位里的/，如kg/m2
            sq_list = re.findall(pattern1, text[i])
            for j in sq_list:
                if j in text[i]:
                    text[i] = text[i].replace(j, j.replace('/', ''))
        text = split_token.join(text)
        return text

    # 去除空格问题
    def step2_strip(self, context):
        split_token = "\n\n"
        if split_token not in context:
            split_token = "\n"
        new_context = []
        context = context.split(split_token)
        for item in context:
            item = item.lstrip().rstrip()
            context_s = item.split("\n")
            for i in range(len(context_s)):
                context_s[i] = context_s[i].lstrip().rstrip()
            item = "\n".join(context_s)
            new_context.append(item)
        return split_token.join(new_context)


def clean_text(context):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    result = []
    sp = speicalProces()
    # context = sp.step1_drop_login(context)
    for item in context.split(split_token):
        item = item.strip(split_token)
        for pattern_item in pattern_list_zh:
            b = re.findall(pattern_item[0], item)
            for i in b:
                if i != '' and pattern_item in pattern_jiance:
                    log.write(str(i) + '\n')
            item = re.sub(pattern_item[0], pattern_item[1], item)
        result.append(item)
    context = split_token.join(result)

    return context


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # context = re.sub('\n\n-*', "", context)
    context = re.sub(r'\n-{3,}\n', "", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context


fw = open("../../../../full_data/dingxiangyuan/dingxiangyuan_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/dingxiangyuan/dingxiangyuan_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = post_process(context)
        context = clean_text(context)
        sp = speicalProces()
        context = post_process(context)

        context = sp.step2_strip(context)
        context = re.sub(r'(\n\n【[^】]* *】)+(\n\n【[^】]* *】)', r'\2', context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
