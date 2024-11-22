
import json
from tqdm import tqdm
import re
import random
import spacy

nlp = spacy.load("en_core_web_sm")
pattern_en = [
    [r'(■|©|●|◆)', r''],
    # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
    [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:]?[^\(\)]*\))', r''],  # 1. 这些固定的词语紧贴左括号
    [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))', r'\1)'],  # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+)s?[\s\.:][^\(\)]*\))', r'通用删除1(英):<u>\1</u>'],  # 最广泛的形式从左括号匹配到右括号
    # [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r'通用删除2(英):<u>\1</u>'],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
    [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)', r'通用删除3(英):<u>\1</u>'],  # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?\s{0,}\d+[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除4(英):<u>\1</u>'],  # 特殊数字  排除可能出现的次幂情况
    [r'(.*(doi|DOI)\s?:.*)', r'通用删除5(英):<u>\1</u>'],  # 存在有DOI描述的句子
    [r'((\\?\[[\d\s,，\–\-—]{1,}\\?\]?)|(\\?\[?[\d\s,，\–\-—]{1,}\\?\]))', r'通用删除6(英):<u>\1</u>'],  # 带有方括号的数字引用
    [r'((\\?\( ?\d+([\s,，\-\–—]+\d+)+\\?\))|(\\?\((\d{1,3}|\d{5,})\\?\)))', r'通用删除7(英):<u>\1</u>'],  # 带有圆括号的数字引用
    [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(\\)?\])', r'通用删除8(英):<u>\1</u>'],  # 固定格式  带有[]的图片表格描述 附录描述 协议描述 无关网址描述
    [r'(^Full size.*)', r'通用删除9(英):<u>\1</u>'],  # Full size image/table 原文这里应该是一个图/表没识别出图形
    [r'(\([^\(\)]*(arrow|←|→)[^\(\)]\))', r''],  # ...箭头 描述图里面不同颜色的箭头

    # 9.4继续添加
    [r'(^Full size.*)', r'通用删除10(英):<u>\1</u>'],  # Full size image/table 原文这里应该是一个图/表没识别出图形
    [r'(\([pP]\.?\d+[^\(\)]*\))', r'通用删除11(英):<u>\1</u>'],  # 带有括号的([Pp]. ...)第几页
    [r'(\([^\(\)]*Additional file[^\(\)]*\))', r''],  # 附加文件带括号
    [r'([\*#]{0,4}Additional file.*)', r'通用删除12(英):<u>\1</u>'],  # 附加文件
    [r'(^Download\s.*)', r'通用删除13(英):<u>\1</u>'],  # 段落开头下载 ...
    [r'^.{0,3}(Editor.s note|To learn more about).*', r'通用删除14(英):<u>\1</u>'],  # 从段落头开始 编辑信息 更多信息
    [r'(^(You can find more|About this video).*)', r'通用删除15(英):<u>\1</u>'],  # 段落开头 你可以找到更多/关于本视频

    #09.23继续添加
    [r'(^[#\*_·]*\s?\d?([Ff]i[qg]s?(ure)?|F\s?IGS?(URE)?).*\n?.*)', r'通用删除16(英):<u>\1</u>'],  # 删除开头为Figure的描述

    # 以上为通用正则库
    # ========================================================================================
    # 以下补充对此组数据清洗的特定正则
    [r'([\(（][^（）\(\)]+[，；,; ]+\d{4}[A-Za-z]?[）\)])', r''],  # 括号内带et al\.的参考
    [r'([\(\{（][^\{\}（）\(\)]*([Ff]i ?g ?\.?(ure)? |[Ss]ee |[Pp]age |[Ee]xhibit |[Pp]icture |[Cc]hapter |[Bb]ox |[Tt]able |[，；,;]+ ?\d{4}[，；,; ]+|[ ，；,;]pp?\. ?\d+)[^（）\{\}\(\)]*[）\}\)])', r''],  # 括号内图、表、页、年份等
    [r'(^[\*_]*(\w{1,2}( \w{1,2})+|(\w[，\.]?\w{0,1})|[\d_ ]+)[\*_]*$)', r'删除3:<u>\1</u>'],  # 无关零碎段，B、a bC、_a_ bC、C21等
    # [r'(^[\*\.]*[\d _]*(?:(\d+\\?\.)|([A-Z][A-Z\-\'a-z]+[，,]? [A-Z ]{1,4}[\.，,：\(])).*(\d+(?:\(\d+\))?[：:； ]+[a-zA-Z]?\d+|[a-zA-Z]?\d+\-[a-zA-Z]?\d+[，\.]|et al\.|https?：\/\/|[， ]+p ?\d+|ed \d+，|[\.，][A-Za-z_ ]+\d{4}[，;；\._]+).*)', r'删除4:<u>\1</u>'],  # 参考文献
    [r'(^[\\\*_ #]*(\d+|[A-Z]{1,2}|.{0,2}SUGGESTED READING|Suggested Reading|ACKNOWLEDGMENTS?|I. INTRODUCTION|Acknowledge?ments?|[Rr][Ee][Fft][Ee][Rr][Ee][Nn][Cc] ?[Ee][Ss]?[\.:：]?|(Selected )?References?|FURTHER ?READING|Further reading( list)?|5\'\-\-CACGTAAGCTATGCAGGCTT\-\-3\'|Useful websites)[\*_]*$)',  r'删除5:<u>\1</u>'],  # 参考文献标题及穿插的标题
    [r'(^(?=[\w\W]{0,150}$)[A-Z][a-z]+ [A-Z\.]{1,6}，.*\n?.*)', r'删除6:<u>\1</u>'],  # 删除4参考遗留的段落
    [r'(^[\*_]*(del\(13q\).{0,10}|This page intentionally left blank|( ?\([a-z]\) ?_?)+|[a-z_\d]{1,3} [a-zA-Z])[\*_]*$)', r'删除7:<u>\1</u>'],  # 一些零碎的无关段落
    [r'(^[\*_]*(www\.|E?mail:|[Hh]ttp|Copyright|All rights).*)', r'删除8:<u>\1</u>'],  # 网址、邮箱、Copyright
    # [r'(^(?=.{50,350}$)(.*(?:\([a-zA-Z]\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*(?:\([a-zA-Z]\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*))', r'删除9:<u>\1</u>'],  # 图注换行部分
    [r'(^(?=.{0,200}$)(?:\d+\.|\(\d+\)) ?.*[,，] ?[A-Za-z]{2,}[,，] ?[A-Za-z]{2,}$)', r'删除10:<u>\1</u>'],  # 人物介绍，地名结尾
    [r'(^(The authors? (would like to )?thanks?).*)', r'删除11:<u>\1</u>'],  # 致谢段落
    [r'(^[\*_]*(Also[,，]? [Ss]ee [Cc]hapter|For more details?[,，]|Acknowledgements are|We (also )?thank|This work was|ISBN|\.com\/books|APPEND[I!]X|Appendix).*)', r'删除12:<u>\1</u>'],  # 一些特殊无关段
    [r'(^[\\\*_]*((Data )?[Ff]rom：|Source：|Citation：).*)', r'删除13:<u>\1</u>'],  # 文献来源
    [r'([a-z]\.)( ?[\|\d]+([，, \.\-\|]+\d*)*$)', r'\1删除14:<u>\2</u>'],  # 段末无关数字
    [r'((^(?=.{0,200}$).*(Department|University|New York|[,， ]UK[\.,， ]|[,， ]USA[\.,， ]|， ?(MD|P[Hh]D)|(MD|P[Hh]D)，).*)|(^(?=.{0,400}$).*(Depa[ri]tment of|Tel：|@[a-z]{2,10}\.com|https?).*)|(^(?=.{0,600}$).*[Ff]rom.*(https?).*))', r'删除15:<u>\1</u>'],  # 部门介绍，网址，学校
    [r'(.*\n)(\1)+', r'\1']  # 重复段
    ]


