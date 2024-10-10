
import json
from tqdm import tqdm
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
pattern_en = [
    # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
    [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:\d][^\(\)]*\))', r''],  # 1. 这些固定的词语紧贴左括号
    [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:\d][^\(\)]*)(\))', r'\1)'],  # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version|Appendix)s?[\s\.:\d][^\(\)]*\))', r''],  # 最广泛的形式从左括号匹配到右括号
    [r'(\([^\(\)]*\s?et[\s\xa0]{1,3}al[^\)\(]*\))', r''],    # 带有括号, et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r''],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
    [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)', r''],  # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?\s{0,}\d+[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除4(英):<u>\1</u>'],  # 特殊数字  排除可能出现的次幂情况
    [r'(.*(doi|DOI)\s?:.*)', r'通用删除5(英):<u>\1</u>'],  # 存在有DOI描述的句子
    [r'((\\)?\[[\d\s,\\，\–\-—]{1,}(\\)?\])', r''],  # 带有方括号的数字引用
    [r'([^\d~\s]\s{0,}(\\)?\([\d\s,\\，\-\–—]{1,}(\\)?\))', r'通用删除7(英):<u>\1</u>'],  # 带有圆括号的数字引用
    [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(\\)?\])', r''],  # 固定格式  带有[]的图片表格描述 附录描述 协议描述 无关网址描述
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
    [r'(^#*\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*)', r'通用删除16(英):<u>\1</u>'],  # 删除开头为Figure的描述

    # 以上为通用正则库
    # ========================================================================================
    # 以下补充对此组数据清洗的特定正则
    [r'(\([^\(\)]*(pone)s?[\d\s\.:][^\(\)]*\))', r''],  # 带有圆括号 里面有特征pone
    [r'(\{[^\{\}]*\})', r''],  # 带有花括号 {}里面所有
    [r'([!\.]{0,}(\\)?[\(\[\{][,\s;-]{0,}(\\)?[\)\]\}])', r'删除20:<u>\1</u>'],  # 前面可以有一个！带有各种括号的里面为空

    [r'(\[[^\[\]]*(@|#|Supplementary material|Reporting Summary|SUMMARY|data not shown)[^\[\]]*\])',r''],                # 带有方括号 里面有一个特殊符号@、#
    [r'(\([^\(\)]*(@|#|SUMMARY|data not shown)[^\(\)]*\))',r''],                # 带有圆括号 里面有一个特殊符号@、#
    [r'^(We|I) thank.*',r''],   # 一句固定格式的句子  感谢...
    # [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.|Appendix)s?[\s\.:\d][^\(\)]*\))',r'删除21:<u>\1</u>'],  # 1. 这些固定的词语紧贴左括号
    [r'^jcm-08-01366.*',r''],
    [r'(^See\s.*)',r'删除22:<u>\1</u>'],        # See在句子开头  见...
    [r'(\(ABSTRACT[^\(\)]*\))',r'删除23:<u>\1</u>'],   # 带有圆括号的ABSTRACT摘要
    [r'(References:.*)',r'删除24:<u>\1</u>'],    #  句子结尾处出现References:...  从reference开始删除
    [r'(.*no conflict of interests.*)',r'删除25:<u>\1</u>'],  # ...没有利益冲突，区别于文章尾的多段删除，这里只需要删除这一段
    [r'(^The author is grateful.*)',r'删除26:<u>\1</u>'],    # 作者感谢...的支持之类的描述
    [r'(^(Informed )?[cC]onsent:.*)',r'删除27:<u>\1</u>'],    # 知情同意、同意 ...
    [r'^(\([A-Z]*\)|[#]{1,}|Click here for additional data file.)$',r'删除28:<u>\1</u>'],    # 单行只有(A-Z)、多个#、点击查看文件
    [r'(.{20,}Supporting information.*)',r'删除29:<u>\1</u>'],    # ...支持信息... 如果Supporting information在段首则对下面的段落全部删除  否则只删除这一行

    [r'(\\)?\[[\s,\.–-]{0,}(\\)?\]',r''],      # 空\[\]  或者中间有个空格或标点
    [r'(\(\[[^\[\(\)\]]*\]\))',r'删除30:<u>\1</u>'],   # 删除前面删除剩余的一些([...])的表述
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|Appendix)s?[\s\.:\d][^\(\)]*\))', r''],# 最广泛的形式从左括号匹配到右括号
    [r'(\[[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|Appendix)s?[\s\.:\d][^\[\]]*\])', r''],# 最广泛的形式从左方括号匹配到右方括号
    [r'(\([\s,\.]{0,5}\))',r''],     # 空()

    [r'([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:\d][^\(\)]*)(\))',r')'],    # （）内出现(dose---F~(4,\ 52)~ = 5.312, p = 0.001; group × dose \[F~(4,\ 52)~ = 2.539 p = 0.051\]; Fig. [2a])，删除;后面出现的Table、Fig...到后面的右括号
    [r'(^The following are available online.*)',r'删除31:<u>\1</u>'],     # 一下内容可在...找到，一版后面接的是网址
    [r'(.*These authors contributed equally to this work.*)',r'删除32:<u>\1</u>'],   # 固定表述
    [r'(\[\^\d+\])',r''],   # 无关数字
    [r'(\(:\s?[①②③④⑤⑥⑦⑧\-⑨⑩\s,\.]{1,}\))',r''],
]


