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
    [r'([^\n\.。）]*[\*\\]*(点击下载|完整版?下载|下载地?址?：|相关专题链接：|点击查看原文：|\*下载)[^\n]+)', r'删除1:<u>\1</u>'],  # 下载链接提示
    [r'(\\?\[[\d\s\-,～~，;；—\\]{0,100}\])', r'删除2:<u>\1</u>'],  # \[2\]、\[3\]
    [r'([\(（](流程图|[Ff]igure|[Ff]ig\.|计算器|见表|表|表格|图|图片|图表|见图) *\d+([\s，,\-–\d]{0,20})[\)）])', r'删除3:<u>\1</u>'],  # （见表1）、（表3）
    # [r'([^:：\?？,，;；\./\*。\-—\s\dA-Za-z分])(\d+([\s，,\-–\d]{0,20}) *)([,，;；\.。][^\dA-Za-z]{2})', r'\1删除4:<u>\2</u>\4'],  # 标点前的无关数字
    [r'(\\*[\(\[（][^\(\)\[\]（）]*(\set[\s\xa0]{1,3}al|\d+[:：] *\w+([\-\.]\d+)?)[^\(\)\[\]（）]*[\)\]）])', r'删除5:<u>\1</u>'],  # 参考删除，只删除带括号的参考文献
    [r'(\*+相关阅读\*+[\w\W]*\*+指南下载\*+[\w\W]*)', r'删除6:<u>\1</u>'],  # 相关阅读-指南下载
    [r'([,，;；.。])([\?？])', r'\1删除7:<u>\2</u>'],  # 1.句子标点后多余标点？?
    [r'(\**[  ]*(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z]{2,6})([\/\w\?= \.-]+)?\/?)', r'删除9:<u>\1</u>'],


    # （这条正则最好放最后一条）
    # [r'((\\\*)+)', r'删除8:<u>\1</u>'],  # 正文中的\*\*
    [r'((\*){2,})', r'删除10:<u>\1</u>'],  # 正文中的**
]

