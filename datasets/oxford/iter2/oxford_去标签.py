import json
from tqdm import tqdm
import re

pattern_en = [
    # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
    [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:][^\(\)]*\))',r''],  # 1. 这些固定的词语紧贴左括号
    [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))',r'\1)'],  # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version)s?[\s\.:][^\(\)]*\))',r''],  # 最广泛的形式从左括号匹配到右括号
    [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r''],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
    [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)', r''],
    # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?\s{0,}\d+[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r''],
    # 特殊数字  排除可能出现的次幂情况
    [r'(.*(doi|DOI)\s?:.*)', r''],  # 存在有DOI描述的句子
    [r'((\\)?\[[\d\s,，\–\-—]{1,}(\\)?\])', r''],  # 带有方括号的数字引用
    [r'((\\)?\([\d\s,，\-\–—]{1,}(\\)?\))', r''],  # 带有圆括号的数字引用
    [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(\\)?\])',r''],  # 固定格式  带有[]的图片表格描述 附录描述 协议描述 无关网址描述
    [r'(^Full size.*)', r''],  # Full size image/table 原文这里应该是一个图/表没识别出图形
    [r'(\([^\(\)]*(arrow|←|→)[^\(\)]\))', r''],  # ...箭头 描述图里面不同颜色的箭头

    # 9.4继续添加
    [r'(^Full size.*)', r''],  # Full size image/table 原文这里应该是一个图/表没识别出图形
    [r'(\([pP]\.?\d+[^\(\)]*\))', r''],  # 带有括号的([Pp]. ...)第几页
    [r'(\([^\(\)]*Additional file[^\(\)]*\))', r''],  # 附加文件带括号
    [r'([\*#]{0,4}Additional file.*)', r''],  # 附加文件
    [r'(^Download\s.*)', r''],  # 段落开头下载 ...
    [r'^.{0,3}(Editor.s note|To learn more about).*', r''],  # 从段落头开始 编辑信息 更多信息
    [r'(^(You can find more|About this video).*)', r''],  # 段落开头 你可以找到更多/关于本视频

    # [r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?)\s?\d+[\*#]{0,4})',r'删除1:<u>\1</u>'],     # 删除单行一直Figure 1
    [r'(^Open in new tab( Download slide.*)?)', r''],  # 单行只有一个Open in new tab Download slide
    [r'([\.,;][^\.,;]*\s([Vv]ideo|VIDEO|Fig)s?[\s\.:][^\(\)]*\))', r')'],
    [r'(\([^\(\)]*\s([Vv]ideo|VIDEO)s?[\s\.:][^\(\)]*\))', r''],  # Vidio   ...视频带括号

]
pattern_zh = [
    [r'([\(][^\)\(]*见?(图|表|详见)\s?\d+[^\)\(]*[\)])', r''],  # 带有英文括号的
    [r'(（[^）（]*见?(图|表|详见)\s?\d+[^）（]*）)', r''],
    [r'(致谢.*)',r'通用删除3(中):<u>\1</u>'],
    [r'(^[\*#]{0,4}点击查看.*)',r'通用删除4(中):<u>\1</u>'],     # 点击查看...
    # [r'(^[\*#]{0,4}(图|表)\s?\d+$)',r'通用删除5(中):<u>\1</u>'],   # 这一段中只有一个 表\d+
    [r'(.*利益冲突.*)',r'通用删除6(中):<u>\1</u>'],    # 文章末利益冲突
    [r'(^[\*#]{0,4}详见.*)',r'通用删除7(中):<u>\1</u>'],    # 详见...
    [r'(^[\*#]{0,4}阅读更多.*)',r'通用删除8(中):<u>\1</u>'],  # 阅读更多...
    [r'((\\)?\[[\d\s,\-\–—]{1,}(\\)?\])', r'通用删除9(中):<u>\1</u>'],  # 带有方括号的数字引用
    # [r'((\\)?\([\d\s,\-\–—]{1,}(\\)?\))', r'通用删除10(中):<u>\1</u>'],  # 带有圆括号的数字引用
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除11(中):<u>\1</u>'],  # 特殊数字  排除可能出现的次幂情况

    # 9.4继续添加
    [r'(（\s{0,}）)', r'通用删除12(中):<u>\1</u>'],  # 空括号里面什么都没有
    [r'(（详见[^（）]*）)', r'通用删除13(中):<u>\1</u>'],  # 中文括号详见...
    [r'([，。]见(图|表)\d+[^，。]*)', r'通用删除14(中):<u>\1</u>'],  # 半句到前后的标点处截至 见图/表1...
    [r'(（[^（）]*视频[^（）]*）)', r'通用删除15(中):<u>\1</u>'],  # 带有中文（）的...视频
]

