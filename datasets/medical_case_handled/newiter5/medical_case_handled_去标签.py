# coding:utf-8
# from common_re import clean_pattern
import json
from tqdm import tqdm
import re

pattern_list_en = [
    [r'([\u4e00-\u9fff])', r''],# 汉字删除
    [r'(?:\n|^)(Case \d+:.*\n+)((?:\d+\n+)(?:Case \d+: .*))',r'\1'],
    [r'(\n|[^\d]\.|\?|!|\)|”)( *(?:<sup>)?[0-9 ]+(?:<\/sup>)? *)(?:\n)',r'\1'],#单行数字  需要修改
    [r'([0-9 ]+ Cases in[^\n.]*)(?:\n)',r''],#100 cases...
    [r'((?:Section *\d+\n+)?(?:ETHICS AND LAW IN[^a-z\n]*\n+)(?:[^a-z\n]*\n+)+)',r''],
    [r'((?:ETHICS AND LAW IN CLINICAL|Ethics and Law in Clinical) *\n*(?:PRACTICE|Practice):.*)',r''],
    [r'(VARICOSE VEIN AND VENOUS ULCER \d+|SWELLINGS IN THE NECK \d+|\d+ A TEXTBOOK ON SURGICAL SHORT CASES|TESTIS, EPIDIDYMIS AND SCROTUM *\d+ *|\d* *SWOLLEN LEG *\d*|SYNDROME AND CERVICAL RIB *\d+|DISEASE, THORACIC OUTLET *\d+|\d* *A TEXTBOOK OF SURGICAL SHORT CASES)',r''],
    [r'(?:\n)(\** *_*[A-Z]\.)(\\\])',r'\1'],
    [r'(?:\n|^)((?:\([a-z]\) ?\d*)+)(?:\n)',r''],


    [r'([a-z，,0-9’;()/] *(?:>|<|\+|\–|%|\'|≥|=|≤|-)* *)(\n+)( *(?:>|<|\+|:|%|\'|≥|=|≤|-)* *([“,，./a-z‘)][^.]|\d+[^.][^.\\])|\(.{3,}\))',r'\1 \3'],
    [r'((?:i\.e\. *)|(?:e\.g\. *)|F[iI][gG][sS]?(?:ures?|URES?)?\. *)(\n+)( *(?:>|<|\+)* *[./a-zA-Z0-9‘()])',r'\1 \3'],
    [r'((?:>|<|\+)* *[./a-zA-Z0-9‘(),] *)(\n+)( *(?:i\.e\. *)|(?:e\.g\. *))',r'\1 \3'],
    [r'(?<=\n)(.*\([^\n()]*)(\n+)([^\n()]*\).*)',r'\1 \3'],
    [r'(\.)((?:(?:(?:[A-Z][a-z]+)|of) ?)+)(\n+)(-+)',r'\1\n\2\3\4'],



    [r'(=+\n+)((?:.*\n+)(?:(?:\(\d+\)\n+)?(?:.*USA_?\n+))+)',r'\1'],
    [r'(?:\n|^)((?:©.*\d{4}\n*)(?:.*(?:https?:\/\/(?:www\.)?|www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?))',r''],#版权介绍
    [r'(?:\n|^)((.*(?:https?:\/\/(?:www\.)?|www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\n*)(©.*\d{4}))',r''],


    [r'(?:\n|^)((?:.*class="ContactIcon">.*\n+)(?:.*\n)*?)(#* *Keywords|#* *Abstract)',r'\2'],
    [r'(?:\n|^)((?:.*class="ContactIcon">.*\n+)(?:.*\n)*)(Email:.*)',r'\n'],

    [r'(?:[^\n])(\*\*Fig(?:ures?|\.) ?\d+[.-]\d+[^\n*]*\*+)',r''],
    [r'(?<=\n)( *F[iI][gG][sS]?(?:ures?|URES?|\.)* ?[0-9A-Z]+([.-]\d+)*[:：.]?(?:\n+ *.{11,}|.*))',r''],#图
    [r'(?:\n)(Table [0-9.]+ \. .*\n+)(\n<sup>(<em>)?[a-z ]+(<\/em>)?<\/sup>.*\n)+',r''],#表
    [r'(?:\n|^)(Table \d+[-–.]\d+ • .*)',r''],
    [r'(?:\n|^)(Table \d+(?:[-–]\d+)*\.? [^\n•]*)(\n+[^\n|])',r'\2'],
    [r'(?<=\n)(Tablee? *\d+[：:].*)',r''],


    [r'([_*]*This page intentionally left blank *(?:\d+|to match pagination of print book)?[_*]*)',r''],


    [r'(￾|◻|||◆|†|￥\d*||\(●|■\(?)',r''],#特殊符号
    [r'(?:\n|^)( *&+ *)(?:\n)',r'\n'],

    [r'(?:\n)((?:In \d{4}.*(?:\n|$)+){2,})',r''],
    [r'([(（][^\d\n\(][^()（）\n]+(?:\(.{2,6}\))?[^()（）\n]*\d{4}[^()（）/\n]*(?:\(.{2,6}\))?[^()（）/\n]*[)）])',r''],#（人物+年份）
    [r'(?:\n|^)(By [A-Z].*[^\n.])',r''],#作者介绍
    [r'(?:\n|^)((?:Key Points[0-9]+\n+)(?:Case [0-9]+:.*)?)',r''],#空标题
    [r'(?:\n|^)([*| ]*CASE CORRELATES[*| ]*\n*[*| -]*\n*[*| -●·]*See.*\n{0,2}[| -]*)',r''],#案例例子删除
    [r'(?:\n|^)( ?\'?[A-Za-z0-9](?: ?[A-Za-z0-9]){0,2} *)(?:\n|$)',r''],#单行的单独字母

    [r'(?:\n|^)(#* *(?:Recommended Reading|Bibllography|Bibliography|REFERENCES?|Further [Rr]eading|(?:CLINICAL)? *CASE CORRELATION|Suggested Reading|Disclosure Statement|Syllabus Mapping)\n*(?:.*\n*)*)(?:\n|$)',r''],#推荐阅读删除
    [r'(?:\n|^|\()( *(?:Reproduced，?|Adapted，?) (?:with permission|from|by).*)(?:\n|\)|\])',r''],

    [r'(?:\n|^|\()( *Data from\D[^\n()（）]*\d{4}\D[^\n()（）\[\]]{0,20})(?:\n|\))',r''],#数据来源类

    [r'(?:\n|^)( *Please refer to.*?)(?:\n)',r''],
    [r'(\.)( *Please refer to.*?(?:\(p\. \d+\)\.\d+)?)(\D\.|\n)',r'\1'],

    [r'(?:\n|^)(See.*(?:page|Table|Case|text).*)',r''],
    [r'(\([^()\n]*see[^()\n]*(?:page|[pP]\.\d*|Table|Case|text|Plate)[^()\n]*\))',r''],

    [r'(?:\n|^)(Table \d+\.\d+)(\n+)(.*[^.?!])',r'\1 \3'],
    [r'(?<=\n)((?:Case *\d+[:：].*\n*)|Duties of a Doctor *\n*| *Rheumatology *\n*|[A-Z]+ *\n*|Anaesthesia *\n*|Neurology *\n*|Neurosurgery *\n*)(?:$)',r''],
    [r'((?:Case *\d+[:：].*\n*))(?:$)',r''],

    [r'(?<=\n)( *Source *[：:].*)',r''],
    [r'(?<=\n)(\(([A-Z][^A-Z\n\d]+ )+[A-Z][^A-Z\n\d]+\) *\n*)(?:$)',r''],
    [r'(\([^()\n]*F[iI][gG][sS]?(?:ures?|URES?|\.)?[^()\n]*\))',r''],
    [r'(?:\n)([●·])( *[。(])',r'\1'],
    [r'(\([^()\n]*EPA *\d+(?:[ ，]+\d+)*\))',r''],
    [r'(?<=\n)(N(?:OTES?|otes?)[：:] *The author.*)',r''],
    [r'(?:\n)((?:(?:[A-Z]+[^A-Z\n ]* ){2,}\(\d{4}-\d{4}\).*(?:\n|$)+){2,})',r''],

    [r'(?:\n|^)(\|)(CASE \d+)',r'\2'],
    [r'(?<=\n)([^\n\(\)]*)(\()([^\n\)]*)(?:\n)',r'\1\3'],
    [r'(?<=\n)([^\n\(]*)(\))(.*)(?:\n|$)',r'\1\3'],
    [r'(?:\n)(A)\.?(.*)(B)\n+(.*)(\n+C\..*)(\n+D\..*)',r'\1.\2\n\3.\4\5\6'],
    [r'[^\n](\| *Table \d+(?:[-–]\d+)*\.?.*\|)(?:\n+).*\|.*',r'\n\1'],


    #个例
    [r'(?:\n)([*_]*Key Points[*_]*)(\n+[*_]*Key Points[*_]*)',r'\1'],
    [r'(?:\n)([*_]*Ms. Rose is a 36 year-old attractive Caucasian woman.*[*_]*)(\n+[*_]*Ms. Rose is a 36 year-old attractive Caucasian woman.*[*_]*)',r'\1'],

    [r'(\.)( *。)',r'\1'],
    [r'(●+)(?:\n|$)',r''],
    [r'(?:\n|^)(> Courtesy of Dr. Mae Melvin, Centers for Disease Control and Prevention\.?|> Reproduced, with permission, from USMLERx.com\.?|FAITH, VALUES AND CULTURE|Faith, Values and Culture|Kimberly L. DiMaria|Children’s Hospital Colorado, Aurora, CO, USA|QaQ一?|Type V|Type IV|Typel|([\.■]*m+)+|Orthopaedics?|TRAUMA AND ORTHOPAEDICS|Ty\.|RAYNAUD’S SYNDROME, BUERGER’S|Ists|Ce Wang|Red dot)(?:\n|$)',r''],
    [r'(?:\n|^)(Clinical Case Studies for the Family Nurse Practitioner， First Edition. Edited by Leslie Neal-Boylan|@ 2011 John Wiley & Sons， Inc. Published 2011 by John Wiley & Sons， Inc.*|Rigler’s double wall sign229)',r''],
    [r'(?:\n|^)([-\']? *(?:!|\.|;|【|。|\}|\)|》\(?))', r''],
    [r'(?:\n|^)( *CCFC\d{4} *)',r''],
    [r'(?:\n|^)(References?\n*(?:\d+\..*\n*)+)',r''],
    [r'(?:\n)((?:(?:.*((?:\d{4}(?: *.{0,9} *\d*)?[;；:：])|(?:[:：;；,，] *\d{4}))\d*(\([0-9A-Z]+\))?[:：]?[0-9A-Za-z]*(?:-\d+)*)[^\n)\]]{0,15}(\n{1,}|$)){2,})',r''],
    [r'((.*website： *)?(?:https?[:：]\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?)',r''],

    [r'([a-z，,0-9’;()/] *(?:>|<|\+|\–|%|\'|≥|=|≤|-)* *)(\n+)( *(?:>|<|\+|:|%|\'|≥|=|≤|-)* *([“,，./a-z‘)][^.]|\d+[^.][^.\\])|\(.{3,}\))',r'\1 \3'],

    [r'(?:\n|^)((?:[^#\n•●©>·:： ]{1,} +){10,}[^\n ]*[a-z，,0-9’;(/] *)(\n+)( *[A-Z][^. ] *(?:[^#\n•●©>·:： ]{1,} +){10,}[^\n :：]*)',r'\1 \3'],
    [r'(?:\n|^)((?:[^#\n•●©>·:： ]{1,} +){10,}[^\n ]*[A-Z] *)(\n+)( *[a-z，,0-9’;)/][^. ] *(?:[^#\n•●©>·:： ]{1,} +){10,}[^\n :：]*)',r'\1 \3'],

    [r'([,，] *)(\n+)( *[^#\n•●©>·:：|])',r'\1 \3'],
    [r'([^#\n•●©>·:：|] *)(\n+)( *[,，])',r'\1 \3']






]

