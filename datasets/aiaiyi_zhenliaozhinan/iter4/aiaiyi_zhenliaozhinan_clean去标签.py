import json
import os
import re
import random
import wordninja
import jieba
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"
pattern_list_zh = [

    [r'([\.。？\?][  ]*)((\*\*)?(《[^《》]+》)(内容预览))', r'\1\n\n\2'],
    [r'(\*+点击下载[^\n]+)', ''],
    [r'([^\n。？]*[\*\\]*(点击下载|完整版?下载|下载地?址?：|相关专题链接：|点击查看原文：|\*[  ]*下载|爱爱医提供|全文下载|指南全集)[\w\W]*)', ''],  # 下载链接提示
    [r'(\\?\[[\d\s\-,～~，;；—\\]{0,100}\])', ''],  # \[2\]、\[3\]
    [r'([\(（][^\(\)\[\]（）]*(流程图|[Ff]igure|[Ff]ig\.|计算器|见表|表|表格|图|图片|图表|见图) *\d+([\s，,、\-–\d]{0,20})[^\(\)\[\]（）]*[\)）])', ''],  # （见表1）、（表3）
    # [r'([^:：\?？,，;；\./\*。\-—\s\dA-Za-z分])(\d+([\s，,\-–\d]{0,20}) *)([,，;；\.。][^\dA-Za-z]{2})', r'\1删除4:<u>\2</u>\4'],  # 标点前的无关数字
    [r'(\\*[\(\[（][^\(\)\[\]（）]*(\set[\s\xa0]{1,3}al|\d+(\(\d+\))?[:：] *\w+([\-\.]\d+)?|ICD)[^\(\)\[\]（）\n]*[\)\]）]?)', ''],  # 参考删除，只删除带括号的参考文献
    [r'(\*+相关阅读[：:]?\*+[\w\W]*)', ''],  # 相关阅读-指南下载
    [r'([,，;；.。])([\?？]+)', r'\1'],  # 1.句子标点后多余标点？?
    # [r'([\(（<]\**[  ]*(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z]{2,6})([\/\w%\?=\.-]+)?\/?[\)）>]|\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w%\?=\.-]+)?\/?)', r'删除9:<u>\1</u>'],
    # [r'([\(（][^\(\)（）]*([Ee]?mail|@)[^\(\)（）]*[\)）])', r'删除11:<u>\1</u>'],
    [r'([\(\[（] *([A-G]\d?|\d[A-G]) *[\)\]）])', ''],   # 句末出现（C）、（A）、（B）
    [r'([图表]\d+老年[^\(\)\[\]（）\s]*)', ''],
    [r'(\\?[\(（\[]+[^\(\)\[\]（）]*(\d+([\(（]\d+[\)）])?[:：] *\w+([\-,～~，;；–—、\.]\d+)?|出版|杂志|中华医学会编着|主编，)[^\(\)\[\]（）]*[\)）\]])', ''],
    [r'(\\\\\[91|o7-11\\\\\]|-6J|-4\\\\\]|‘3J|L34J|』\}i\{i|¨1|㈣|\\\[6-1t J|\\_l4J|【“|\\_5\\\]|』|『|\\\\\[“〕|通信作者：王兴鹏，二海交通大学附属第一人民医院200080Email：xpwch@public7．stanet．cn|通信作者：陈超|通讯作者：高旭光Email:gxg56@tom.com|    ‘|\\\[2j|x\\\]--JL)', ''],
    [r'([^\n。？]*(链接>>|参加本指南修订的血管外科专家|[^《]2012中国妊娠和产后甲状腺疾病诊治指南|解读美国甲状腺协会（ATA）妊娠及产后甲状腺疾病诊治指南|2011ATA妊娠及产后甲状腺疾病诊治指南|慢性肾脏病贫血指南（全文）|出处：|下列网址免费获得|北京大学肿瘤医院乳腺肿瘤内科|\*+图1:|本文刊载于|点击下图|流程图：)[^\n]*)', ''],
    [r'( +（\d）)(。)', r'\1'],
    [r'([。，] *)(/)', r'\1'],
    [r'([\(（](收稿日期|本文编辑|吴铁吉|刘智胜|卫医发|中国版|吴鸿伟|JACC|来自|详见|via @|Email：|压力导丝|英国血友病|参照|欧洲呼吸学会|图)[^\(\)（）]*[\)）])', ''],
    [r'([\{\}])(\d)', r'-\2'],
    [r'([\{\}])([、。])', r'）\2'],
    [r'([\{\}])([A-Za-z\u4e00-\u9fff])', r'\2'],
    [r'(P)(《)(0.01)', r'\1<\3'],
    [r'(压下降|脉压|尿量|饱和度)(）|〕)', r'\1>'],
    [r'(DOI：[^。]+)', ''],
    [r'AI】', r'AI'],
    [r'【胆源性', r'\[胆源性'],
    [r'([\u4e00-\u9fff）％])([“¨、\\_a-z ”u—\d【]*J)([,\.。，])', r'\1。'],
    [r'([^\n]+(本书目录)[\w\W]+)', ''],
    [r'\*+\s+\*+《2011年英国高血压指南要点介绍》内容预览\*+\s+新近，英国国家卫生与临床优化研究所（ NICE）对2006年高血压诊疗指南进行了要点更新。该指南结合近年内新获取的临床研究证据，对高血压的防止作\s+出了新的建议，', '']


]


