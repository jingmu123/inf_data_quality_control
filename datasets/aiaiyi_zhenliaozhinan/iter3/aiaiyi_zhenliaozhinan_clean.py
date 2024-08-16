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

    [r'([\.。？\?][  ]*)((\*\*)?(《[^《》]+》)(内容预览))', r'\1\n增加换行:\2'],
    [r'(\*+点击下载[^\n]+)', r''],
    [r'([^\n。？]*[\*\\]*(点击下载|完整版?下载|下载地?址?：|相关专题链接：|点击查看原文：|\*[  ]*下载|爱爱医提供|全文下载|指南全集)[^\n]*)', r'删除1:<u>\1</u>'],  # 下载链接提示
    [r'(\\?\[[\d\s\-,～~，;；—\\]{0,100}\])', r'删除2:<u>\1</u>'],  # \[2\]、\[3\]
    [r'([\(（][^\(\)\[\]（）]*(流程图|[Ff]igure|[Ff]ig\.|计算器|见表|表|表格|图|图片|图表|见图) *\d+([\s，,、\-–\d]{0,20})[^\(\)\[\]（）]*[\)）])', r'删除3:<u>\1</u>'],  # （见表1）、（表3）
    # [r'([^:：\?？,，;；\./\*。\-—\s\dA-Za-z分])(\d+([\s，,\-–\d]{0,20}) *)([,，;；\.。][^\dA-Za-z]{2})', r'\1删除4:<u>\2</u>\4'],  # 标点前的无关数字
    [r'(\\*[\(\[（][^\(\)\[\]（）]*(\set[\s\xa0]{1,3}al|\d+(\(\d+\))?[:：] *\w+([\-\.]\d+)?|ICD)[^\(\)\[\]（）\n]*[\)\]）]?)', r'删除5:<u>\1</u>'],  # 参考删除，只删除带括号的参考文献
    [r'(\*+相关阅读[：:]?\*+[\w\W]*)', r'删除6:<u>\1</u>'],  # 相关阅读-指南下载
    [r'([,，;；.。])([\?？])', r'\1删除7:<u>\2</u>'],  # 1.句子标点后多余标点？?
    [r'([\(（<]\**[  ]*(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z]{2,6})([\/\w%\?=\.-]+)?\/?[\)）>]|\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w%\?=\.-]+)?\/?)', r'删除9:<u>\1</u>'],
    [r'([\(（][^\(\)（）]*([Ee]?mail|@)[^\(\)（）]*[\)）])', r'删除11:<u>\1</u>'],
    [r'([\(\[（] *([A-G]\d?|\d[A-G]) *[\)\]）])', r'删除12:<u>\1</u>'],   # 句末出现（C）、（A）、（B）
    [r'([图表]\d+老年[^\(\)\[\]（）\s]*)', r'删除13:<u>\1</u>'],
    [r'(\\?[\(（\[]+[^\(\)\[\]（）]*(\d+([\(（]\d+[\)）])?[:：] *\w+([\-,～~，;；–—、\.]\d+)?|出版|杂志)[^\(\)\[\]（）]*[\)）\]])', r'删除14:<u>\1</u>'],
    [r'(\\\\\[91|o7-11\\\\\]|-6J|-4\\\\\]|‘3J|L34J|』\}i\{i|¨1|㈣|\\\[6-1t J|\\_l4J|【“|\\_5\\\])', r'删除15:<u>\1</u>'],
    [r'([^\n。？]*(链接>>|参加本指南修订的血管外科专家|[^《]2012中国妊娠和产后甲状腺疾病诊治指南|解读美国甲状腺协会（ATA）妊娠及产后甲状腺疾病诊治指南|2011ATA妊娠及产后甲状腺疾病诊治指南|慢性肾脏病贫血指南（全文）|出处：|下列网址免费获得|北京大学肿瘤医院乳腺肿瘤内科)[^\n]*)', r'删除16:<u>\1</u>'],
    [r'( +（\d）)(。)', r'\1删除17:<u>\2</u>'],
    [r'([。，] *)(/)', r'\1'],
    [r'([\(（](收稿日期|本文编辑|吴铁吉|刘智胜|卫医发|中国版|吴鸿伟|JACC|来自|详见)[^\(\)（）]*[\)）])', r'删除18:<u>\1</u>'],



    # （这条正则最好放最后一条）
    # [r'((\\\*)+)', r'删除8:<u>\1</u>'],  # 正文中的\*\*
    # [r'((\*){2,})', r''],  # 正文中的**
]