start_end_list = [
    ['521bd141-460d-4a13-bcb5-4fb284c500d3', r'\*\*Brain\*\*', r''],
    ['81218a18-d085-461c-b9bc-a0ba15cc4066', r'\*\*Brain\*\*', r''],
    ['077a0fd7-6bdd-46fe-b116-57a52e21981e', r'\*\*Serum Creatine Kinase\*\*', r'\*\*SUGGESTED READING\*\*'],
    ['93b12cb1-27b1-4c4a-a358-822b1942f3ef', r'# Movement Disorders', r'# titlepage\.xhtml'],
    ['208cbc52-25d1-4a68-9232-70fc85eda0af', r'\*\*Introduction to Screening for Referral in Physical Therapy\*\*', r'Acquired immunodeficiency syndrome \(Continued\)'],
    ['229e9a17-abde-46dc-8c1e-5556476f586e', r'\*\*CASE HISTORY\*\*', r'\*\*Outcome\*\*'],
    ['457f8d5a-efdf-418d-ba91-20746f81991c', r'\*\*Abstract\*\*', r'\*\*References\*\*'],
    ['0741ae0e-ffaf-48ab-97d7-cfb224918bd1', r'# 1 Introduction to Pelvic Pain', r'# Index'],
    ['834aa23a-73b2-46ee-836c-41bdadefbc0e', r'The ideal therapeutic goals for managing patients with primary or metastatic', r'\*\*REFERENCES\*\*'],
    ['155053b0-42d0-49c0-af8b-367a28f2c7f3', r'\*\*ChapterLearning How to _1_ Diagnose\*\*', r'\*\*Index to Conditions\*\*'],
    ['228273ee-6b59-44ae-a894-4057519bf1d1', r'\*\*Methods in Cellular and Molecular Pathology\*\*', r'\*\*REFERENCES\*\*'],
    ['769957bc-60ea-4021-a12e-b985711e02d1', r'\*\*Clinical Pathological Correlation 1\*\*', r'\*\*Suggested Reading\*\*'],
    ['a1ed637b-c0ee-443b-a005-044c77adcab3', r'\*\*Common Presentations of Acute Cardiac Conditions\*\*', r'\*\*_Disposition_\*\*'],
    ['abee9c88-5f5b-4707-a3d6-6879f9260bd0', r'\*\*Psoriasis _Nummular Dermatitis_\*\*', r''],
    ['affc2b3a-715f-4a44-8818-ead0e0fd577d', r'\*\*ABDOMINAL PAIN\*\*', r'\*\*toneal cavity\*\*'],
    ['b2ab9a9f-1728-4436-8151-58cf3b3e9836', r'\*\*_Guttate Psoriasis_ _Seborrheic Dermatitis_\*\*', r''],
    ['b3fe557f-2a0a-4323-9fa5-8d80007e07d5', r'\*\*The patient with difficulty or pain during swallowing\*\*', r'\*\*SectionII Gastroenterology illustrated\*\*'],
    ['b9085cdc-a2ba-4fbd-945b-3eb321e99b56', r'\*\*Introduction\*\*', r'\*\*Abdominal aneurysm， 166\*\*'],
    ['b9702bee-c259-4212-afca-dd691cc01bb9', r'\*\*Chapter 1Tremor\*\*', r'Bibliography'],
    ['0b35511a-f54a-496a-9f8b-17e6c300e359', r'The nail is one of the smallest of structures', r'\*\*REFERENCES\*\*'],
    ['1b8f6c97-84d2-4668-b8c4-9c2b1556cf45', r'\*\*Abdominal Pain in Adults\*\*', r'\*\*Selected References\*\*'],
    ['2c2b8e20-a3b5-4130-92fc-353d5ee8726c', r'Contents', r'\*\*Acanthoma large\-cell\*\*'],
    ['2c0434a8-3533-4226-a647-0c6da73f4940', r'CASE 1', r'SUGGESTED READING'],
    ['3adc0f37-9da7-48e0-993d-a485879cdabd', r'RURITIC urticarialpapules and plaques of preg\-nancy \(PUPPP\)', r''],
    ['4ab0c1cb-1530-4e26-a64e-b97563f67fb2', r'# 1\. Acne Vulgaris\/', r'References'],
    ['4ad0b6da-eda4-44b4-a59f-facf8f46b19f', r'# 1\. Normal Breast and Physiological Changes', r'References'],
    ['4dc05d78-96c4-4e87-bc49-3b82e8b73d2d', r'# Section 1 Differential Diagnosis of Abnormal Symptoms and Signs\/', r'#### References'],
    ['7b118c1e-1e6f-4380-b8a2-67bbeba6bd22', r'1\.2 History of the Classification of Cutaneous Lymphomas', r'References'],
    ['7baea7cd-b7c0-4b9d-9ca1-421a9f0af9e4', r'Neurodevelopmental Disorders', r'21\.12\-1 What are some of the strengths you perceive in this family\?'],
    ['7ce3f548-2a55-4fe8-85fe-d926f4f615da', r'1\.\xa0The Skin and Eruptives Lesions', r'Fig\. 11\.176'],
    ['7f497e27-cffa-46c9-8d9d-ed6e5a3f6904', r'1\.\xa0Clinical Examination and Approach to the Patient in Dermatology', r'Fig\. 43\.1'],
    ['8a5e068b-0e53-4195-a067-f5ac1dea28af', r'\*\*NORMAL STRUCTURE\*\*', r'\*\*REFERENCES\*\*'],
    ['8e6cef70-1573-4f89-8f26-9371fb711243', r'\*\*THE CONCEPT OF PSYCHOSIS\*\*', r'\*\*Other approaches like Errorless learning to'],
    ['9b23e3d1-25aa-4df6-b97d-d32704dbd099', r'###### Diagnosis in Energetic Medicine', r'#### Glossary of Terms'],
    ['32de240a-1f6d-487c-a89f-f0f81ff3ba94', r'The medical history and physical examination are not sepa\-rate entities，', r'\*\*Index\*\*'],
    ['52a3f993-17bf-42a3-9f0f-de829faf67d1', r'\*\*Children with speech disorder: defining the problem\*\*', r'# APPENDIX 2: Sentence Imitation Task'],
    ['54be2232-4d50-438e-b6c5-20ca7f592d76', r'\*\*Psychosocial Factors in Differential Diagnosis\*\*', r'\*\*ACKNOWLEDGMENTS\*\*'],
    ['75f3acc7-3f76-4a2f-aa07-8fd59eadbdeb', r'\*\*Differential Diagnosis：General Princioles\*\*', r'\*\*Abdominal cutaneous reflex， 187，225Amyoplasia congenita\.'],
    ['be75c9aa-cf5d-4704-8a58-2ef9a283277e', r'\*\*1 Introduction\*\*', r'\*\*References\*\*'],
    ['c6efe251-3d71-49a9-ad3e-f2b180433fac', r'\*\*ABDOMINAL PAIN\*\*', r'\*\*INDEX\*\*'],
    ['c16df092-3e81-4fb1-98cb-fe71d0be2a7d', r'\*\*Introduction to Pancreatic Cystic Neoplasms\*\*', r'\*\*References\*\*'],
    ['c66a2992-fc0f-4d95-99e3-2bc43a40b132', r'\*\*INTRODUCTION\*\*', r'\*\*REFERENCES\*\*'],
    ['c975fde5-7859-464a-84c1-e4db235db8e3', r'\*\*Chest Wall Deformity\*\*', r'\*\*Achterman C， Kalamchi A\. Congenital deficiency of the\*\* \*\*fibula\. J Bone Joint Surg Br\. 1979；61\-B：133\-7\.\*\*'],
    ['cdfff79f-aa22-472a-8aab-c8b2f60bffd1', r'\*\*ABDOMINAL PAIN\*\*', r'Note： Page numbers followed by “b，""f"and "t"refer to boxes， figures， and tables， respectively\.'],
    ['d5577941-ae84-44fd-a89a-4b64c772ac54', r'\*\*HISTORY\*\*', r'\*\*SUGGESTED READING\*\*'],
    ['dffa4729-443d-4835-b5b9-0320e4dfa0e3', r'\*\*FIrs T\-Tr IMEsTEr U LTr Aso UNd\*\*', r'\*\*rEFErENc Es\*\*'],
    ['e3a6f768-2da1-4bd4-8ab2-0b145e705896', r'\*\*Blood\-brain barrier\*\*', r'\*\*Appendix A Clinical Pears\*\*'],
    ['e4f000d3-0281-4b43-958b-5b26c8f367df', r'\*\*1 AbdominalDistention\*\*', r'\*\*_Pai_\*\*'],
    ['e4f287cc-1c54-40a0-ab88-fd2d810d26d2', r'\*\*Pinterest\*\*', r'abdominal inspection'],
    ['e8f137bf-8511-4c2b-94ef-16e64eb02618', r'\*\*_Prerenal_\*\*', r'APPENDIX'],
    ['e0823e30-40ee-42a2-ac6b-cf786070cefb', r'\*\*Introduction\*\*', r'\*\*Index\*\*'],
    ['ec09cf96-eba3-40d6-a0fe-dfbf2f2bf292', r'\*\*The Routine History and Physical Examination\*\*', r'\*\*Abscesses\*\*'],
    ['efb0e6f4-6238-4735-9e4c-6f4e26e39d1b', r'Abstract', r'References'],
    ['f1bfdcd8-75e1-42c0-969e-342022b12a25', r'Chapter 1', r'\*\*Index\*\*'],
    ['f596e33d-e08a-4734-8805-3d0fcb84b75c', r'\*\*Ischemic Stroke\*\*', r''],
    ['fe1c5f78-e005-4f95-be4e-c84754a0702b', r'\*\*Tissue Processing Overview\*\*', r'\*\*Index\*\*'],
]

