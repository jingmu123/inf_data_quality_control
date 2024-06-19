import json
import re
from pprint import pprint
from tqdm import tqdm

log_dict = {}
# 规则必须以列表形式存储，分别是要替换的内容，以及替换成什么内容
pattern_list = [
    # 初始简单错误修复，不会产生文本干扰
    [r'\d* *_\(_', ''],  # 无关文本删除
    [r'\?●', r'?\n\n●'],  # 对该格式错误进行修复
    [r'[@◎]? ?\d+ John Wiley & Sons\， Inc\. Published \d+ by John Wiley & Sons， Inc', ''],  # 清洗作者
    [r'(\(see ‘)?\*?\*?Syllabus Mapping\*?\*?(’below\))?',''], #无关文本
    #中文
    [r'([a-zA-Z_●\*\d])[\u4e00-\u9fa5]+_?', r'\1 '],  # ,判断前面为特殊符号清洗中文
    [r'^[\u4e00-\u9fa5]+|[\u4e00-\u9fa5]+$', ''],  # 中文开头或结尾的进行删除
    [r'[\u4e00-\u9fa5]?( ?)_?◆?[\u4e00-\u9fa5]+_?([a-zA-Z\n_●\*\d·\(])', r'\1\2 '],  # 判断后面为特殊符号清洗中文
    [r'[一川个入价八元心卜口斗必人课厂翼]([^\u4e00-\u9fa5])', r'\1'],  # 对特征与需要保留的中文进行单独替换处理
    #\\
    [r'\)?\\\[[^\*\)]*?\\\]\)?', ''],  # 删除\\[\\]\\\
    [r'\\\]', ''],  # 删除\\]
    [r'\\\[(\d+\.\d+1)?( ?\d+? ?,? ?\d+?)?_?', ''],  # 删除\\[+\d
    [r'\$\$\$\$ [^\$]*\$\$\$\$', ''],  #无关文本
    [r'\\\\[=\-_>\*\\\\ ]', ''],  #删除\\
    # ©
    [r'\((\w+)?,? ?Abbott ?(<sup>® +</sup>)?( +)?©?\)', ''],  # 删除Abbott
    # [r'(Reprinted.*University Press)?\(?(AliveCor)?(Copyright)?_? ?©( +)?(\d+)?\)?(_?\d+:\d+)?\.?', ''],  #删除©剩余内容
    [r'(” )?\(p. \d+\)', ''],  #删除(p. 117)
    #删除空格
    [r' +/?\)', ')'],  #删除空格
    [r'([//\(]) +', r'\1'],  # 删除空格

    #处理figure 速度慢，清洗不是很干净
    # [r' ?\(( +)?Figure[^\)]*\)', ''],  #clean figure  有 ()
    # [r'^[fF]igure.*',r''],#删除figure开头的所以文本 (存在部分误删)
    # [r'\([sS]ee Figure[^\)\*]*\)?',''], #删除带(see 的figure
    # [r'\([fF]ig[^\)\*]*\)?',''], #删除(flg.88.1)
    # [r'[^\.\*]*[fF]igure (\d+[\.-])+[^\.]*\.?',''],# 删除figure前后段
    #处理其他
    [r'\([^\(]*(Bin Li|Bing Wang)[^\)]*\)', ''],  #删除作者
    [r'\d+.  \d+.', ''],  # #\n\n4.  4.\n\n
    [r'\((ER; )?[Ss]ee also[^\)]*\)', ''],  #remove see also
    [r'\(?_?。?●?_? ?[Ss]ee also [^\.]*\.?', ''],  #remove see also
    [r'(?i)Case Files[\x80-\x9e¢®¿£¬©¨¸\xad¶¡¦§][\s\S]*', ''],  #删除®
    [r'[\x80-\x9e¢®¿£¬©¨¸\xad¶¡¦§†￾‡]', ''],  #删除®
    # http清洗:
    [r'iveser vicest', 'iveservicest'],  #干扰文本修复
    [r'http', ' http'],  #http前面加个空格
    [r'\( ?http[^ ]*\)', ''],  #根据括号进行删除
    [r'.*/.*ccessed.*', ''],  #删除http 存在部分误删
    [r'.*ccessed.*/.*', ''],  #删除http 存在部分误删
    [r'.*ccessed (at )?[A-Za-z]+ \d+.*', ''],  #
    [r'.*vailable at：.*', ''],  #删除http 存在部分误删
    [
        r'\(?(TLC; +)?(q3 )?(e.g., )?https?[:：]?//()?([Ww]ww\.)?(\w+)?\.?(\w+)?(\d+)?(\w+.htm)?[\\=\.\?\w%/\*†\-]*\)?( +)?\|?(\\\\_\d\.aspx)?([a-z\d]*\.html)?(\.)?(；)?',
        ''],  #匹配http
    [r'(see： )?(or )?\(?\(?(\w+)?www[\.\w+-/\\]+\)?', ''],  #删除www
    [r'(‐professionals/privacy/laws\‐)?(Source：)? ?(CDC：)?\(? ?[\w\.\\/\-]+\.html? ?\)?\.?', ''],  #补充
    [r'\([Ss]ee [Cc]ases ?([\(\)\d\-， \w\?]+)?\)', ''],  #删除see case
    [r'[\(●]?[Ss]ee Cases ?([\(\d\-， \w\?]+)?\)?\.?，?', ''],  #删除see case
    [r'CASE$',''], #结尾的case删除，没有内容
    [r'\*\*Questions\.\*\*$',''],  #结尾的Questions删除，没有内容
    [r'This page intentionally left blank ?(\d+)?',''],#删除无关文本
]
# 单个的无关文本替换
context_pattern = [
    ['A15% to 30%B30% to 50%', 'A.15% to 30%\n\nB.30% to 50%'],
    ['382).', ''],
    ['CASE CORRELATION', ''],
    ['￥', ''],
    ['(continued overleaf)', ''],
    ['First Edition. Edited by Leslie Neal-Boylan.', ''],
]


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context