class clean_pattern:
    def __init__(self):
        pass

    # 通用英文正则
    def clean_pattern_en(self):
        pattern_en = [
            # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
            [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:][^\(\)]*\))',r''],   # 1. 这些固定的词语紧贴左括号
            [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))',r'\1)'],   # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
            [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version)s?[\s\.:][^\(\)]*\))',r''], # 最广泛的形式从左括号匹配到右括号

            [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r''],     # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
            [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
            [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)',r''], # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
            [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r''],     # 特殊数字  排除可能出现的次幂情况
            [r'(.*(doi|DOI)\s?:.*)', r''],  # 存在有DOI描述的句子
            [r'((\\)?\[[\d\s,，\-\–—]{1,}(\\)?\])', r''],  # 带有方括号的数字引用
            [r'((\\)?\([\d\s,，\-\–—]{1,}(\\)?\))', r''],  # 带有圆括号的数字引用
            [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(\\)?\])',r''],   # 固定格式  带有[]的图片表格描述 附录描述 协议描述 无关网址描述
            [r'(^Full size.*)', r''],  # Full size image/table 原文这里应该是一个图/表没识别出图形
            [r'(\([^\(\)]*(arrow|←|→)[^\(\)]\))', r''],  # ...箭头 描述图里面不同颜色的箭头

        ]
        return pattern_en

    # 通用中文正则
    def clean_pattern_zh(self):
        pattern_zh = [
            [r'([\(][^\)\(]*见?(图|表|详见)\s?\d+[^\)\(]*[\)])', r''],  # 带有英文括号的
            [r'(（[^）（]*见?(图|表|详见)\s?\d+[^）（]*）)', r''],
            [r'(致谢.*)',r''],
            [r'(^[\*#]{0,4}点击查看.*)',r''],     # 点击查看...
            # [r'(^[\*#]{0,4}(图|表)\s?\d+$)',r'通用删除5(中):<u>\1</u>'],   # 这一段中只有一个 表\d+
            [r'(.*利益冲突.*)',r''],    # 文章末利益冲突
            [r'(^[\*#]{0,4}详见.*)',r''],    # 详见...
            [r'(^[\*#]{0,4}阅读更多.*)',r''],  # 阅读更多...
            [r'((\\)?\[[\d\s,\-\–—]{1,}(\\)?\])', r''],  # 带有方括号的数字引用
            # [r'((\\)?\([\d\s,\-\–—]{1,}(\\)?\))', r'通用删除10(中):<u>\1</u>'],  # 带有圆括号的数字引用
            [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r''],  # 特殊数字  排除可能出现的次幂情况
        ]
        return pattern_zh

    def ending_starts(self):
        ending_starts = [
            [r'^[#\*]{0,4}\s?Availability of data and materials'],
            [r'^[#\*]{0,4}\s?(To read this article in full you will need to make a payment|Call your doctor for|Other side effects not listed may also occur in some|Supplemental Online Material|### Footnotes|Article info|Acknowledgments?|Trial Registration|Files in this Data Supplement|Potential Competing Interests|Closing)s?'],
            [r'[#\*]{0,4}\s?(Reference|Funding and Disclosures|Polls on Public)s?'],
            [r'^(Ethics Statement|Ethics?|Ethics Approval|Ethical Approval|Statement of Ethics|Ethics Approval and Informed Consent|Funding|Consent for publication|Author Contributions|Compliance with Ethical Standards|Study Approval Statement|Ethical Consideration)[$\n]'],
            [r'^[#\*]{0,4}参考文献'],   # 中文参考文献
            # [r'^(Abbreviations)s?'],   # 缩写词 类似于文言文下面的词语注释


        ]
        return ending_starts
    # 通用删除从文章开头到某一段
    def delete_page_start(self, context, end, is_add):
        """
        通用删除从文章开头到文章某一段结束   需要判断需不需要加上结束的这段来决定end_index是否加1
        :param context: 传入分割好的文本context，列表结构
        :param end: 传入到某段结束删除特征的正则形式
        :param is_add: 传入1或0
        :return: 带有标签的context
        """
        end_index = 0
        for index, item in enumerate(context):
            if re.search(end, item):
                end_index = index
        if end_index > 0:
            for i in range(0, end_index + is_add):
                # context[i] = "通用开头删除-1:<u>{}</u>".format(context[i])
                context[i] = ""
        return context

    # 通用删除从某一个段开始到文章结束
    def delete_page_ending(self, context, start):
        """
        通用删除从某一段开始到文章结束
        :param context: 分割好的文本，列表结构
        :param start: 从某段开始删除开始的特征的正则形式
        :return: 列表结构的文本
        """
        new_context = []
        references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(start, item.strip()):
                references_started = True
            if references_started:
                # item = "通用结尾删除-1:<u>{}</u>".format(item)
                item = ''
            new_context.append(item)
        return new_context

    # 通用句中某一部分的删除
    def delete_page_middle(self, context, start, end, is_add):
        """
        通用删除某一部分方法，需要传入开始的特征和结束的特征的正则   不包含结束的段，如果想要包含需要在end_index处加1
        :param context: 切分过的内容，列表结构
        :param start: 从某一段开始的特征
        :param end: 到某一段结束的特征
        :param is_add: 传入1或0
        :return: 返回打过标签的列表
        """
        delete_line = 0
        delete_line_index = []
        for index, item in enumerate(context):
            if re.search(start, item):
                delete_line_index.append(index)
                delete_line += 1
            if re.search(end, item):
                delete_line_index.append(index)
                delete_line -= 1
        if delete_line <= 0 and len(delete_line_index) >= 2:
            start_index = delete_line_index[0]
            end_index = delete_line_index[-1]
            for i in range(start_index, end_index + is_add):
                # context[i] = "通用间距删除-1:<u>{}</u>".format(context[i])
                context[i] = ""
        return context