class clean_pattern:
    def __init__(self):
        pass

    # 通用删除从文章开头到某一段
    def delete_page_start(self, context, pattern):
        # 避免重复加标签，特征最好合并为1-2条，当段保留一条，当段删除一条。
        # end_pattern = [
        #     [r'(^[#\*_ ]*(Abstract|I?ntroduction|Section\||INTRODUCTION|CHAPTER _1_|FIrs T-Tr IMEsTEr U LTr Aso UNd|DUKERADIOLOGT_ _CASE REVIEW)：?[_\* ]*$)', 0],
        #     [r'(^[#*_ ]*(Background|Preface|Foreword)：?[_\* ]*$)', 0],
        # ]
        end_index = 0
        # con_len = int(len(context)/5)
        flag = False
        for index, item in enumerate(context):
            if re.search(pattern, item):
                end_index = index
                flag = True
                break
        if not flag:
            print(pattern)

        for i in range(0, end_index):
            context[i] = "开头批量删除-1:<u>{}</u>".format(context[i])
            # context[i] = ""

        return context


    def delete_page_ending(self, context, ending_starts):
        # ending_starts = [
        #     r'(^|\n)[#\* _]*(APPENDIX.{0,8})[#\* _]*($|\n)',
        #     r'(^|\n)[#\* _]{0,4}(Reference|REFERENCE)[Ss]?[#\* _]{0,4}($|\n)',
        # ]
        for start in ending_starts:
            flag = False
            start_index = len(context)
            ref_started = []
            for index, item in enumerate(context):
                if re.search(start, item.strip()):
                    ref_started.append(index)
                    flag = True

            if not flag:
                print(start)

            if ref_started:
                start_index = ref_started[-1]

            if start_index != len(context):
                for i in range(len(context)-start_index):
                    context[start_index] = "结尾批量删除-1:<u>{}</u>".format(context[start_index])
                    start_index += 1
            if flag:
                break
            # context = context[0:start_index]

        return context


    # 通用句中某一部分的删除
    def delete_page_middle(self, context):
        """
        通用删除某一部分方法
        :param context: 切分过的内容，列表结构
        :param start_to_end的每一项[0]: 从某一段开始的特征
        :param start_to_end的每一项[1]: 到某一段结束的特征
        :param start_to_end的每一项[2]: 根据结束段是否删除设置1或0
        :return: 返回打过标签的列表
        """
        start_to_end = [
            [r'(^[\*_ ]*(CONTENTS|Contents)[\*_ ]*$)', r'(^[#\*_\s]*([A-Z][a-zA-Z]{3,}( [a-zA-Z]{3,}){0,8})：?[_\*\s]*$)|(.{200,})', 0],
            # [r'(^\*\*SECTION\*\*$)', r'(^[#\*_\s]*([A-Z][a-zA-Z]{3,}( [a-zA-Z]{3,}){0,8})：?[_\*\s]*$)|(.{200,})', 0],
        ]

        for middle in start_to_end:
            delete_line_index = []
            flag = False
            for index, item in enumerate(context):
                if re.search(middle[0], item):
                    satrt = [index, 0]
                    delete_line_index.append(satrt)
                    flag = True
                    continue

                if flag:
                    if re.search(middle[1], item):
                        end = [index, 1]
                        delete_line_index.append(end)
                        flag = False
                    else:
                        pass

            length = len(delete_line_index)
            if length >= 2:
                for i in range(1, length):
                    if delete_line_index[i - 1][1] < delete_line_index[i][1]:
                        start_index = delete_line_index[i - 1][0]
                        end_index = delete_line_index[i][0]
                        for i in range(start_index, end_index + middle[2]):
                            context[i] = "通用间距删除-1:<u>{}</u>".format(context[i])
                            # context[i] = ""
        return context


