
import json
from tqdm import tqdm
import re
import random

pattern_en = [
    # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
    [r'(\(\s?([Pp]anel|[Vv]ideo|[Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:]?[^\(\)]*\))', r''],  # 1. 这些固定的词语紧贴左括号
    [r'(\(\s?[^\(\)]*)([\.;；，]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))', r'\1)'],  # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version)s?[\s\.:：][^\(\)]*\))', r'通用删除1(英):<u>\1</u>'],  # 最广泛的形式从左括号匹配到右括号
    [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r'通用删除2(英):<u>\1</u>'],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
    [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)', r'通用删除3(英):<u>\1</u>'],  # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?\s{0,}\d+[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除4(英):<u>\1</u>'],  # 特殊数字  排除可能出现的次幂情况
    [r'(.*(doi|DOI)\s?:.*)', r'通用删除5(英):<u>\1</u>'],  # 存在有DOI描述的句子
    [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(\\)?\])', r'通用删除8(英):<u>\1</u>'],  # 固定格式  带有[]的图片表格描述 附录描述 协议描述 无关网址描述
    [r'(((\\)?\[[\d\s,，\–\-—]{1,}(\\)?\]?)|((\\)?\[?[\d\s,，\–\-—]{1,}(\\)?\]))', r'通用删除6(英):<u>\1</u>'], #改动 # 带有方括号的数字引用
    [r'((\\)?\([\d\s,，\-\–—]{1,}(\\)?\))', r'通用删除7(英):<u>\1</u>'],  # 带有圆括号的数字引用

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

    # 以上为通用正则库
    # ========================================================================================
    # 以下补充对此组数据清洗的特定正则
    [r'(^[ \\]*(Correspondence：|OPEN ACCESS|E-mail|Copyright).*)', r'删除1:<u>\1</u>'],
    [r'(^#*\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*)', r''],  # 删除开头为Figure的描述
    [r'(^[ \\]*(([A-Z][a-z]+( \w+){0,2})[,，] ?){2,}([A-Z][a-z]+( \w+){0,2})[ \\]*.*)', r'删除3:<u>\1</u>'],
    # [r'(?<!of|in|to)( [\d,，\-\–—]+)(\.($| ))',  r'删除4:<u>\1</u>\2'],
    [r'([a-z])([\d,，\-\–—]+)(\.($| ))',  r'\1删除4-1:<u>\2</u>\3'],
    [r'^([\d,，\-\–— \.]+)$', r'删除5:<u>\1</u>'],
    [r'(^\d+\\?\..*\d{4}[;；：\.]\w+(\(\d+\))?[:：；]?[\w\-]+.*)', r'删除6:<u>\1</u>'],
    [r'(.*((Received|Accepted|Published) Date：|E-mail：).*)', r'删除7:<u>\1</u>'],
    [r'(^(ISSN：).*)', r'删除9:<u>\1</u>'],
    [r'(^(is properly cited|cited|\d+(：\d+)*|[\w \)]{1,5})[\.：\s]*$)', r'删除10:<u>\1</u>'],
    [r'(\.)([\d；：\. ]*(ISSN：).*)',  r'\1删除11:<u>\2</u>'],
    [r'(^We thank .*)', r'删除12:<u>\1</u>'],
    [r'(.*(work is properly|is properly cited).*)', r'删除13:<u>\1</u>'],
    [r'(^(Clinical ?Image|Clinical ?Video)$)', r'删除14:<u>\1</u>'],
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
    [r'([，。]见(图|表)\d+[^，。]*)', r'通用删除14(中):<u>\1</u>'],  # 半句到前后的标点处截至 见图/表1...
    [r'(（[^（）]*视频[^（）]*）)', r'通用删除15(中):<u>\1</u>'],  # 带有中文（）的...视频

    # 以上为通用正则库
    # ========================================================================================
    # 以下补充对此组数据清洗的特定正则


    ]

