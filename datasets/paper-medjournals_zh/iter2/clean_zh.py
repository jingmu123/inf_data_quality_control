# -*- coding: utf-8 -*-
import json
from tqdm import tqdm
import re
import random

pattern_en = [
    # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
    [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:]?[^\(\)]*\))', r''],  # 1. 这些固定的词语紧贴左括号
    [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))', r'\1)'],  # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束

    [r'((\([^\(\)]*)([,;] ([Ff]igs?(?:ure)?|F\s?IGS?(?:URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version)s?[\s\.:][^\(\)]*\)))',r'\2)删除11：<u>\3</u>'],
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]s?\.|Participant \d+|Provider \d+|software|version)s?[\s\.:][^\(\)]*\))', r'通用删除1(英):<u>\1</u>'],  # 最广泛的形式从左括号匹配到右括号
    [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r'通用删除2(英):<u>\1</u>'],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
    [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)', r'通用删除3(英):<u>\1</u>'],  # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?\s{0,}\d+[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除4(英):<u>\1</u>'],  # 特殊数字  排除可能出现的次幂情况
    [r'(.*(doi|DOI)\s?:.*)', r'通用删除5(英):<u>\1</u>'],  # 存在有DOI描述的句子
    [r'((\\)?\[[\d\s,\\，\–\-—]{1,}(\\)?\])', r'通用删除6(英):<u>\1</u>'],  # 带有方括号的数字引用
    [r'((\\)?\([\d\s,\\，\-\–—]{1,}(\\)?\))', r'通用删除7(英):<u>\1</u>'],  # 带有圆括号的数字引用

    [r'(((?:\\)?\[\s?[^\[\]]*)([,;] ([Ff]igs?(?:ure)?|F\s?IGS?(?:URE)?|Tables \d and|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(?:\\)?\]))',r'\2]删除11：<u>\3</u>'],
    [r'(((?:\\)?\[\s?[^\[\]]*)([,;] ([Ff]igs?(?:ure)?|F\s?IGS?(?:URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(?:\\)?\]))',r'\2]删除11：<u>\3</u>'],
    [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(\\)?\])', r'通用删除8(英):<u>\1</u>'],  # 固定格式  带有[]的图片表格描述 附录描述 协议描述 无关网址描述.
    [r'(^Full size.*)', r'通用删除9(英):<u>\1</u>'],  # Full size image/table 原文这里应该是一个图/表没识别出图形
    [r'(\([^\(\)]*(arrow|←|→)[^\(\)]\))', r''],  # ...箭头 描述图里面不同颜色的箭头

    # 9.4继续添加
    [r'(^Full size.*)', r'通用删除10(英):<u>\1</u>'],  # Full size image/table 原文这里应该是一个图/表没识别出图形
    [r'(\([pP]\.?\d+[^\(\)]*\))', r'通用删除11(英):<u>\1</u>'],  # 带有括号的([Pp]. ...)第几页
    [r'(\([^\(\)]*Additional file[^\(\)]*\))', r''],  # 附加文件带括号
    [r'([\*#]{0,4}(?:Please see *)?Additional file.*)', r'通用删除12(英):<u>\1</u>'],  # 附加文件
    [r'(^Download\s.*)', r'通用删除13(英):<u>\1</u>'],  # 段落开头下载 ...
    [r'^.{0,3}(Editor.s note|To learn more about).*', r'通用删除14(英):<u>\1</u>'],  # 从段落头开始 编辑信息 更多信息
    [r'(^(You can find more|About this video).*)', r'通用删除15(英):<u>\1</u>'],  # 段落开头 你可以找到更多/关于本视频

    #09.23继续添加
    [r'(^#*\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*)', r'通用删除16(英):<u>\1</u>'],  # 删除开头为Figure的描述

    # 以上为通用正则库
    # ========================================================================================
    # 以下补充对此组数据清洗的特定正则
    [r'(\D[\.]\s*)(\d{1,3}(?:[\s,\–\-— ]+\d+){0,20})($|\n| *[A-Z][A-Za-z])',r'\1删除4：<u>\2</u>\3'],
    # [r'([^N]\D[\.]\s*)(\d{1,3}(?:[\s,\–\-— ]+\d+){0,20})($|\n| *[A-Z][A-Za-z])', r'\1删除4：<u>\2</u>\3'],

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
    [r'((\\)?[\[［][\d\s,\-\–—]{1,}(\\)?[\]］])', r'通用删除9(中):<u>\1</u>'],  # 带有方括号的数字引用
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