class speicalProces:
    def __init__(self):
        pass

    def is_title(self, con):
        patter = r'(^[\\\*_ #]*(SUGGESTED READING|Suggested Reading|ACKNOWLEDGMENTS?|Acknowledge?ments?|[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc] ?[Ee][Ss]?|(Selected )?References?|FURTHER READING|Further reading( list)?|Useful websites)[\*_]*$)'
        if re.search(patter, con):
            return True
        else:
            return False

    def is_person_name_ratio_high(self, text):
        text = text.strip('*_ ')
        doc = nlp(text)
        total_characters = len(text)
        person_characters = sum(len(ent.text) for ent in doc.ents if ent.label_ == "PERSON")
        if total_characters == 0:  # 避免除以零的错误
            return False
        return (person_characters / total_characters) >= 0.8

    def is_page_number(self, con):

        if len(re.findall(r'([，；] ?\d+([\-，] ?\d+)*[A-Za-z])|([ _]\d+[_ ])', con)) > 25:
            return True

        # if re.search(r'([^\d][，；\._]+ ?\d+[a-z]?[\d\-]*[a-z]?[\*_]*$)|(^[\*_]*[a-z\\\-A-Z ]+\d+[\*_]*$)|([a-zA-Z][，；\._] ?\d+[a-zA-Z]?([\-，] ?\d+[a-zA-Z]?)*[\*_ ]*$)|( \d+$)', con) and len(con) < 120:
        #     if re.search(r'(^[#\*\s_]*(CASE|[Cc]ase|[Cc]hapter|Question) \d+)|(^TABLE|SCA|HDL|[Tt]able|CHAPTER)', con):
        #         return False
        #     else:
        #         return True

        return False

    def is_ref(self, con):
        flag = False
        patterns = [
            r'^[\*\.]*[\d _]*(\\?\[\d+\\?\]?|_\d+_ ?|\d+\\?[\.，][^\d]|[A-Ze][A-Z\-\'a-z]+( [A-Z\-\'a-z]+)?[， ,]?[A-Z ]{1,4}[\.，,：\(])',  # 参考文献开头，序号或者人名
            r'([\s\.，,]+et al?[\.:：，,]+)',  # et al
            r'(\d+(\((\d+[,， ]+)?(Suppl\.? )?\d+\))?[：:；; ,，]+[a-zA-Z]?\d+)|([a-zA-Z]{0,2}\d+[\-–][a-zA-Z]{0,2}\d+[，,\.])|(\d+\([a-zA-Z]{0,2}\d+([\-–][a-zA-Z]{0,2}\d+)?\)[：:；; ,，])|(\([^\(\)]*p[p\. ]*\d+[\-–][a-zA-Z\d]{1,4}\)[，,\.])',  # 页码范围格式
            r'([Dd]oi[：:])',  # DOI
            r'([Vv]ol\.?\s*\d+)',  # 卷号
            r'(no\.?\s*\d+)',  # 期号
            r'([，, ]+p[p \.]*\d+|p[p \.]*\d+[：,，\- ]+)',  # 页码
            r'(ht ?tps?[：:]|www\.)',  # 网址
            r'([，,；;][A-Za-z_ ]*\d{4}[，,\._]+)|([A-Z][\.，]? ?(\(\d{4}\)|\(\d{4}，[^\(\)]*\))\.)|([\.;；：:，, ]\d{4}[;；：:，,\.])|(\((20[012]\d|1[89]\d{2})\))',  # 年份
            r'(ed \d+[，,])|((2nd|1st|3rd|\d+th) ?ed)|(\([Ee]ds?\.?\))',  # 版本号
            r'(Accessed|editor：|Pub\-?lishing|Germany：|London：|book)',  # 访问、出版、编辑、地点
            r'(， ?(?!IV|VI)[A-Z]{2,3}[，,：\.])',  # 地名，缩写
            r'(ISBN：)',  # ISBN
            r'(\d+([\.\\\/\-]\d+){2,})'  # 10.1007/978-1-4614-8344-1\_38
        ]
        p_sum = 0
        for pat in patterns:
            if re.search(pat, con):
                p_sum += 1
        if (p_sum >= 3 and len(con) < 500) or (p_sum == 2 and len(con) < 300):
            flag = True
        # print(con, f'|{p_sum}|', '\n')

        return flag

    def move_duan(self, context):
        con_len = len(context)
        pp = r'(^(?=.{0,150}$)[\*_\s]*\d+(\.\d+)+[\s_]*[A-Z].*)'
        for i, con in enumerate(context):
            # 目录段落群
            if i > 0 and i < len(context) - 1 and all((re.search(pp, context[j]) or re.search(r'^目录段删除', context[j])) for j in range(i-1, i+2) if j >= 0 and j < len(context)):
                context[i] = "目录段删除-1:<u>{}</u>".format(context[i])
                context[i-1] = "目录段删除-1:<u>{}</u>".format(context[i-1])
                context[i+1] = "目录段删除-1:<u>{}</u>".format(context[i+1])
                continue

            # 无关标题及其后一段
            if self.is_title(con):
                context[i] = "无关标题删除-1:<u>{}</u>".format(context[i])
                context[i+1] = "无关标题后段删除-1:<u>{}</u>".format(context[i+1])
                continue

            # 页码段落删除
            if self.is_page_number(con):
                context[i] = "目录索引段删除-1:<u>{}</u>".format(context[i])
                continue

            # # 人名段落删除
            # if self.is_person_name_ratio_high(con):
            #     context[i] = "人名段删除-1:<u>{}</u>".format(context[i])
            #     continue

            # 零碎段落删除
            count = True if len(re.findall(r'[A-Za-z]', con)) <= 3 and re.search(r'[^A-Za-z]]', con) else False
            if len(con) <= 15 and count and not re.search(r'[:：]|\d+\\?\.', con):
                context[i] = "零碎段删除-1:<u>{}</u>".format(context[i])
                # context[i] = ''
                continue

            # 参考段落删除
            if self.is_ref(con):
                context[i] = "参考段删除-1:<u>{}</u>".format(context[i])
                continue

        return context

    def move_hang(self, context, lang):
        if lang == 'en':
            context = re.sub(r'([^|\n]{45,}[a-z，→\-\d])([ _\*]*\n+\n[ _\*]*)(([\“a-z&][^\.\)]|\d+[^\.\d\\\)s]).{45,})', r'\1|删除1换行|\3', context)
            # context = re.sub(r'([,，；\(\.,;].*?[^\.\| \*]|\-)([ \*]*\n+\n[ \*]*)([a-z&\(][^\.].{3,})', r'\1|删除换行|\3', context)
            context = re.sub(r'([a-z，\-])([ _\*]*\n+\n[ _\*]*)([a-z&][^\.\)].{5,})', r'\1|删除换行|\3', context)
            context = re.sub(r'([a-z，\-])([ _\*]*\n+\n[ _\*]*)([a-z&][^\.\)].{5,})', r'\1|删除换行|\3', context)
            # context = re.sub(r'([^|\n]{45,}[a-z，\-\d])([ \*]*\n+\n[ \*]*)((\( ?[^\d]).{45,})', r'\1|删除2换行|\3', context)
            context = re.sub(r'([a-z，\d\--])([ \*]*\n+\n[ \*]*(Table) [\W\w]*?)(\n+\n[ \*]*)([a-z][^ \--].{45,})', r'\1|删除表格换行|\5\2', context)
            context = re.sub(r'([^|\n]{45,}[a-z，\-\d])(\n+\n)([ \*]*[A-Ze][A-Z\-\'a-z]+(?: [A-Ze][A-Z\-\'a-z]+)?[ \*]*\n+\n)((?:[a-z&][^\.\)]|\d+[^\.\d\\\)s]).*)', r'\3\1|删除标题插入换行|\4', context)

        return context


    def move_hang2(self, context, lang):
        if lang == 'en':
            context = re.sub(r'(\n\n[\*_ ]*(?:\d+\.|\(\d+\)))([\*_ ]*\n\n[\*_ ]*)([A-Z].*)', r'\1|删除序号换行|\3', context)  # 引用序号换行删除
            context = re.sub(r'(\-|[^|\n]{45,}[a-z，→\)])([ _\*]*\n+\n[ _\*]*)(([\“a-z&\.\(][^\.\)]).{45,})', r'\1|删除0换行|\3', context)
            # context = re.sub(r'(\-|[^|\n]{45,}[a-z，→\)])([ \*]*\n+\n[ \*]*)(([\“a-z&\.\(]).{45,})', r'\1|删除0换行|\3', context)
            context = re.sub(r'(\n[\* _]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)? (?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)?)([ _\*]*\n+\n[ _\*]*)(.*)([ _\*]*\n+\n[ _\*]*)(.*)', r'\1|删除3图换行|\7|删除3图换行|\9', context)
            context = re.sub(r'(\n\n[\*_]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+.{50,})([ \*]*\n+\n[ \*]*)(.*(?:\([a-z](?:，[a-z])?\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*(?:\([a-z](?:，[a-z])?\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*)', r'\1|删除1图换行|\5', context)
            context = re.sub(r'([ \*_]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)?)([ _\*]*\n+\n[ _\*]*)(.*[^\)\.\?？ _\*][ _\*]*\n)', r'\1|删除2图换行|\5', context)

        return context