pattern_list_en = [
    [r'。', r'\.'], [r'，', r','], [r'；', r';'],
    [r'([\.。？\?][  ]*)((\*\*)?(《[^《》]+》)(内容预览))', r'\1\n\n\2'],  # 增加换行
    [r'([a-z\)）])(\s{3,}([(（]\d+[)）]|(\\?\[[\d\s\-,～~，;；–—\\]{0,100}\]))?)( ?[a-z])', r'\1 \5'],
    [r'([a-z\)）])(\s{3,}([(（]\d+[)）]|(\\?\[[\d\s\-,～~，;；–—\\]{0,100}\]))?)( ?[,，;；.。])', r'\1\5'],
    [r'([a-z\)）])(\-\s{3,}([(（]\d+[)）]|(\\?\[[\d\s\-,～~，;；–—\\]{0,100}\]))?)( ?[a-z])', r'\1\5'],
    # 8.06补充
    [r'(\*+点击下载[^\n]+)', ''],
    [r'([^\n\.。？]*[\*\\]*(点击下载|完整版?下载|下载地?址?：|相关专题链接：|点击查看原文：|\*[  ]*下载)[^\n]*)', ''],  # 下载链接提示
    [r'( *[\(（](\d+([\s,，\-–\d]{0,100}))[\)）])([,，;；\\\.。])', r'\4'],  # 句末序号
    [r'(\\*[\(\[（][^\(\)\[\]（）]*(\set[\s\xa0]{1,3}al|\d+(\(\d+\))?[:：] *\w+([\-\.]\d+)?|ICD)[^\(\)\[\]（）\n]*[\)\]）])', ''],  # （Smith et al, 2006）、（Snowden et al 2011）
    [r'([\(（]([fF]ig|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able|[Ss]ee|[Rr]efer|[Aa]ppendix|NICE|[Bb]ox|Kannel|Bordley|Giorgi2004|American|search) *([^\(\)（）]*[\)）]))', ''],  # ( figure 2 ) ( ( figure 2 ), panels A and C)
    [r'([^\d][,，;；.。] *)(\d+(([\s，,\-–]+\d+){0,20}) *)([A-Zabeih][A-Za-z])', r'\1\5'],  # 句首8-17、8、2，3等
    [r'(\s{4,})(\d+(([\s，,\-–]+\d+){0,20}) *)([A-Zabeih][A-Za-z])', r'\1\5'],
    [r'(\\?\[[\w\s\-,～~，;；–—\\]{0,100}\])', ''],  # 句末\[1, 2\]、\[3–22\]、\[4\]等
    [r'([^。\.\n]+\d{4}[;；]\w+[:：]\w+[^\nA-Z]+)', ''],
    [r'(©|See pages 31–33 for the updated information\.|See Table 1\.|\*\*《2014BSG Barrett食管诊断和治疗指南》\*\*|Telephone: 028 9052 4391)', ''],
    [r'([,\.][^\n\.,。？\?\(\)（）]+([Aa]ppendix|in [Tt]able|on pages?)[^\n\.,。？\?\(\)（）]+?[\.,])', '.'],
    [r'([A-Za-z\d）\)](?<! and) ?)([\(\[（](\d+(([\s，,\-––]+\d+){0,20}))[\)\]）])', r'\1'],
    [r'((Professor Alan|We are grateful to|The development of this framework|Douglas P\.|A\. John Camm|To help you)[\w\W]+?(\n[  ]*\n))', ''],
    [r'de(\?)bril', ''],
    [r'((ó 2011 European|Perth:|Date written:|Final submission:|Author:|Stack A|For more detailed|Footnote:|See the NICE|Entries to MEDLINE|From the National|CREST wishes|Dr Mark Gibson|Experts of the guideline|Copies of the full-text|therecent American|see NEJM|Advice on|A recent document)[^\n]+)', ''],
    [r'((\\\*Refer to|Review by date|\*+Disclaimer|\*+《2013AHA ACC成人超重与肥胖管理指南》内容预览)[\w\W]*)', ''],
    [r'(et al\. )([\(（]\d+[\)）] *)', r'\1'],
    [r'(,)(\s{3,})', r'\.\2'],
    [r'(The 2002 American[^\.]+\.)', ''],
    [r'fashion3through', 'fashion through'],
    [r'rare6,7and', 'rare and'],
    [r'2005.2,3The', '2005. The'],
    [r'statin2,3,9 -13and', 'statin and'],
    [r'preexcitation.3', 'preexcitation.'],
    [r'concentration74-76andthere', 'concentration and there']
]