ending_starts = [
    r'^[#\*]{0,4}\s?(Availability of data and materials|AVAILABILITY OF DATA AND MATERIALS?)',
    r'^[#\*]{0,4}\s?(To read this article in full you will need to make a payment|Call your doctor for|Other side effects not listed may also occur in some|Supplemental Online Material|### Footnotes|Article info|Acknowledgments?|Trial Registration|Files in this Data Supplement|Potential Competing Interests|Closing)s?',
    r'[#\*]{0,4}\s?(Reference|Funding and Disclosures|Polls on Public|Conflict of [Ii]nterest|Declaration|Important Point)s?[#\*]{0,4}\s{0,}($|\n)',
    r'^(Ethics Statement|Ethics?|Ethics Approval|Ethical Approval|Statement of Ethics|Ethics Approval and Informed Consent|Funding|Consent for publication|Author Contributions|Compliance with Ethical Standards|Study Approval Statement|Ethical Consideration)[$\n]',
    r'^[#\*]{0,4}参考文献',   # 中文参考文献
    # [r'^(Abbreviations)s?($|\n)'],   # 缩写词 类似于文言文下面的词语注释
    
    # sudo 添加文章末尾删除主要为大写
    r'^ACKNOWLEDGMENT(S)?',   #感谢
    r'^ACKNOWLEDGEMENT(S)?(\n|$)',  # 单行只有一个ACKNOWLEDGEMENTS以下的需要删除
    r'^AVAILABILITY OF DATA AND MATERIAL(\n|$)',  # 单行AVAILABILITY OF DATA AND MATERIAL全为大写
    r'^(CONFLICTS? OF INTEREST STATEMENT|CONFLICTS?(ING)? OF INTEREST|Confict of Interest statement)',# 单行利益冲突CONFLICT OF INTEREST STATEMENT 全为大写
    r'^(FINANCIAL DISCLOSURES/)?FUNDING(\n|$)',  # 拨款
    r'^(ETHICAL|ETHICS) APPROVAL',  # 伦理...
    r'^DATA AVAILABILITY',  # 数据可用性
    r'^SUPPLEMENTARY MATERIAL',  # 补充材料
    r'^ACKNOWLEGE?MENTS?',  # 感谢
    r'^AUTHORS’ CONTRIBUTIONS?',  # 作者补充
]

pattern_more_line_feed = [
    [r'^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table)[\*#]{0,4}\s?\d+.{0,4}(\n|$)'],
]


class clean_pattern:
    def __init__(self):
        pass
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

    # 解决多余换行问题
    def more_line_feed(self, context, Line_feed_rules):
        """
        本方法是实现有多余换行的连接操作。需要传入一个列表，列表中的元素为：
        1. 仅有 [current_line_rule]，只需要匹配当前行；
        2. 包含 [current_line_rule, next_line_rule]，需要同时匹配当前行和下一行。
        :param context: 段落内容列表
        :param Line_feed_rules: 换行规则列表，规则为 [当前行的规则, 下一行的规则] 或者 [当前行的规则]
        :return: 处理后的 context
        """
        # 去除空字符串
        context = [item for item in context if item.strip() != ""]

        index = 0
        while index < len(context):
            item = context[index]
            stripped_item = item.strip()
            # 检查所有换行规则
            for line_feed_rule in Line_feed_rules:
                current_line_rule = line_feed_rule[0]
                # 如果规则长度为 2，需要同时匹配当前行和下一行
                if len(line_feed_rule) == 2:
                    next_line_rule = line_feed_rule[1]
                    if index + 1 < len(context) and re.search(current_line_rule, stripped_item) and re.search(next_line_rule, context[index + 1].strip()):
                        # 合并当前段和下一段
                        context[index] = item.rstrip() + " " + context[index + 1].lstrip()
                        # 删除下一段
                        del context[index + 1]
                        index = index-1
                        break

                # 如果规则长度为 1，只需要匹配当前行
                elif len(line_feed_rule) == 1:
                    if index + 1 < len(context) and re.search(current_line_rule, stripped_item):
                        # 合并当前段和下一段
                        context[index] = item.rstrip() + " " + context[index + 1].lstrip()
                        # 删除下一段
                        del context[index + 1]
                        # index = index-1
                        break

            index += 1
        return context

    # 解决缺少换行问题
    def lack_line_feed(self, context, line_feed_rules):
        """
        本方法是实现缺少换行的添加操作。需要传入一个列表，列表中的元素为：
        [current_line_rule, complete_rule]，需要传入当前的内容规则和修改后的内容规则。
        :param context: 段落内容列表
        :param line_feed_rules: 缺少换行的规则列表，每个规则包含当前行匹配的规则和修改后的内容规则
        :return: 处理后的 context
        """
        index = 0
        while index < len(context):
            item = context[index]
            stripped_item = item.strip()
            # 遍历每个换行规则
            for line_feed_rule in line_feed_rules:
                current_line_rule = line_feed_rule[0]
                complete_rule = line_feed_rule[1]
                # 如果当前行符合 current_line_rule，则根据 complete_rule 进行处理
                if re.search(current_line_rule, stripped_item):
                    # 根据 complete_rule 插入换行操作，可以是换行符或其它格式
                    context[index] = re.sub(current_line_rule, complete_rule, stripped_item)
            # 继续处理下一段
            index += 1
        return context
class speicalProces:
    def __init__(self):
        pass
    def step0_common_clean(self,context,cp,lang):
        result = []
        combined_ending_starts = '|'.join(ending_starts)
        context = cp.delete_page_ending(context, combined_ending_starts)
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


def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()
    context = context.split(split_token)
    context = sp.step0_common_clean(context,cp,lang)
    new_context = cp.more_line_feed(context, pattern_more_line_feed)
    i = 0
    while i < len(new_context):
        if re.search(r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?)[\*#]{0,4}\s?\d+.{0,4}\|删除)',new_context[i]):
            new_context[i] = re.sub(r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?)[\*#]{0,4}\s?\d+.*)',r'',new_context[i])
        print(new_context[i])
        i += 1


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




fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\recleanB2_oxford.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\oxford_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "cd9624a3-ffa6-40a1-a972-e4e52bcc95b8":
        context = item["text"]
        if re.search("Author notes",context):
            continue
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