class speicalProces:
    def __init__(self):
        pass

    def context_pre1(self, context):  # 文件分割前预处理 清洗中文文本 \n问题，
        context = re.sub(r'\n\n([^a-zA-Z]*[a-z])', r'\1', context)  # 修复\n问题，小写保留
        context = re.sub(r'(\n\n[^a-zA-Z]*[A-Z])', r'\1', context)  # 修复\n问题，大写删除
        context=re.sub(r'© Springer[\s\S]*?Email: [^\n]*\n\n','',context)
        context = re.sub(r'(Tien V|© )([^_]*?_\d+)?(Springer-Verlag London \d+)?', '', context)  # 必须预处理，无关文本过长，中间有\n\n
        context=re.sub(r'[^\n]*\n\nEmail:[^\n]*','',context) #名字加邮箱
        #全局清洗
        context = re.sub(r'​|﻿', '', context) #特殊符号
        context = re.sub(r'\*?\*?CASE CORRELATES.*', '', context)#无关文本
        context = re.sub(r'</?(sub?p?|a|em)>', '', context)  # 删除subp a,em
        context=re.sub(r'<span.*?</span>','',context) #删除span
        context=re.sub('_','',context)


        return context

    def context_last1(self, context):  # 文件分割合并后处理
        context = re.sub(r'\n\n.\n\n', r'.\n\n\n\n', context)

        return context


def clean_text(context, lang="zh"):
    # 如果存在特殊处理，以类的方式整合，初始化类；
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    result = []
    context = sp.context_pre1(context)

    for item in context.split(split_token):

        # 1.正则
        for pattern_item in pattern_list:
            if pattern_item[0] in [r'<\w+>[^<]*</\w+>']:
                if re.findall(pattern_item[0], item) != []:  # 检测模块，会消耗较多时间
                    if str(pattern_item[0]) not in log_dict:
                        log_dict[str(pattern_item[0])] = re.findall(pattern_item[0], item)
                    else:
                        log_dict[str(pattern_item[0])] = log_dict[str(pattern_item[0])] + re.findall(pattern_item[0],
                                                                                                     item)
            item = re.sub(pattern_item[0], pattern_item[1], item,re.IGNORECASE)
        # 2.文本替换
        for replace_item in context_pattern:
            item = item.replace(replace_item[0], replace_item[1])

        result.append(item)
    context = split_token.join(result)
    context = sp.context_last1(context)
    return context


fw = open(f"../../../../full_data/medical_case_handled/medical_case_handled" + "_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/medical_case_handled/medical_case_handled" + "_preformat.jsonl", "r",
          encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
    print(log_dict.keys())  # 打印log等内容
    for i in log_dict.keys():
        pprint(log_dict[i])
