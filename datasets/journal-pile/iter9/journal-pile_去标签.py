import json
from tqdm import tqdm
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

pattern_en = [
    [r'(^!\[.*(\n.*){0,})', r''],  # 带有![ 这句是图片的描述!是因为图片加载不过来
    [r'(^\[\^\d+\][^$]*)', r''],  # 句子开头为[^\d] 一般在句子结尾无关文本 必须放在处理带有[]特征的前面先删除掉
    [r'([A-Z])(\[)([a-zA-Z][^\]]*)(\])', r'\1\3'],
    [r'\([^\(\)]{0,20}([,\.;\s]{0,}(and\s+)?\[[^\[\]]{1,50}\]\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}){1,}[^\(\)]{0,20}\)', r''],
    # 固定删除格式 [...](...){...} 外面可带圆括号或方括号，括号一定是同一种要带都带,要不就都不带
    [r'\[[^\[\]]{0,20}([,\.;\s]{0,}(and\s+)?\[[^\[\]]{1,50}\]\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}){1,}[^\[\]]{0,20}\]', r''],
    # 固定删除格式 [...](...){...} 外面可带圆括号或方括号
    [r'(\[[^\[\]]{1,50}\])?\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}', r''],  # 固定删除格式 [...](...){...}不带括号
    [r'((\^)?(\\)?\([^\[]{,50}([,;\.\s]{0,}\[[^\[\]]*(@|#|Supplementary material|Reporting Summary|SUMMARY|data not shown|www|[Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee)[^\[\]]*\]){1,}[^\]]{,50}(\\)?\)(\^)?)',r''],  # 带有圆括号 里面有一个特殊符号@、#
    [r'((\^)?(\\)?\[[^\[]{,50}([,;\.\s]{0,}\[[^\[\]]*(@|#|Supplementary material|Reporting Summary|SUMMARY|data not shown|www|[Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee)[^\[\]]*\]){1,}[^\]]{,50}(\\)?\](\^)?)',r''],  # 带有方括号 里面有一个特殊符号@、#
    [r'(\^)?((\\)?[\[\(])?([,;\.\s]{0,}\[[^\[\]]*(@|#|Supplementary material|Reporting Summary|SUMMARY|data not shown||[Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee)[^\[\]]*\]){1,}((\\)?[\]\)])?(\^)?',r''],  # 带有方括号 里面有一个特殊符号@、#
    [r'\\\n', r''],
    [r'([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:\d][^\(\)]*)(\))', r')'],
    # （）内出现(dose---F~(4,\ 52)~ = 5.312, p = 0.001; group × dose \[F~(4,\ 52)~ = 2.539 p = 0.051\]; Fig. [2a])，删除;后面出现的Table、Fig...到后面的右括号
    [r'(^The following are available online.*)', r''],  # 一下内容可在...找到，一版后面接的是网址
    [r'(.*These authors contributed equally.*)', r''],  # 固定表述
    [r'(\[\^\d+\])', r''],  # 无关数字
    [r'(\(:\s?[①②③④⑤⑥⑦⑧\-⑨⑩\s,\.]{1,}\))', r''],
    [r'([\(][^\)]*([hH]ttps?|www|WWW|HTTPS?|\.ua\.|\.edu)[^\(]*[\)])', r''],  # 带有()\<>的非常规网址或网址路径
    [r'([<][^>]*([hH]ttps?|www|WWW|HTTPS?|\.ua\.|\.edu)[^<]*[>])', r''],  # 带有()\<>的非常规网址或网址路径
    [r'([^-]\s?)(\([\dA-Z]{1,10}-([^-\.,~\s]{1,10}-){1,}[^-\.,\s]{1,10}\))([^-]\s?)', r'\1\4'],  # 删除类似于编号 (IJCCM-21-40-g003)
    [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.|Supplementary [mM]aterial|video|model)s?[\s\.:\d][^\(\)]*\))', r''],  # 1. 这些固定的词语紧贴左括号
    [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www|Supplementary [mM]aterial)s?[\s\.:\d][^\(\)]*)(\))', r'\1)'],  # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version|Appendix|Supplementary [mM]aterial)s?[\s\.:\d][^\(\)]*\))', r''],  # 最广泛的形式从左括号匹配到右括号
    [r'(\([^\(\)]*\s?et[\s\xa0]{1,3}al[^\)\(]*\))', r''],  # 带有括号, et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r''],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'((\\)?\[[\d\s,\\，\–\-—]{1,}(\\)?\])', r''],  # 带有方括号的数字引用
    [r'(\([^\(\)]*Additional file[^\(\)]*\))', r''],  # 附加文件带括号
    [r'(^[\*#]{0,4}Additional file.*)', r''],  # 附加文件
    [r'(^#*\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*)', r''],  # 删除开头为Figure的描述
    [r'(\([^\(\)]*(pone)s?[\d\s\.:][^\(\)]*\))', r''],  # 带有圆括号 里面有特征pone
    [r'(\{[^\{\}]*\})', r''],  # 带有花括号 {}里面所有
    [r'([!\.]{0,}(\\)?[\(\[\{][,\s;-]{0,}(\\)?[\)\]\}])', r''],  # 前面可以有一个！带有各种括号的里面为空
    [r'^(We|I) thank.*', r''],  # 一句固定格式的句子  感谢...
    [r'^jcm-08-01366.*', r''],
    [r'(^See\s.*)', r''],  # See在句子开头  见...
    [r'(\(ABSTRACT[^\(\)]*\))', r''],  # 带有圆括号的ABSTRACT摘要
    [r'(References:.*)', r''],  # 句子结尾处出现References:...  从reference开始删除
    [r'(.*no conflict of interests.*)', r''],  # ...没有利益冲突，区别于文章尾的多段删除，这里只需要删除这一段
    [r'(^(The authors?|We are|Authors?).*(thanks?|grateful|acknowledge|indebted|appreciates?|gratitude).*)', r''],  # 作者感谢...的支持之类的描述
    [r'(^(Informed )?[cC]onsent:.*)', r''],  # 知情同意、同意 ...
    [r'^(\([A-Z]*\)|[#]{1,}|Click here for additional data file.)$', r''],  # 单行只有(A-Z)、多个#、点击查看文件
    [r'(.{20,}Supporting information.*)', r''],
    [r'(\(\[[^\[\(\)\]]*\]\))', r''],  # 删除前面删除剩余的一些([...])的表述

    [r'(^10\.\d{4}[^\d].*$)', r''],  # 单行 10.1371/journal.pone.0035893.t001  类型的表述
    # [r'([^\d])(\s?(\$){1,}\s?)', r'\1删除36:<u>\2</u>'],  # 存在不是在数字后面的$符号  可匹配多个
    [r'(.*(conflicts? of|competing) interest[^$]*)', r''],  # ...利益冲突... 一般在句中只能针对这句去删除
    [r'(^(This|The|These)\s.{0,50} (were|was|is) .{0,15}(supported|funded|carried|approved|financed)[^$]*)', r''],  # 这项研究得到了...的支持
    [r'(^Paper extracted from[^$]*)', r''],  # 论文摘自
    [r'(^Assistance with the study[^$]*)',r''],  # 协助学习
    [r'(\.)((Table|Fig|Figure|Video)(\.)?\s?\d[A-Z].*)', r'\.'],  # 处于句子的句末的Table/Fig描述
    [r'(^This work has been.*$)',r''],   # 固定表述  这项工作...
    [r'(DOI:\()?10\.\d{4}/.*(Table|Fig|Figure|Video)\.?\s?\d\.[A-Z].*',r''],
    [r'(.*[^\d]10\.\d{4}[^\d].*$)',r''],  # 固定表述  单独一行 10.7717...

    [r'(^(E-mail|Twitter|Published|iThenticate screening|Financial source|Clinical Trial number \(ReBEC\)|Acknowledgments|Citation):[.\n]*)',r''],   # E-mail:开头的句子
    [r'(^The data underlying[.\n]*)',r''],   # 基础的数据...  一般都在第一句
    [r'(.*(equally to this work|contributed equally).*)',r''],    #  ...对此贡献对等
    [r'(.*All authors (participated|have read).*)',r''],   #All authors participated 所有的作者都参加了...
    [r'([^_])((Table|Fig)(\.)?\s?\d\s?$)',r'\1'],
    [r'(.*(This research received no external funding|revised the manuscript|[Pp]ublished online:|All authors read and approved the final manuscript).*)',r''],   # 这项研究没有得到外部资助

    [r'Additional file.*',r''],       # 上面有处理附加文件的句子 Additional file是句子开头   还有出现在句中的情况，此次处理位于句中但句尾进行删除
    [r'(\\)?\[[\s,\.–-]{0,}(\\)?\]', r''],  # 空\[\]  或者中间有个空格或标点
    [r'(\([\s,\.-]{0,5}\))', r''],  # 空()
    [r'(^Appendix\s?.*(\n.*)?)',r''],   # 附录 。。。
    [r'(^All calculations.*)',r''],
    [r'(.*(the|a) manuscript.*)',r''],   # 。。。手稿 一般在末尾段落
    # [r'(.*[A-Z]\.[A-Z]\.[A-Z]\..*)',r'删除56:<u>\1</u>'],
    [r'(.*version to be published.*)',r''], # ...版本
    [r'(\(\s?(video)\s?\))',r''],    # 括号 括号里面只有一个单词固定单词
    [r'(\(\s?(see|Fig|[Ff]igure|Table)[^\)]*$)',r''],    # 只有左半边括号 图片，表...
    [r'\\',r''],   # 多余符号 \\

    [r'(^(Presented at|Cite this article as|Sample Availability)\s?:.*$)',r''],       #进宫朝见...？
    [r'^((The )?Supplementary [Ii]nformation|Source code|Financing|To cite this article|None declared).*',r''],   #补充信息开头整句话
    [r'.*([Aa]uthors have equally|Patient consent)[.\n]*',r''],        # 作者的贡献...
    [r'(^We would like to (express special thanks|acknowledge).*$)',r''],   # 我们要感谢。。。
    [r'(^.*(A|a) sincere thank you.*)',r''],
    [r'^(The views expressed in this article|Special thanks are extended|Supplementary Data online at|This work was part of the|A comment to this article is available online at).*',r''],  # 本文表达的观点
    [r'.*[cC]onceived and designed the experiments.*',r''],
    [r'^(SUPPLEMENTARY FIGURES|Supplemental Material|Supplemental Information).*(\n.*)?',r''],
    [r'^\s?(Raw data|Dataset)\s?$',r''],
    [r'(.*([A-Z]\.){2,}\s?(and\s?([A-Z]\.){2,}\s?){1,}.*)',r''],
    [r'^[\.?!]{1,}(\n|$)',r''],      # 单行只有一个标点

    [r'[^\.]*\.gov[^\d]*NCT\d+\.?',r''],
]