pattern_zh = [
    [r'([\(][^\)\(]*见?(图|表|详见)\s?\d+[^\)\(]*[\)])', r'通用删除1(中):<u>\1</u>'],  # 带有英文括号的
    [r'(（[^）（]*见?(图|表|详见)\s?\d+[^）（]*）)', r'通用删除2(中):<u>\1</u>'],
    [r'(致谢.*)', r'通用删除3(中):<u>\1</u>'],
    [r'(^[\*#]{0,4}点击查看.*)', r'通用删除4(中):<u>\1</u>'],  # 点击查看...
    # [r'(^[\*#]{0,4}(图|表)\s?\d+$)',r'通用删除5(中):<u>\1</u>'],   # 这一段中只有一个 表\d+
    [r'(.*利益冲突.*)', r'通用删除6(中):<u>\1</u>'],  # 文章末利益冲突
    [r'(^[\*#]{0,4}详见.*)', r'通用删除7(中):<u>\1</u>'],  # 详见...
    [r'(^[\*#]{0,4}阅读更多.*)', r'通用删除8(中):<u>\1</u>'],  # 阅读更多...
    [r'((\\)?\[[\d\s,\-\–—]{1,}(\\)?\])', r'通用删除9(中):<u>\1</u>'],  # 带有方括号的数字引用
    # [r'((\\)?\([\d\s,\-\–—]{1,}(\\)?\))', r'通用删除10(中):<u>\1</u>'],  # 带有圆括号的数字引用
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除11(中):<u>\1</u>'],  # 特殊数字  排除可能出现的次幂情况

    # 9.4继续添加
    [r'(（\s{0,}）)', r'通用删除12(中):<u>\1</u>'],  # 空括号里面什么都没有
    [r'(（详见[^（）]*）)', r'通用删除13(中):<u>\1</u>'],  # 中文括号详见...
    [r'([，。]见(图|表)[\d\s,，\-\–—]+[^，。]*)', r'通用删除14(中):<u>\1</u>'],  # 半句到前后的标点处截至 见图/表1...
    [r'(（[^（）]*视频[^（）]*）)', r'通用删除15(中):<u>\1</u>'],  # 带有中文（）的...视频

    # 以上为通用正则库
    # ========================================================================================
    # 以下补充对此组数据清洗的特定正则


    ]
Line_feed_rules = [
    [r'^.{1,10}[^\.,!]$',r'^:']
]
class clean_pattern:
    def __init__(self):
        pass

    # 通用删除从文章开头到某一段
    def delete_page_start(self, context):
        """
        通用删除从文章开头到文章某一段结束
        :param context: 传入分割好的文本context，列表结构
        :param end_pattern的每一项[0]: 传入到某段结束删除特征的正则形式
        :param end_pattern的每一项[1]: 根据当段是否删除设置1或0
        :return: 带有标签的context
        """
        # 避免重复加标签，特征最好合并为1-2条，当段保留一条，当段删除一条。
        end_pattern = [
            [r'(^[#\s]*(Abstract|ABSTRACT)：?\s*)', 0],
            [r'(^[#\s]*(Background|Introduction)：?\s*)', 0],

        ]
        end_index = 0
        for end in end_pattern:
            for index, item in enumerate(context):
                if re.search(end[0], item):
                    end_index = index + end[1]
            if end_index > 0:
                for i in range(0, end_index):
                    context[i] = "通用开头删除-1:<u>{}</u>".format(context[i])
                    # context[i] = ""
        return context

    # 通用删除从某一个段开始到文章结束
    def delete_page_ending(self, context):
        """
        通用删除从某一段开始到文章结束
        :param context: 分割好的文本，列表结构
        :param ending_starts的每一项: 从某段开始删除开始的特征的正则形式
        :return: 列表结构的文本
        """
        # 避免重复加标签，特征最好合并为1-2条，当段保留一条，当段删除一条。
        ending_starts = [
            [r'^[#\*]{0,4}\s?(References?：?|Funding( Sources| Statement| and Disclosure)?|Polls on Public|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?ment|Conflicts? of [Ii]nterest|Source of (Support|Funding)|Supplementary (Material)?)s?[#\*]{0,4}\s{0,}($|\n)'],
            [r'^.{0,10}(Competing [Ii]nterest|Funding|Source of Support|Supporting information|Availability of data and materials|Financial support and sponsorship|conflict of interest|Acknowledgement|Reporting summary|Disclosure|Supplementary information|Disclosure statement|Author contribution|Conflict of interest statement|Ethics|Conflicts of Interest|Data Availability|Data sharing statement|Additional Information).{0,10}(\n|$)s?'],
            [r'^(The author has served|There is no funding|We are indebted to|The online version of this article|Under the direction of the authors|The work was supported|Thanks to all the|This article is distributed|We are grateful to|The work performed at)']

        ]

        for start in ending_starts:
            references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
            for index, item in enumerate(context):
                if re.search(start[0], item.strip(),re.IGNORECASE):
                    references_started = True
                if references_started:
                    # context[index] = "通用结尾删除-1:<u>{}</u>".format(context[index])
                    context[index] = ''
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
            # 样例
            # [r'funding|...', r'Acknowledgments', 1],
        ]
        for middle in start_to_end:
            delete_line_index = []
            for index, item in enumerate(context):
                if re.search(middle[0], item):
                    satrt = [index, 0]
                    delete_line_index.append(satrt)
                if re.search(middle[1], item):
                    end = [index, 1]
                    delete_line_index.append(end)

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
                        context[index] = item.rstrip() + "|删除段之间换行|" + context[index + 1].lstrip()
                        # 删除下一段
                        del context[index + 1]
                        index = index-1
                        break

                # 如果规则长度为 1，只需要匹配当前行
                elif len(line_feed_rule) == 1:
                    if index + 1 < len(context) and re.search(current_line_rule, stripped_item):
                        # 合并当前段和下一段
                        context[index] = item.rstrip() + "|删除段之间换行|" + context[index + 1].lstrip()
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

    def Continuous_phrase_clean(self, context):
        Continuous_phrase_index = []
        Continuous_phrase_len = []

        # 记录每个片段的index和长度
        for index, item in enumerate(context):
            Continuous_phrase_index.append(index)
            Continuous_phrase_len.append(len(item.split()))

        # 检查是否有连续5个及以上长度小于20的片段
        del_indices = []  # 记录需要删除的index
        temp_indices = []  # 临时存储符合条件的index

        for i, length in enumerate(Continuous_phrase_len):
            if length < 20:
                temp_indices.append(Continuous_phrase_index[i])
            else:
                # 如果temp_indices中有连续5个及以上的片段，记录这些index
                if len(temp_indices) >= 5:
                    del_indices.extend(temp_indices)
                temp_indices = []  # 重置

        # 如果最后一段也是连续的，检查并添加到删除index
        if len(temp_indices) >= 5:
            del_indices.extend(temp_indices)

        # 根据del_indices删除context中对应的片段
        cleaned_context = [item for i, item in enumerate(context) if i not in del_indices]

        return cleaned_context