pattern_zh_list=[
    [r'(\n|^)((?:资助|利益[\u4E00-\u9FFF]{0,2}|伦理[\u4E00-\u9FFF]{0,2}|[\u4E00-\u9FFF]{0,2}作者[\u4E00-\u9FFF]{0,5}|来源[\u4E00-\u9FFF]{0,5}|基金[\u4E00-\u9FFF]{0,3}|知情同意|开放获取|患者[\u4E00-\u9FFF]{0,4}|透明度|公众传播|数据共享|开发获取)[(（][A-Za-z ]+[）)][:：].*)',r'\1删除1：<u>\2</u>'],
    # [r'(\n|^)(—*(?:原文|分类号|志谢|(?:基金)?资助[(（]Funding[）)]|透明度[(（]Transparency[）)]|关于作者[(（]Contributors[）)]|来源与同行评议[(（]Provenance and peer review[）)])[:：].+)',r'\1删除1：<u>\2</u>'],
    [r'([(（]\D[^\n()（）=]*[^0-9=\.\-\-：:]\d{4}[:：;；,，年][^\n()（）%]*[）)])',r'删除2：<u>\1</u>'],
    [r'(?:\n|^)((?:(?:(?:This|The) [a-z]{2,}( [a-z]{2,})? (?:is|was) (?:supported(?: primarily)?|funded|approved|founded|conducted) (?:by|with).*)|Nil\.)(?:\n*There are no conflicts of interest\.)?)',r'\n删除3：<u>\1</u>'],

    [r'(?:\n|^)((?:利益(?:冲突|竞争)\(Competing interests\)[:：].*)(?:\n[^\n0-9][^\n.．].*)+)',r'\n删除5：<u>\1</u>'],
    [r'(\n|\(|（)((?:https?[：:][/／]{2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[-.．／/][a-zA-Z0-9@／/_]{2,})+)(\n|$|\)|）)',r'删除6：<u>\1\2\3</u>'],
    [r'(\([\u4E00-\u9FFF]+|（[\u4E00-\u9FFF]+)((?:https?[：:][/／]{2}(?:www[.．])?|www[.．])?[a-zA-Z0-9@／/-]+(?:[.．][a-zA-Z0-9@／/-]{2,})*[.．](?:com|cn|org))(\)|）)',r'删除6：<u>\1\2\3</u>'],

    [r'(?:\n|^)(The authors thank.*|Not applicable|The authors declare that.*|Please contact author for data requests\.|None\.|There are no conflicts of interest\.|There is no funding for this review\.|The authors contributed equally to.*|The present study was supported by.*|The patients had signed.*|All the authors reported no conflict.*|Peer review under responsibility of.*|The datasets supporting the conclusions.*|This paper is a review article.*|All authors .*|All data generated or analyzed.*)',r'\n删除7：<u>\1</u>'],
    [r'(?:\n|^)(YZ:.*|The authors acknowledge.*|(?:All )?[Tt]he data supporting.*|The online version contains.*|We are very grateful to.*|The authors certify that.*|No funding.|We thank.*|All clinical data are stored by.*|Formal consent has been obtained.*|The hospital ethics committee approved.*|Data source:.*|The authors?.*)',r'\n删除7：<u>\1</u>'],

    [r'(\.)( *Chin Med J \d{4}; *\d+\(\d+\): *\d+-\d+)',r'\1删除8：<u>\2</u>'],
    [r'(\n|^)(Supplementary (?:data|information).*)',r'\1删除9：<u>\2</u>'],
    [r'(,)( *(?:https?[：:][/／]{2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[.．／/][a-zA-Z0-9@／/_]{2,})+)(\.)',r'删除10：<u>\1\2</u>\3'],
    [r'(\n|^|\.|。)([^\n\u4E00-\u9FFF]*[Dd][Oo][Ii][:：.].*)',r'\1删除11：<u>\2</u>'],
    [r'(\n|^|\.|。)([\–\-\—]*(?:原文出?处?[:：]|摘译?自|N Engl|分类号[:：]|志谢[:：]?|基金[\u4E00-\u9FFF]{0,5}[:：]|[\u4E00-\u9FFF]{0,2}作者[:：]|[\u4E00-\u9FFF]{0,3}主持者[:：]|起草人[:：]).*)',r'\1删除12：<u>\2</u>'],
    [r'(\n|^)((?:[\u4E00-\u9FFF]{0,3}(?:参考文?献?|贡献者)).{0,20}(?:参?见|经)(?:网站)? *(?:www[.．])? *[A-Za-z]+[.．]com.*)',r'\1删除13：<u>\2</u>'],

    [r'([(（][^\n()（）]*[Dd][Oo][Ii][:：][^\n()（）]*[）)])',r'删除14：<u>\1</u>'],

    #个例
    [r'(?:\n|^)(希望广大读者继续关注本刊，提出宝贵的意见和建议，积极提供文稿，本刊将择优刊登于相应栏目。|BA Bahia, CE MG Minas Gerais, PR Paraná, RJ Rio de Janeiro, SC Santa Catarina, SP São Paulo|Authors would to thank.*|The patient consented.*|The use of animals in this study.*)',r'\n删除个例：<u>\1</u>']
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
            [r'^[#\*]{0,4}\s?(References?：?|Funding( Sources| Statement| and Disclosure)?|Polls on Public|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?ment|Conflicts? of [Ii]nterest|Source of (Support|Funding))s?[#\*]{0,4}\s{0,}($|\n)'],

        ]

        for start in ending_starts:
            references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
            for index, item in enumerate(context):
                if re.search(start[0], item.strip()):
                    references_started = True
                if references_started:
                    context[index] = "通用结尾删除-1:<u>{}</u>".format(context[index])
                    # context[index] = ''
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


