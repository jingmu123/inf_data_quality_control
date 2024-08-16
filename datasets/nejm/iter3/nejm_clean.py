import json
import os
import re
import random

import jieba
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm




import json
import os
import re
import random

import jieba
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"

pattern_list = [
    # [r'(^([Ff]igs?(ure)?s?|F\s?IGS?(URE)?s?|Ref|DOI|Table)\s\d+[^\n]*)',r'删除1:<u>\1</u>'],    # 固定形式  Figure|Table|DOI|REF 开头  删除整行
    [r'(\(pages?\s[^\(\)]*\))',r''],   # 固定格式 （page ...）
    [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|Details|Appendix|Funded|Section|epoch|Panels?|[sS]ee|for example, see|Supplementary Appendix|For more)s?[\s\.][^\(\)]*\))',r''],   # 固定格式  带有（）的图片表格描述 附录描述 协议描述
    [r'([^\dm]+\s?)(<sup>(<a>)?[\d\s\-—,]{1,20}(</a>)?</sup>)',r'\1'],   # 特殊格式的数字引用删除
    [r'<sup>(<a>)?[\s,]{1,5}(</a>)?</sup>',r''],
    [r'(\([^\(\)]{,40}N Engl J Med[^\(\)]{,40}\))',r''],     # 带有括号的引用 例(N Engl J Med 300:9–13, 1979)
    [r'§',r''],    # 一个特殊符号

    [r'(\([^\(\)]*\s(NCT|ISRCTN|Panels?)\d[^\(\)]*\))',r''],    #固定形式  删除（... NCT112233 ...） 描述什么机构 拨打电话
    # # [r'(\.)(([^\.]*\d+\.[^\.]*)?([^\.]*.( .){1,5}$))',r'\1删除6:<u>\2</u>'],     #删除以... 省略的后半句，中间允许出现一个数字加点
    [r'(\([^\(\)]*(www\.|NEJM\.org|nejm\.org|https?:|versions?\s?\d|opens? in new tab)[^\(\)]*\))',r''],    # 匹配带括号且有网址特征的句子
    [r'(([^\.]*\d+\s?\.){0,3}[^\.]*(at NEJM\.org|www\.nejm\.org|opens? in new tab)\.)',r''],   # 带有NEJM.org描述但是没有括号的句子 删除8只能在删除7后面
    [r'(\(\d+:\d+\) Download)',r''],    # 一个时间 一个下载
    [r'([\(_]{0,}\d+:\d+[\)_]{0,})',r''],  # 时间

    [r'^((Table|Figure) \d\.)(\s+(Table|Figure) \d\.)',r'\1'],  # Table 1.  Table 1. 重复问题
    [r'^.{0,30}/NEJM.{0,30}$',r''],   #  10.1056/NEJMoa2117995-t2   特殊字串
    [r'†|‡|¶|‖|\\\*',r''],   # 特殊符号

    [r'^Download\s.*',r''], # 下载...
    [r'^.{0,3}(Editor.s note|To learn more about).*',r'']   # 编辑信息 更多信息

]

class speicalProces:
    def __init__(self):
        pass

    def step1_reference(self, context):
        new_context = []
        first_paragraph = context[0]
        references_started1 = False  # 初始化 references_started 变量
        references_started2 = False
        CitingArticles_started1 = False  # 初始化 CitingArticles_started 变量
        CitingArticles_started2 = False
        if re.search(r'\*[^\n]*References?', first_paragraph):
            references_started1 = True  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
            context[0] = "参考删除-0" + context[0]
        elif re.search(r'\*[^\n]*(Citing Article|Related Article)s?', first_paragraph):
            CitingArticles_started1 = True  # CitingArticles_started开关   定义CitingArticles_started是因为他和有References出现的页开始删除的地方有所不同
            context[0] = "参考删除-0" + context[0]
        for index, item in enumerate(context):
            if re.search(r'^(References?|Funding and Disclosures|Polls on Public)\s', item.strip()):
                references_started2 = True
            if re.search(r'\.[A-Z][a-z]?\.\s+\n', item.strip()):
                CitingArticles_started2 = True
                references_started2 = True

            if references_started1 and references_started2:
                item = "参考删除-1:{}".format(item)
            if CitingArticles_started1 and CitingArticles_started2:
                item = "参考删除-2:{}".format(item)
            # if (not references_started1 and references_started2) or (not CitingArticles_started1 and CitingArticles_started2):
            #     item = "无关删除-1:<u>{}</u>".format(item)
            if re.search('^参考删除-\d:Table \d\.',item):
                item = re.sub(r'参考删除-\d:(.*)',r'\1',item)
                references_started1 = False
                CitingArticles_started1 = False
            # if not references_started1 and references_started2:
            #     item = "无关删除-1" + item

            new_context.append(item)
        return new_context

    def step2_wuguantext_following(self, context):
        new_context = []
        references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(
                    r'^(Funding and Disclosures|Polls on Public|Author Affiliations|Historical Journal Articles Cited)',
                    item.strip()) :
                references_started = True
            if references_started:
                item = "无关删除-1" + item
            new_context.append(item)
        return new_context

    def step4_rm_kongge(self, context):
        context = context.lstrip().rstrip()
        content = context.split(" ")
        first_content = content[0]
        last_content = " ".join(content[1:])
        final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', last_content)
        # 多执行一次，弥补正则边界重叠问题；
        final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', final_content)
        if len(final_content) == 0:
            return first_content

        merge_piece = first_content + final_content.lstrip()[0]

        split_word = list(jieba.cut(merge_piece, cut_all=False))
        if len(split_word[-1]) > 1:
            return first_content + final_content
        return first_content + " " + final_content

def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    # 分解处理
    result = []
    sp = speicalProces()
    context = context.split(split_token)
    context = sp.step1_reference(context)
    context = sp.step2_wuguantext_following(context)
    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)
        if lang == "zh":
            item = sp.step4_rm_kongge(item)
        result.append(item)
    for item in result:
        print(item)

    deleted_context = []
    for item in result:
        if re.search(r"(参考|无关)", item):
            continue
        deleted_context.append(item)
    # 整合
    context = split_token.join(deleted_context)

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
    # 对多标点进行替换
    context = re.sub(r'[。，](\s?[。，：；]){1,5}',r'。',context)
    context = re.sub(r'[,\.](\s+[,\.]){1,5}',r'\.',context)
    return context



fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean3_nejm_preformat.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\nejm_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    # sampled_lines = random.sample(lines, 1000)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "16c660a2-c629-487d-8cbf-e2724dafbfcc":
        context = item["text"]
        lang = item["lang"]
        if re.search(r'(\. \. \.|\. \. \.)$',context):   #跳过结尾带有省略的数据
            continue
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        print(item)
        fw.write(item + "\n")