class speicalProces:
    def __init__(self):
        pass





def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    cp = clean_pattern()
    sp = speicalProces()
    context = context.split(split_token)

    # 若有需要再补充正则并调用，正则在对应的函数里补充
    context = cp.delete_page_start(context)
    context = cp.delete_page_ending(context)
    # context = cp.delete_page_middle(context)
    context = cp.more_line_feed(context,Line_feed_rules)
    context = cp.Continuous_phrase_clean(context)
    final_results = []
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
        final_results.append(item)
    for index,item in enumerate(final_results):
        print(index,item)
    context = split_token.join(final_results)

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
    context = re.sub(r'([,\.?;])(\s?[?,\.;]){1,10}',r'\1',context)
    return context




fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean3_journal-pile.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\journal-pile_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    sampled_lines = random.sample(lines, 2000)
    for items in tqdm(sampled_lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "3bed132e-40e2-403c-870b-775b4c6d122c":
        context = item["text"]
        if len(context) >2000:
            lang = item["lang"]
            title = item["title"]
            context = re.sub(r'[\*]{0,}', r'', context)
            context = re.sub(r'\xa0', r' ', context)
            context = clean_text(context, lang)
            context = post_process(context)
            # print(context, '\n-------------------')
            item["text"] = context
            item = json.dumps(item, ensure_ascii=False)
            # print(item)
            fw.write(item + "\n")
        else:
            continue
# # fw.close()


#
# # 处理单行数据的函数
# def process_line(item):
#     context = item["text"]
#     lang = item["lang"]
#     title = item["title"]
#
#     # 清洗操作
#     context = re.sub(r'[\*]{0,}', r'', context)
#     context = re.sub(r'\xa0', r' ', context)
#     context = clean_text(context, lang)
#     context = post_process(context)
#
#     # 更新 item
#     item["text"] = context
#     return json.dumps(item, ensure_ascii=False)
#
#
# # 多线程处理函数
# def process_lines_in_threads(lines, max_workers=8):
#     processed_items = []
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         # 提交所有任务
#         futures = [executor.submit(process_line, json.loads(item.strip())) for item in lines]
#
#         # 使用 tqdm 进度条追踪任务完成进度
#         for future in tqdm(as_completed(futures), total=len(futures)):
#             processed_items.append(future.result())
#
#     return processed_items
#
#
# if __name__ == "__main__":
#     # 读取文件
#     with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\journal-pile_preformat.jsonl", "r",
#               encoding="utf-8") as fs:
#         lines = fs.readlines()
#
#     # 开始多线程处理
#     processed_data = process_lines_in_threads(lines, max_workers=8)
#
#     # 将结果写入新文件
#     with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean1_journal-pile.jsonl", "w", encoding="utf-8") as fw:
#         for item in processed_data:
#             fw.write(item + "\n")