pattern_list_en = [
    ['\\s*●\\(See.*', ''],
    ['\\*\\s*urn:lims:.*?•?\\s*No\\s*', ''],#*   urn:lims:b498:s2691415 No
    [' ?View Patient Education', ''],
    ['\\((picture|figure|table)\\s*.*\\)', ''], #(picture1) (figure 2-1xxx)
    [r'[\s•\\-]{0,5}\((See|see|ESMO|ESC|ASCO)[^\(\)]*(\([^\(\)]*\)[^\(\)]*){0,}\)', ''],#(see table...)    7/25修改
    ['\\(show table.*\\)', ''], #(show table...)
    ['(.*)(for|For) additional information(.*)', ''],
    ['(.*)See individual agents(.*)', ''],
    ['(.*)Reference Range(.*)', ''],
    ['(.*)Consumer Information Use and Disclaimer(.*)', ''],
    ['(.*Last Reviewed Date.*)|(SUMMARY AND RECOMMENDATIONS)|SUMMARY|ACKNOWLEDGMENTS|(SOCIETY GUIDELINE LINKS)', ''],#...Last Reviewed Date...、SUMMARY AND RECOMMENDATIONS、SUMMARY、ACKNOWLEDGMENTS、SOCIETY GUIDELINE LINKS
    ['\\(参见.*\\)', ''],
    ['(.*)见(.*)专题(.*)', ''],
    # ['(.*\\(第\\d+版\\))|(.*专家(共识|建议)(\\(\\d+.*版\\))?)|(.*(临时|防控)指南)(专题)?|(学会指南链接：.*)|(Society guideline links:.*)', ''], #...(第1版)、...专家共识、...指南、学会指南链接：...、Society guideline links:...
    ['(More on this topic)|(Patient education:.*)', ''],
    ['(👍|▶|●|©|®|†|¶|║|§|∧|™|■|❏|□|✓|✔|❍|😃|�|∑|✦|❤️|❤)', ''],
    ['(^\\s*(–|—))|((-|–|—)\\s*$)', ''], #-patient、doctor-
    ['\\((\\[?)\\s*#?((\\d+-\\s*\\d+-\\s*\\d+)|(\\d+-\\s*\\d+)|(\\d+(,|，)\\s*\\d+.*)|(\\d+))(\\]?).*?\\)', ''], #1.(23-1-32...) (12,dadada) ([12.医疗数据])

    [r'\(\s+Ref\s+\)',''],
    [r'\([^\)\(]{1,50}\d{4};[^\)\(]{1,200}\)',''],

    [r'\([^\(\)]{0,100}algorithm\s[^\(\)]{0,100}\)',''],
    [r'\(\s?[A-Z][^\(\)]{0,20}\s\d{4}[^\(\)]{0,50}\)',''],
    [r'^Contributor Disclosures',''],
    [r'^\s?(Please read the Disclaimer at the end of this page|Links to society and government-sponsored guidelines|Beyond the Basics topics).*',''],
    [r'\([^\(\)]{1,50}(waveform|movie|calculator)[^\(\)]{1,50}\)', ''],
    # 8.06补充
    [r'([^\n\.。）]*[\*\\]*(点击下载|完整版?下载|下载地?址?：|相关专题链接：|点击查看原文：|\*下载)[^\n]+)', r'删除1:<u>\1</u>'],  # 下载链接提示
    [r'(\**[  ]*(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?)', r'删除2:<u>\1</u>'],  # 网址
    [r'( *[\(（](\d+([\s,，\-–\d]{0,100}))[\)）])([,，;；.。])', r'删除3:<u>\1</u>\4'],  # 句末序号
    [r'(\\*[\(\[（][^\(\)\[\]（）]*(\set[\s\xa0]{1,3}al|\d+[:：] *\w+([\-\.]\d+)?)[^\(\)\[\]（）]*[\)\]）])', r'删除4:<u>\1</u>'],  # （Smith et al, 2006）、（Snowden et al 2011）
    [r'(([\(（][^\(\)（）]{0,50})([fF]igure|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able) *([^\(\)（）]{0,50}[\)）]))', r'删除5:<u>\1</u>'],  # ( figure 2 ) ( ( figure 2 ), panels A and C)
    [r'([^\d][,，;；.。] *)(\d+(([\s，,\-–]\d+){0,20}) *)([A-Z])', r'\1删除6:<u>\2</u>\5'],  # 句首8-17、8、2，3等
    [r'(\\?\[[\d\s\-,～~，;；—\\]{0,100}\])', r'删除7:<u>\1</u>'],  # 句末\[1, 2\]、\[3–22\]、\[4\]等

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

def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    if lang == "zh":
        pattern_list = pattern_list_zh
    elif lang == 'en':
        pattern_list = pattern_list_en
    else:
        pattern_list = pattern_list_en+pattern_list_zh

    # 分解处理
    result = []
    sp = speicalProces()

    # special_process：
    # context = sp.step1_drop_sentenc(context)
    context = context.split(split_token)

    # 7/24uptodata_new修改
    # context = sp.step3_reference(context)

    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            # print(pattern_item)
            # print(re.findall(src, item))
            item = re.sub(src, tgt, item)
        if lang == "en":
            item = sp.step5_sentence_segment(item)
        # if "url:" not in item and sp.step2_endding_filter(item):
        #     # print(item)
        #     continue

        result.append(item)
    # for item in result:
    #     print(item)
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
    context = re.sub(r'[。，\.](\s?[。，\.：]){1,5}',r'。',context)
    context = re.sub(r'[,\.](\s+[,\.]){1,5}',r'.',context)
    return context


#读jsonl
fw = open(r"C:\Program Files\lk\projects\pdf\aiaiyi_zhenliaozhinan\aiaiyi_zhenliaozhinan_preformat_en_clean1B.jsonl", "w", encoding="utf-8")
with open(r"C:\Program Files\lk\projects\pdf\aiaiyi_zhenliaozhinan\aiaiyi_zhenliaozhinan_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "aecebefc-b489-471e-82ee-a9b12fb2ee91":
        context = item["text"]
        # print(context, '\n-------------------')
        lang = item["lang"]
        if lang == 'en':
            context = clean_text(context, lang)
            context = post_process(context)
            # print(context)
            item["text"] = context
            print(item["text"])
            item = json.dumps(item, ensure_ascii=False)
            fw.write(item + "\n")

fw.close()