# reclean2_aiaiyi_zhenliaozhinan_zh.jsonl
'''
采样量: 300
干净文本:212 脏文本:88
[300, {'多余换行': 8, '语义不完整': 6, '无关文本': 109, '多余标点': 12, '缺少换行': 3, '特殊符号': 2, '标点错误': 4, '错别字': 2, '页码/数字': 4, '错误删除': 3, '语句/字词重复': 1, '缺少标点': 1}] ,
各纬度问题频次F={'多余换行': 8, '语义不完整': 6, '无关文本': 109, '多余标点': 12, '缺少换行': 3, '特殊符号': 2, '标点错误': 4, '错别字': 2, '页码/数字': 4, '错误删除': 3, '语句/字词重复': 1, '缺少标点': 1}
合格率=70.667%
质量分=81.34668
推荐解决的单个问题顺序以及收益（供参考）：{'无关文本': 96.24682, '语义不完整': 82.33939, '多余换行': 82.2155, '错误删除': 81.87195, '多余标点': 81.77308, '页码/数字': 81.51773, '标点错误': 81.49921, '缺少换行': 81.46483, '特殊符号': 81.43654, '错别字': 81.41478, '缺少标点': 81.37745, '语句/字词重复': 81.34668}
推荐解决的组合问题顺序以及收益（供参考）：{'无关文本#语义不完整': 97.37785, '无关文本#多余换行': 97.11565, '语义不完整#多余换行': 83.20822}
'''


pattern_list_en = [

    # ['(\\((\\[?)\\s*#?((\\d+-\\s*\\d+-\\s*\\d+)|(\\d+-\\s*\\d+)|(\\d+(,|，)\\s*\\d+.*)|(\\d+))(\\]?).*?\\))', r'删除84:<u>\1</u>'], #1.(23-1-32...) (12,dadada) ([12.医疗数据])
    # [r'(\([^\)\(]{1,50}\d{4};[^\)\(]{1,200}\))', r'删除85:<u>\1</u>'],
    # [r'(\(\s?[A-Z][^\(\)]{0,20}\s\d{4}[^\(\)]{0,50}\))', r'删除86:<u>\1</u>'],
    [r'([\.。？\?][  ]*)((\*\*)?(《[^《》]+》)(内容预览))', r'\1\n增加换行:\2'],  # 增加换行
    # 8.06补充
    [r'(\*+点击下载[^\n]+)', r''],
    [r'([^\n\.。？]*[\*\\]*(点击下载|完整版?下载|下载地?址?：|相关专题链接：|点击查看原文：|\*[  ]*下载)[^\n]+)', r'删除1:<u>\1</u>'],  # 下载链接提示
    # [r'([\(（]?\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?[\)）]?)', r'删除2:<u>\1</u>'],  # 网址
    [r'( *[\(（](\d+([\s,，\-–\d]{0,100}))[\)）])([,，;；.。])', r'删除3:<u>\1</u>\4'],  # 句末序号
    [r'(\\*[\(\[（][^\(\)\[\]（）]*(\set[\s\xa0]{1,3}al|\d+(\(\d+\))?[:：] *\w+([\-\.]\d+)?|ICD)[^\(\)\[\]（）\n]*[\)\]）]?)', r'删除4:<u>\1</u>'],  # （Smith et al, 2006）、（Snowden et al 2011）
    [r'([\(（]([fF]ig|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able|[Ss]ee|[Rr]efer|Appendix|Dr|NICE) *([^\(\)（）]*[\)）]))', r'删除5:<u>\1</u>'],  # ( figure 2 ) ( ( figure 2 ), panels A and C)
    [r'([^\d][,，;；.。] *)(\d+(([\s，,\-–]+\d+){0,20}) *)([A-Z])', r'\1删除6:<u>\2</u>\5'],  # 句首8-17、8、2，3等
    [r'(\\?\[[\d\s\-,～~，;；–—\\]{0,100}\])', r'删除7:<u>\1</u>'],  # 句末\[1, 2\]、\[3–22\]、\[4\]等
    [r'([^。\.\n]+\d{4}[;；]\w+[:：]\w+[^\nA-Z]+)', r'删除8:<u>\1</u>'],
    [r'(See pages 31–33 for the updated information\.|See Table 1\.|\*\*《2014BSG Barrett食管诊断和治疗指南》\*\*|as summarized in Table1\.)', r'删除11:<u>\1</u>'],
    [r'((Professor Alan B\.R\.)[\w\W]*?(\n\n))', r'删除10:<u>\1</u>'],
    [r'([^\n\.。？\?\(\)（）]+Appendix[^\n\.。？\?\(\)（）]+?\.)', r'删除12:<u>\1</u>'],


]


