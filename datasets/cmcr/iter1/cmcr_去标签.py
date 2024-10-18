
import json
from tqdm import tqdm
import re


pattern_list = [
    [r'(^[\*#]{0,4}图\s?\d+.*)',r''],
    [r'(（\s{0,}）)',r''], # 空括号里面什么都没有
    [r'(（详见[^（）]*）)',r''],   # 详见...
    [r'(^(视频).*)',r''],  # 单行只有一个视频
    [r'(（请扫描文章首页左下角二维码）)',r''],
    [r'本病例选自.*',r''],
    [r'([，。]见(图|表)\d+[^，。]*)',r''],   # 见图/表1...
    [r'(（[^（）]*视频[^（）]*）)',r''],    # 带有（）的...视频
]

pattern_page_ending = [

]
class clean_pattern:
    def __init__(self):
        pass

    # 通用英文正则
    def clean_pattern_en(self):
        pattern_en = [
            # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
            [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|See|For more|panel|http|www|NCT\d+|NO\.|version)s?[\s\.:][^\(\)]*\))',r''],   # 1. 这些固定的词语紧贴左括号
            [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))',r'\1)'],   # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
            [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version)s?[\s\.:][^\(\)]*\))',r''], # 最广泛的形式从左括号匹配到右括号

            [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r''],     # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
            [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
            [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)',r''], # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
            [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[a-z\d+\s\-\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r''],     # 特殊数字  排除可能出现的次幂情况
            [r'(.*(doi|DOI)\s?:.*)', r''],  # 存在有DOI描述的句子
            [r'((\\)?\[[\d\s,\-\–—]{1,}(\\)?\])', r''],  # 带有方括号的数字引用
            [r'((\\)?\([\d\s,\-\–—]{1,}(\\)?\))', r''],  # 带有圆括号的数字引用
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
            [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[a-z\d+\s\-\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r''],  # 特殊数字  排除可能出现的次幂情况
        ]
        return pattern_zh

    def ending_starts(self):
        ending_starts = [
            [r'^[#\*]{0,4}\s?Availability of data and materials'],
            [r'^[#\*]{0,4}\s?(To read this article in full you will need to make a payment|Call your doctor for|Other side effects not listed may also occur in some|Supplemental Online Material|### Footnotes|Article info|Acknowledgments?|Trial Registration|Files in this Data Supplement|Potential Competing Interests|Closing)s?'],
            [r'[#\*]{0,4}\s?(Reference|Funding and Disclosures|Polls on Public)s?'],
            [r'^(Ethics Statement|Ethics?|Ethics Approval|Ethical Approval|Statement of Ethics|Ethics Approval and Informed Consent|Funding|Consent for publication|Author Contributions|Compliance with Ethical Standards|Study Approval Statement|Ethical Consideration)[$\n]'],
            [r'^[#\*]{0,4}参考文献'],   # 中文参考文献
            [r'^(Abbreviations)s?'],   # 缩写词 类似于文言文下面的词语注释


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
                context[i] = "".format(context[i])
                # context[i] = ""
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
                    item = re.sub(src, tgt, item)
            else:
                for pattern_item in pattern_zh:
                    src = pattern_item[0]
                    tgt = pattern_item[1]
                    item = re.sub(src, tgt, item)
            result.append(item)
        return result

    def step1_morelinefeed(self,context):
        for index,item in enumerate(context):
            if item.strip() == "":   # 去除某些段出现空字符串
                del context[index]
        index = 0
        while index < len(context):
            item = context[index]
            # 合并以小写字母或特定标点符号开头的段落
            stripped_item = item.strip()
            if index >= 0:
                if index + 1 < len(context) and re.search(r'^[\*#]{0,4}(图|表)\s?\d+[\*#]{0,4}$', stripped_item):
                    # 合并到下一个 item
                    context[index] = item.rstrip() + "" + context[index + 1].lstrip().lstrip()
                    # 删除下一个 item
                    del context[index + 1]
                    # 不增加 index, 继续检查当前索引位置的元素
                    index = index - 1
                    continue
            index += 1
        return context
    def step2_repeated_paragraph(self,context):   # 删除掉重复的表叙述
        for index,item in enumerate(context):
            if re.search(r'^[\*#]{0,4}表\s?\d+',item.strip()):
                if item.strip() == context[index+1].strip():
                    del context[index+1]
        return context
def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()
    context = context.split(split_token)
    if len(context) < 3:
        return ""
    result = sp.step0_common_clean(context,cp,lang)
    context = sp.step1_morelinefeed(result)
    context = sp.step2_repeated_paragraph(context)
    new_context = []
    for item in context:
        # 1.正则
        for pattern_item in pattern_list:
            src = pattern_item[0]
            tgt = pattern_item[1]
            item = re.sub(src, tgt, item)
        new_context.append(item)
    for ending_start in pattern_page_ending:
        ending = ending_start[0]
        new_context = cp.delete_page_ending(new_context, ending)
    for index,item in enumerate(new_context):
        print(index,item)

    context = split_token.join(new_context)

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




fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_cmcr.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\cmcr_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "0103327b-63de-4496-b426-2bda1b1e26d9":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0',r' ',context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
    # print(item)
        fw.write(item + "\n")