class speicalProces:
    def __init__(self):
        pass

    def step5_sentence_segment(self, context):
        patter = r'([A-Za-z]{15,})'
        if re.search(patter, context):
            word_list = re.findall(patter, context)
            for wordl in word_list:
                # 使用 wordninja 进行分词
                words = wordninja.split(wordl)
                output_string = " ".join(words)
                words_escape = re.escape(wordl)
                context = re.sub(rf'{words_escape}', output_string, context)
        return context

    def step6_unrelated_text(self, context):
        patter1 = r'([^A-Za-z]([A-Z][a-z]?\.)+ ?[A-Za-z]{,20})'
        patter2 = r'([\(（]\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?[\)）]|\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?)'
        patter3 = r'(MD|Professor)'
        patter4 = r'(Fax|mail|calling)'
        website_list = re.findall(patter2, context)
        for web in website_list:
            if len(re.findall(r'\.', web[0])) >= 2:
                context = re.sub(re.escape(web[0]), '', context)
        if len(re.findall(patter1, context)) > 4 or len(re.findall(patter3, context)) > 4 or (
                len(re.findall(patter3, context)) > 2 and len(context) < 500):
            # context = "(此段删除)无关文本-1：" + context
            context = ""
        if len(website_list) > 2 or len(re.findall(patter4, context)) > 2:
            # context = "(此段删除)无关文本-2：" + context
            context = ""
        return context

    def step7_http(self, context):
        patter2 = r'([\(（]\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?[\)）]|\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?)'
        website_list = re.findall(patter2, context)
        # print(website_list)
        for web in website_list:
            if len(re.findall(r'\.', web[0])) >= 2:
                context = re.sub(re.escape(web[0]), '', context)
        return context


def clean_text(context, lang):
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    if lang == "zh":
        pattern_list = pattern_list_zh
        context = sp.step7_http(context)
    elif lang == 'en':
        pattern_list = pattern_list_en
        context = sp.step5_sentence_segment(context)
    else:
        pattern_list = pattern_list_zh + pattern_list_en
        context = sp.step7_http(context)

    # 1.正则
    for pattern_item in pattern_list:
        src = pattern_item[0]
        tgt = pattern_item[1]
        context = re.sub(src, tgt, context)

    # 分解处理
    result = []
    if lang == "en":
        context = context.split(split_token)
        for item in context:
            item = sp.step6_unrelated_text(item)
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
    # 对多标点进行替换
    context = re.sub(r'([。，：、？；\.,\?;:])(\s*[。，：、？；．\.,\?;:])+', r'\1', context)
    return context


#读jsonl
fw = open(r"C:\Program Files\lk\projects\pdf\aiaiyi_zhenliaozhinan\aiaiyi_zhenliaozhinan_preformat_en_clean4.jsonl", "w", encoding="utf-8")
with open(r"C:\Program Files\lk\projects\pdf\aiaiyi_zhenliaozhinan\aiaiyi_zhenliaozhinan_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        context = item["text"]
        # print(context, '\n-------------------')
        lang = item["lang"]
        exit_flag = False
        wuguan = ["目录：","自然人群中幽门螺杆菌感染特点：","The  American Heart Association","Hisamichi AIZAWA","《2010RNAO慢性疾病支持性自我管理策略》","2013 AHA/ACC/TOS Guideline"]
        for txt in wuguan:
            if txt in context:
                # context = "(本页删除)本页文本质量太差:\n" + context
                exit_flag = True
                break
        if exit_flag:
            continue
        if lang == 'en':
            # context = post_process(context)
            context = clean_text(context, lang)
            context = post_process(context)
            # print(context)
            item["text"] = context
            print(item["text"], "\n--------------------------------------------------")
            item = json.dumps(item, ensure_ascii=False)
            fw.write(item + "\n")
fw.close()