pattern_zh = [
    [r'([\(][^\)\(]*见?(图|表|详见)\s?\d+[^\)\(]*[\)])', r''],  # 带有英文括号的
    [r'(（[^）（]*见?(图|表|详见)\s?\d+[^）（]*）)', r''],
    [r'(致谢.*)', r''],
    [r'(^[\*#]{0,4}点击查看.*)', r''],  # 点击查看...
    # [r'(^[\*#]{0,4}(图|表)\s?\d+$)',r'通用删除5(中):<u>\1</u>'],   # 这一段中只有一个 表\d+
    [r'(.*利益冲突.*)', r''],  # 文章末利益冲突
    [r'(^[\*#]{0,4}详见.*)', r''],  # 详见...
    [r'(^[\*#]{0,4}阅读更多.*)', r''],  # 阅读更多...
    [r'((\\)?\[[\d\s,\-\–—]{1,}(\\)?\])', r''],  # 带有方括号的数字引用
    # [r'((\\)?\([\d\s,\-\–—]{1,}(\\)?\))', r'通用删除10(中):<u>\1</u>'],  # 带有圆括号的数字引用
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r''],
    # 特殊数字  排除可能出现的次幂情况

    # 9.4继续添加
    [r'(（\s{0,}）)', r''],  # 空括号里面什么都没有
    [r'(（详见[^（）]*）)', r''],  # 中文括号详见...
    [r'([，。]见(图|表)[\d\s,，\-\–—]+[^，。]*)', r''],  # 半句到前后的标点处截至 见图/表1...
    [r'(（[^（）]*视频[^（）]*）)', r''],  # 带有中文（）的...视频

    # 以上为通用正则库
    # ========================================================================================
    # 以下补充对此组数据清洗的特定正则

]
Line_feed_rules = [
    [r'^.{1,10}[^\.,!]$', r'^:']
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
            [r'(^[#\s]*(Abstract|ABSTRACT|INTRODUCTION)：?\s.{0,50}(\n|$))', 0],
            [r'(^[#\s]*(1\.\s?)?(Introduction)：?\s.{0,50}(\n|$))', 0],

        ]
        end_index = 0
        for end in end_pattern:
            for index, item in enumerate(context):
                if re.search(end[0], item, re.I):
                    end_index = index + end[1]
            if end_index > 0:
                for i in range(0, end_index):
                    # context[i] = "通用开头删除-1:<u>{}</u>".format(context[i])
                    context[i] = ""
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
            [r'^.{0,10}(Competing (of\s)?[Ii]nterest|Funding|Source of Support|Supporting information|Availability of data and materials|Financial support( and sponsorship)?|conflict of interest|Acknowledgement|Reporting summary|Disclosure|Supplementary information|Disclosure statement|Author contribution|Conflict of interest statement|Ethics|Conflicts of Interest|Data [Aa]vailability( [Ss]tatement)?|Data sharing statement|Additional Information|Online supplemental material|Not applicable|Ethical approval|Supplementary Material|Ethical aspects|Declared none|Acknowledgment|Supplementary data|Contributor|SUPPLEMENTAL DATA|Data accessibility)s?.{0,15}(\n|$)'],# 在句子开头处匹配到并且后面没有什么其他内容
            [r'^(The author has served|There is no funding|We are indebted to|The online version of this article|Under the direction of the authors|The work was supported|Thanks to all the|This article is distributed|We are grateful to|The work performed at|Financial support and sponsorship|JX and SZ contributed equally to this article|SUPPLEMENTARY MATERIALS TABLE|SUPPLEMENTARY DATA|Supporting Information|The authors are grateful|Financial support and sponsorship|Statement of Ethics|Manuscript source|CONFLICT OF INTEREST|This article belongs to|Electronic supplementary material|Author.{0,5} contributions?|Thanks go to|This work was funded|Financial support|We would like to thank|CONFLICTS OF INTEREST|We gratefully acknowledge|Additional Information and Declarations|Funding:?|Declaration of patient consent|Enhanced content|Publisher(\'s)? note|No funding|The authors? declare|Contributors:|Consent|The following information|Source of Support:|Supplementary Material|Sources of Funding|References and recommended reading|The Supporting Information is|All authors contributed to the writing|Ethical clearance|Declaration of conflicting interest|We wish to thank|Declaration of Competing Interest|Trial status|Enhanced Digital Features|Authors\' declaration of interests|Shareable PDF|The author confirms that|Provenance and peer review|Availability of supporting data|Support for this research)'],# 匹配到开头就行
            [r'(No competing financial interests exist|statement:|There were no sources of funding for the study|Supplementary Data online at)']  # 匹配到就行
        ]

        for start in ending_starts:
            references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
            for index, item in enumerate(context):
                if re.search(start[0], item.strip(), re.I):
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
                    if index + 1 < len(context) and re.search(current_line_rule, stripped_item) and re.search(
                            next_line_rule, context[index + 1].strip()):
                        # 合并当前段和下一段
                        context[index] = item.rstrip() + "" + context[index + 1].lstrip()
                        # 删除下一段
                        del context[index + 1]
                        index = index - 1
                        break

                # 如果规则长度为 1，只需要匹配当前行
                elif len(line_feed_rule) == 1:
                    if index + 1 < len(context) and re.search(current_line_rule, stripped_item):
                        # 合并当前段和下一段
                        context[index] = item.rstrip() + "" + context[index + 1].lstrip()
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
    context = cp.more_line_feed(context, Line_feed_rules)
    context = cp.Continuous_phrase_clean(context)
    # for index,item in enumerate(context):
    #     print(index,item)

    import re

    final_results = []
    skip_next = False  # 用于标记是否跳过下一个item

    for i, item in enumerate(context):
        if skip_next:
            skip_next = False  # 跳过当前项并重置标志
            continue

        # 1. 正则处理逻辑
        if lang == "en":
            # 检查是否匹配 'Ethics Statement'
            if re.search(r'^(Ethics Statement|Role of the funding source|Code availability|PROM Questionnaire|Sample Availability|Funding Information)[.\n]*', item):
                final_results.append("")  # 当前项置为空字符串
                if i + 1 < len(context):  # 确保下一个项存在
                    final_results.append("")  # 下一个项也置为空字符串
                    skip_next = True  # 标记跳过下一个项
                continue  # 跳过剩余替换逻辑

            # 对英文模式的其他pattern进行替换
            for src, tgt in pattern_en:
                item = re.sub(src, tgt, item)
        else:
            # 对中文模式的pattern进行替换
            for src, tgt in pattern_zh:
                item = re.sub(src, tgt, item)

        final_results.append(item)  # 将处理后的item添加到结果中

    for index, item in enumerate(final_results):
        print(index, item)
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
    context = re.sub(r'[。，](\s?[。，：；]){1,5}', r'。', context)
    context = re.sub(r'([,\.?;])(\s?[?,\.;]){1,10}', r'\1', context)
    return context


fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean8B_journal-pile.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\journal-pile_preformat.jsonl", "r",
          encoding="utf-8") as fs:
    lines = fs.readlines()
    sampled_lines = random.sample(lines, 3000)
    for items in tqdm(sampled_lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "dc1bd8f6-0533-4883-bc8b-41a22854e910":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'[\*#]{0,}', r'', context)
        context = re.sub(r'\xa0', r' ', context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context, '\n-------------------')
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")

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