pattern_more_line_feed = [
    [r'[^|]{50,}\s?[a-zA-Z][^\.,!?|#]\s?#*$', r'^#*[\(a-z\d]'],        # 上一段非标点结尾，下一段小写开头
    [r'\s(of|in|and|or|not|the|a|any|some|for|is|are|The|A|with|&|And|their|his|her|from|on)\s?#*$'],   #  上一段结尾是A或者The 下一段一定要连上
    [r'[^|]{100,}[a-z]#*$', r'^#*(?!Table)[A-Z][^|]{100,}']
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
            [r'(^[ #]*(Abstract)[ #]*(\n|$))', 0],
            [r'(^[ #]*(Background|Introduction)[ #]*(\n|$))', 0],
            [r'(^[ #]*(Clinical ?Image|Clinical ?Video|ClinicalPresentation)[ #]*(\n|$))', 0],
        ]
        end_index = 0
        flag = False
        for end in end_pattern:
            for index, item in enumerate(context):
                if re.search(end[0], item):
                    end_index = index + end[1]
                    flag = True
            if end_index > 0:
                for i in range(0, end_index):
                    # context[i] = "通用开头删除-1:<u>{}</u>".format(context[i])
                    context[i] = ""
            if flag:
                break
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
            [r'^[ #]*(Reference|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?m ?ent|Funding|Funding Sources|Research Funding|Pseudomembranous Tracheobronchitis|Disclosure|Declaration|Permission|Institutional Review Board Statement|Consent( for Publication)?)s?[ #]*($|\n)'],
            # [r'(^1\\\. )']
            [r'(^1\\?\..*\d{4}[;；：\.]\w+(\(\d+\))?[:：；]?[\w\-]+.*)']
        ]

        for ii, start in enumerate(ending_starts):
            references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
            for index, item in enumerate(context):
                if re.search(start[0], item.strip()):
                    references_started = True
                if references_started:
                    if ii > 0:
                        context[index] = "通用结尾删除-1:<u>{}</u>".format(context[index])
                    else:
                        context[index] = ''
            if references_started:
                break
        return context

    def delete_page_ending2(self, context):
        """
        通用删除从某一段开始到文章结束
        :param context: 分割好的文本，列表结构
        :param ending_starts的每一项: 从某段开始删除开始的特征的正则形式
        :return: 列表结构的文本
        """
        # 避免重复加标签，特征最好合并为1-2条，当段保留一条，当段删除一条。
        ending_starts = [
            [r'(^[\\ #]*(OPEN ACCESS)[\\ #]*$)'],
            [r'(^[\\ #]*(Correspondence：|Citation：))']
        ]

        for ii, start in enumerate(ending_starts):
            references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
            for index, item in enumerate(context):
                if re.search(start[0], item.strip()):
                    references_started = True
                if references_started:
                    context[index] = "通用结尾删除-1:<u>{}</u>".format(context[index])

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
            [r'(^[\\ #]*(OPEN ACCESS)[\\ #]*$)', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})', 0],
            [r'(^[\\ #]*(Correspondence：))', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})|(^\d{1,2}\\?\.)', 0],
            [r'(^[\\ #]*(Citation：))', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})|(^\d{1,2}\\?\.)', 0],

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


class speicalProces:
    def __init__(self):
        pass

    def move_duan(self, context):

        context = re.sub(r'([a-z，\-\d])(\n\n)([a-z])',  r'\1删除1换行\3', context)
        context = re.sub(r'([^|\n]{100,})(\n\n)( *[a-z])', r'\1删除2换行\3', context)
        context = re.sub(r'([a-z，\d])(\n\n((Supplementary )?Table|\|) [\W\w]*?)(\n\n)(([a-z\(]).*)', r'\1删除表格换行\6\2', context)
        context = re.sub(r'([\d])(\n\n((Supplementary )?Table|\|) [\W\w]*?)(\n\n)((±\d).*)', r'\1删除表格换行\6\2', context)

        return context

def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    cp = clean_pattern()
    sp = speicalProces()
    context = re.sub(r'([\u4e00-\u9fff]+ )', r'删除8:<u>\1</u>', context)

    context = context.split(split_token)
    # 若有需要再补充正则并调用，正则在对应的函数里补充
    context = cp.delete_page_start(context)
    context = cp.delete_page_middle(context)
    context = cp.delete_page_ending(context)
    context = cp.delete_page_ending2(context)

    context = split_token.join(context)
    context = sp.move_duan(context)
    context = context.split(split_token)

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

    final_results = cp.more_line_feed(final_results, pattern_more_line_feed)
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
    context = re.sub(r'([,\.?])(\s?[?,\.]){1,5}',r'\1',context)
    return context




fw = open(r"C:/Program Files/lk/projects/pdf/accr/accr_preformat_clean3.jsonl", "w", encoding="utf-8")
with open(r"C:/Program Files/lk/projects/pdf/accr/accr_preformat.jsonl", "r", encoding="utf-8") as fs:
    number = 84
    lines = fs.readlines()#[number-1:number]
    for items in tqdm(lines):
        item = json.loads(items.strip())
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        # exit_flag = False
        # wuguan = ["Hidden Tongue", "Mrs. F.I， 48 years old", "A 24 year old male developed sudden"]
        # for txt in wuguan:
        #     if txt in context:
        #         # context = "(本页删除)本页文本质量太差:\n" + context
        #         exit_flag = True
        #         break
        # if exit_flag:
        #     continue
        context = re.sub(r'\xa0', r' ', context)
        context = re.sub(r'([\*\_\\]+)', r'', context)

        context = clean_text(context, lang)
        context = post_process(context)
        print(context, "\n--------------------------------------------------")
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
fw.close()