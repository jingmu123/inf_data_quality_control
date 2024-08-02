import json
import os
import re
import random

import jieba
from langdetect import detect
from langdetect import detect_langs
from tqdm import tqdm

url_pattern = r"(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?"
pattern_list_zh = [
        [r'文中有.*具体指导。', ''],
        ['\\((基础篇|高级篇|Beyond the Basics|见下文|附视频)\\)', ''],  #（基础篇）、（高级篇）、（Beyond the Basics）、（见下文）、（附视频）
        [r'\(参见[^\(\)]*(\([^\(\)]*\)[^\(\)]*){0,5}\)', ''], #（参见...）  （参见（...）{0,5}）7/24uptodata_new修改
        ['(((基础|高级)篇)?(\\(参见.*\\))?)|(患者教育\\s*[：:—-].*(\\(基础篇\\))?)|(Patient education:.*)', ''], # 1、基础篇参见...2、...患者教育：...3、...患者教育-...4、...患者教育—...5、Patient education:...
        ['\\((流程图|figure|NCT|Grade|视频|计算器|波形|表|表格|图|图片|图表)\\s*\\d+.*?\\)', ''],  #（流程图 1）、（figure 1）等
        ['\\d{3}-\\d{3}-\\d{4}', ''], #232-432-4122
        ['(<sup>)?(\\\\)?(\\[|［)(\\d+|(\\d+[,.、~～-]\\s*\\d+.*))(\\\\)?(\\]|］)(</sup>)?', ''],   #[1,2] [1.2] [1、2] [1-2] \[1.2\] <sup>\[1.2\]</sup>
        # ['\\(参见\\s*[^（]+(\\([^)]*\\))?[^)]*\\)', ''],#（参见（...））
        ['参见网页\\(here\\)', ''],
        ['关于.*参见.*(\\n.*[：:].*)*', ''],
        # ['\\((\\[?)\\s*#?((\\d+-\\s*\\d+-\\s*\\d+)|(\\d+-\\s*\\d+)|(\\d+(,|，)\\s*\\d+.*)|(\\d+))(\\]?).*?\\)', ''], #1.(23-1-32...) (12,dadada) ([12.医疗数据])
        ['(.*)学会指南链接(.*)', ''],
        # ['[^。](见?)([^。]*)专题(.*)', ''],
        ['更多|总结与推荐|(\\(影像.*?\\))|在线资源和支持组织|信息参见网站|如图所示：', ''], #更多、总结与推荐、总结、在线资源和支持组织、（影像...）、信息参见网站
        ['●|•|❤️', ''],
        ['(^\\s*(–|—))|((-|–|—)\\s*$)', ''], #-医疗、医院-
        [r'[^。]*(详[^。]*见|见?[^。]*专题|见?附表|见(下|上)文(流程图)?|附图)[^。]*。',r''],  # 7/30
        ['[^。](参见附图|详见).*', ''],
        ['.*见?参考文献.*', ''],
        ['.*the website.*', ''],
        ['致谢.*', ''],
        ['(，|。)。','。'],
        # 7/24uptodata_new修改
        [r'\\\[[\d\s\-,—\\]{0,100}\]',''],
        [r'\([^\(\)]{1,50}(流程图|figure|NCT|Grade|视频|计算器|波形|表|表格|图|图片|图表|影像)[^\(\)]{1,50}\)',''],
        # 7/25
        [r'^由 UpToDate 的医生.*',r''],
        [r'^There is a newer version of this topic available in English.*',r''],
        [r'^该专题有一个更新版本.*',r''],
        [r'^请阅读本页末的.*',r''],


]

pattern_list_en = [
                    ['\\s*●\\(See.*', ''],
                    ['\\[\\d+([,，、-]\\d+)*\\]', ''], #[1,2] [1.2] [1、2] [1-2]
                    ['\\*\\s*urn:lims:.*?•?\\s*No\\s*', ''],#*   urn:lims:b498:s2691415 No
                    ['Yes', ''],
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
                    ['(.*\\(第\\d+版\\))|(.*专家(共识|建议)(\\(\\d+.*版\\))?)|(.*(临时|防控)指南)(专题)?|(学会指南链接：.*)|(Society guideline links:.*)', ''], #...(第1版)、...专家共识、...指南、学会指南链接：...、Society guideline links:...
                    ['(More on this topic)|(Patient education:.*)', ''],
                    ['(👍|▶|●|©|®|†|¶|║|§|∧|™|■|❏|□|✓|✔|❍|😃|�|∑|✦|❤️|❤)', ''],
                    ['(^\\s*(–|—))|((-|–|—)\\s*$)', ''], #-patient、doctor-
                    ['\\((\\[?)\\s*#?((\\d+-\\s*\\d+-\\s*\\d+)|(\\d+-\\s*\\d+)|(\\d+(,|，)\\s*\\d+.*)|(\\d+))(\\]?).*?\\)', ''], #1.(23-1-32...) (12,dadada) ([12.医疗数据])

                    [r'\\\[[\d\s\-,—\\]{0,100}\]',''],

                    [r'(\([^\(\)]{1,50}){1,}([fF]igure|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able)\s([^\(\)]{1,50}\)){1,}',''],  #   ( figure 2 ) ( ( figure 2 ), panels A and C)
                    [r'\(\s+Ref\s+\)',''],
                    [r'\([^\)\(]{1,50}\d{4};[^\)\(]{1,200}\)',''],

                    [r'\([^\(\)]{0,100}algorithm\s[^\(\)]{0,100}\)',''],
                    [r'\(\s?[A-Z][^\(\)]{0,20}\s\d{4}[^\(\)]{0,50}\)',''],
                    [r'^Contributor Disclosures',''],
                    [r'^\s?(Please read the Disclaimer at the end of this page|Links to society and government-sponsored guidelines|Beyond the Basics topics).*',''],
                    [r'\([^\(\)]{1,50}(waveform|movie|calculator)[^\(\)]{1,50}\)','']
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
        # if len(re.findall(url_pattern, content)) >= 1:
        #     return True
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

def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"


    if lang == "zh":
        pattern_list= pattern_list_zh
    elif lang=='en':
        pattern_list= pattern_list_en
    else:
        pattern_list = pattern_list_en+pattern_list_zh

    # 分解处理
    result = []
    sp = speicalProces()

    # special_process：
    # context = sp.step1_drop_sentenc(context)
    context = context.split(split_token)

    # 7/24uptodata_new修改
    context = sp.step3_reference(context)

    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            # print(pattern_item)
            # print(re.findall(src, item))
            item = re.sub(src, tgt, item)
        if lang == "zh":
            item = sp.step4_rm_kongge(item)
        if "url:" not in item and sp.step2_endding_filter(item):
            # print(item)
            continue

        result.append(item)
    for item in result:
        print(item)
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
fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean3_uptodate_new_preformat_zh.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\uptodate_new_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()

    # 随机抽取5000条记录
    sampled_lines = random.sample(lines, 1000)
    for items in tqdm(sampled_lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "aecebefc-b489-471e-82ee-a9b12fb2ee91":
        context = item["text"]
        lang = item["lang"]
        if lang == "zh":
            if re.search("Links to related guidelines are provided separately", context):
                continue
            context = clean_text(context, lang)
            context = post_process(context)
            # print(context)
            item["text"] = context
            item = json.dumps(item, ensure_ascii=False)
            print(item)
            fw.write(item + "\n")