class speicalProces:
    def __init__(self):
        pass
    def step1_drop_sentenc(self,content):
        pattern3=r'。?.*见.*详.*?[。，]'
        pattern1=r'。?.*题专.*见.*?[。，]'
        pattern2=r'。.*表附见.*?[。，]'
        pattern4=r'。(图程流)?文(下|上)见.*?[。，]'
        text=content.strip('\n').split("\n")
        for i in range(len(text)):
            text[i] = re.sub(pattern3, '。', text[i][::-1])[::-1]
            text[i]=re.sub(pattern1,'。',text[i][::-1])[::-1]
            text[i] = re.sub(pattern2, '。', text[i][::-1])[::-1]
            text[i] = re.sub(pattern4, '。', text[i][::-1])[::-1]
        text='\n'.join(text)
        return text

    def step2_endding_filter(self,content):
        if "打印" in content or "邮件" in content or "致谢" in content or "感谢" in content or "参见" in content or "下文" in content or "上文" in content or "流程图" in content or "网站" in content:
            return True
        if "uptodate" in content.lower():
            return True
        if re.search(r'专题[^。]*版本',content):
            return True
        if len(re.findall(url_pattern, content)) >= 1:
            return True
        return False

    def step3_reference(self, context):
        new_context = []
        references_started = False   #定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        introduce = 0
        introduce_index = []
        Inc = 0
        Inc_index = []

        guidelines = 0
        guidelines_index = []
        for index, item in enumerate(context):
            if re.search(r'^(References|参考文献|见参考文献|致谢|REFERENCES|ACKNOWLEDGMENT|The following organizations also provide reliable health information|More on this topic|Topic[^\.]*Version|For country code abbreviations|ACKNOWLEGMENT)', item.strip()):
                references_started = True
            if references_started:
                item = ""

            if re.search(r'^2024© UpToDate, Inc', item.strip()):
                Inc += 1
                Inc_index.append(index)
            if re.search(r'ALERT: ', item.strip()):
                Inc -= 1
                Inc_index.append(index)

            # 要删除从Author到引言 设定了两个条件在循环时同时出现Author和引言，记下index，对相应的index进行删除
            if re.search(r'^(Author)', item.strip()):
                introduce += 1
                introduce_index.append(index)
            if re.search(r'^(引言|简介)', item.strip()) or re.search(r'^INTRODUCTION', item.strip()) or re.search(r'^Please read the Disclaimer at the end of this page',item.strip()):
                introduce -= 1
                introduce_index.append(index)

            if re.search(r'^(SOCIETY GUIDELINE LINKS)',item.strip()):
                guidelines += 1
                guidelines_index.append(index)
            if re.search(r'^INFORMATION FOR PATIENT',item.strip()) and guidelines == 0:
                guidelines += 1
                guidelines_index.append(index)
            if re.search(r'^.{,5}(Basics topics|Beyond the Basics topics)', item.strip()):
                guidelines -= 1
                guidelines_index.append(index)

            new_context.append(item)

        if introduce <= 0 and len(introduce_index) >= 2:
            start_index = introduce_index[0]
            end_index = introduce_index[-1]
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index + 1):
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                new_context[i] = ''


        if Inc <= 0 and len(Inc_index) >= 2:
            start_index = Inc_index[0]
            end_index = Inc_index[-1]
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index + 1):
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                new_context[i] = ''



        if guidelines <= 0 and len(guidelines_index) >= 2:
            start_index = guidelines_index[0]
            end_index = guidelines_index[-1]
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index + 1):
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                new_context[i] = ''

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
        split_token = "\n"
        result = []
        context = context.split(split_token)
        patter1 = r'([^A-Za-z]([A-Z][a-z]?\.)+ ?[A-Za-z]{,20})'
        patter2 = r'([\(（]\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?[\)）]|\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?)'
        patter3 = r'(MD|Professor)'
        patter4 = r'(Fax|mail|calling)'
        for item in context:
            if len(re.findall(patter1, item)) > 4 or len(re.findall(patter3, item)) > 4 or (len(re.findall(patter3, item)) > 2 and len(item) < 500):
                item = "(此段删除)无关文本-1：" + item
            website_list = re.findall(patter2, item)
            # print(website_list)
            if len(website_list) > 2 or len(re.findall(patter4, item)) > 2:
                item = "(此段删除)无关文本-2：" + item
            for web in website_list:
                if len(re.findall(r'\.', web[0])) >= 2:
                    item = re.sub(re.escape(web[0]), rf'删除2:<u>{web[0]}</u>',item)
            result.append(item)
        context = split_token.join(result)
        return context