class speicalProces:
    def __init__(self):
        pass
    def rm_lid_piece(self, context):
        end_index=len(context)
        same_lis=[]
        for index,part in enumerate(context):
            if index+1==end_index:
                break

            # print(part)
            # print(1, part, bool(re.sub(r'\s', '', part)))
            if not re.sub(r'\s','',part) or not re.sub(r'\s','',context[index+1]):
                continue
            if part==context[index+1]:
                context[index+1]='删除重复语句1：<u>'+context[index+1]+'</u>'
                same_lis.append(part)
            elif part in context[index+1] or context[index+1] in part:
                context[index + 1] = '删除重复语句3：<u>' + context[index + 1] + '</u>'


        return context

    def short_paragraphs(self,context):
        Key_words=['特此说明','欢迎作者与读者使用']
        if len(context) == 1:
            for word in Key_words:
                if word in context[0]:
                    context[0]='删除整段：'+context[0]

        else:
            return context
        return context







def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    cp = clean_pattern()
    sp = speicalProces()

    pattern_list = pattern_zh_list
    for pattern_item in pattern_list:
        context = re.sub(pattern_item[0], pattern_item[1], context)


    context = context.split(split_token)
    context=sp.short_paragraphs(context)
    context=sp.rm_lid_piece(context)
    # print(context)



    # 若有需要再补充正则并调用，正则在对应的函数里补充
    context = cp.delete_page_start(context)
    context = cp.delete_page_ending(context)
    # context = cp.delete_page_middle(context)

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
        if not re.sub(r'\s', '', item):
            final_results.append(item)
            continue
        if item in final_results :
            final_results.append(f'删除重复语句2：<u>{item}</u>')

        else:
            final_results.append(item)

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


#e4066c13-b3de-47c1-94dc-c31f5e4906ad
fw = open(r"C:\Users\Administrator\PycharmProjects\untitled\paper-medjournals_zh\reclean2_paper-medjournals_zh.jsonl", "w", encoding="utf-8")
with open(r"C:\Users\Administrator\PycharmProjects\untitled\paper-medjournals_zh\paper-medjournals_zh_preformat.jsonl", "r", encoding="utf-8") as fs:
# with open(r"C:\Users\Administrator\PycharmProjects\untitled\paper-medjournals_zh\test.jsonl", "r", encoding="utf-8") as fs:

    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "5a9815c6-c389-410a-884d-86bd79e6dc56":
        context = item["text"]
        print(item["seq_id"])
        if re.search(r'如下.{0,3}$', context):
            continue
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0', r' ', context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context, '\n-------------------')
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
fw.close()