class speicalProces:
    def __init__(self):
        pass
    def step0_common_clean(self,context,cp,lang):
        result = []

        ending_starts = cp.ending_starts()
        for ending_start in ending_starts:
            start = ending_start[0]
            context = cp.delete_page_ending(context, start)

        pattern_en = cp.clean_pattern_en()
        pattern_zh = cp.clean_pattern_zh()
        for item in context:
            # 1.正则
            if lang == "en":
                for pattern_item in pattern_en:
                    src = pattern_item[0]
                    tgt = pattern_item[1]
                    # print(pattern_item)
                    item = re.sub(src, tgt, item)
            else:
                for pattern_item in pattern_zh:
                    src = pattern_item[0]
                    tgt = pattern_item[1]
                    item = re.sub(src, tgt, item)
            result.append(item)
        return result






def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()

    pattern_list = pattern_list_en
    for pattern_item in pattern_list:
        context = re.sub(pattern_item[0], pattern_item[1], context)




    context = context.split(split_token)
    result = sp.step0_common_clean(context,cp,lang)


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
    context = re.sub(r'[。，](\s?[。，：；]){1,5}',r'。',context)
    context = re.sub(r'([,\.?])(\s?[?,\.]){1,5}',r'\1',context)
    return context




# fw = open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\reclean5_medical_case_handled.jsonl", "a", encoding="utf-8")
with open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\test.jsonl", "r", encoding="utf-8") as fs:
# with open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\medical_case_handled_preformat.jsonl", "r",encoding="utf-8") as fs:

    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "5a9815c6-c389-410a-884d-86bd79e6dc56":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0',r' ',context)
        context=re.sub(r'[\*\_]]{0,}',r'',context)
        context = clean_text(context, lang)
        context = post_process(context)
        print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        # fw.write(item + "\n")
#