def clean_text(context, lang, seq_id):
    split_token = "\n\n"
    # if split_token not in context:
    #     split_token = "\n"
    cp = clean_pattern()
    sp = speicalProces()
    context = re.sub(r'([\u4e00-\u9fff]+)', r'', context)

    context = context.split(split_token)
    # 若有需要再补充正则并调用，正则在对应的函数里补充
    for s_e in start_end_list:
        id = s_e[0]
        if seq_id == id:
            start = r'^' + s_e[1]
            end = [r'^' + s_e[2]]
            if s_e[1]:
                context = cp.delete_page_start(context, start)
            if s_e[2]:
                context = cp.delete_page_ending(context, end)
    cp.delete_page_middle(context)

    context = split_token.join(context)

    context = re.sub(r'\n\n(# ?(\d+\. ?.*)[\w\W]*?\n\n)(\2[\w\W]*?\n\n)(Keywords)', r'\n\n\2\n\n\4', context)
    context = sp.move_hang2(context, lang)

    context = context.split(split_token)

    final_results = []
    for item in context:
        # 1.正则
        item = item.strip('')
        for pattern_item in pattern_en:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)

        final_results.append(item)

    final_results = sp.move_duan(final_results)
    final_results = [con for con in final_results if con.strip()]
    context = split_token.join(final_results)
    context = sp.move_hang(context, lang)

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
    context = re.sub(r'([,\.?])(\s?[?,\.]){1,5}',r'\1',context)
    return context




# fw = open(r"C:\Users\Administrator\Desktop\original_data\differential_diagnosis_book\differential_diagnosis_book_clean_en.jsonl", "w", encoding="utf-8")
with open(r"C:\Users\Administrator\Desktop\original_data\differential_diagnosis_book\differential_diagnosis_book_preformat_en_chunk.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    # lines = random.sample(lines, 300)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        seq_id = item["seq_id"]
        pattern = r'7f497e27-cffa-46c9-8d9d-ed6e5a3f6904_10$'
        if re.search(pattern, seq_id):
            context = item["text"]
            lang = item["lang"]
            title = item["title"]
            context = clean_text(context, lang, seq_id)
            context = post_process(context)
            print(context, '\n---------换页----------')
        # context = context.split("\n\n")
        # print(len(context))
        # for con in context[:500]:
        #     print(con, '\n')
#         item["text"] = context
#         item = json.dumps(item, ensure_ascii=False)
#         fw.write(item + "\n")
# fw.close()