def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    if lang == "zh":
        pattern_list = pattern_list_zh
    elif lang == 'en':
        pattern_list = pattern_list_en
    else:
        pattern_list = pattern_list_zh + pattern_list_en

    # 分解处理
    result = []
    sp = speicalProces()
    # 1.正则
    for pattern_item in pattern_list:
        src = pattern_item[0]
        tgt = pattern_item[1]
        # print(pattern_item)
        # print(re.findall(src, item))
        context = re.sub(src, tgt, context)

    # special_process
    # context = sp.step1_drop_sentenc(context)

    context = context.split(split_token)

    for item in context:

        if lang == "en":
            item = sp.step5_sentence_segment(item)
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
    context = re.sub(r'([。，：、？；：\.,\?;:])(\s*[。，：、？；：．\.,\?;:])+', r'\1', context)
    return context


#读jsonl
fw = open(r"C:\Program Files\lk\projects\pdf\aiaiyi_zhenliaozhinan\aiaiyi_zhenliaozhinan_preformat_zh_clean3.jsonl", "w", encoding="utf-8")
with open(r"C:\Program Files\lk\projects\pdf\aiaiyi_zhenliaozhinan\aiaiyi_zhenliaozhinan_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    count = 0
    for items in tqdm(lines):
        item = json.loads(items.strip())
        context = item["text"]
        # print(context, '\n-------------------')
        lang = item["lang"]
        if "目录：" in context:
            context = "(本页删除)本页发现目录的特征:\n" + context
            # continue

        # ll = ['zh', 'en']
        # if lang not in ll:
        #     count += 1
        #     print(lang)
        #     print(context, '\n-------------------')

        if lang == 'zh':
            # context = post_process(context)
            context = clean_text(context, lang)
            context = post_process(context)
            # print(context)
            item["text"] = context
            print(item["text"], "\n--------------------------------------------------")
            item = json.dumps(item, ensure_ascii=False)
            fw.write(item + "\n")

fw.close()



