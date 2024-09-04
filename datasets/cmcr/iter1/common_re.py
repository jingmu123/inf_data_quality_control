import re


class clean_pattern:
    def __init__(self):
        pass

    # 通用英文正则
    def clean_pattern_en(self):
        pattern_en = [
            # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
            [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|See|For more|panel|http|www|NCT\d+|NO\.|version)s?[\s\.:][^\(\)]*\))',r''],   # 1. 这些固定的词语紧贴左括号
            [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))',r'\1)'],   # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
            [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version)s?[\s\.:][^\(\)]*\))',r'通用删除1(英):<u>\1</u>'], # 最广泛的形式从左括号匹配到右括号

            [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r'通用删除2(英):<u>\1</u>'],     # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
            [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
            [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)',r'通用删除3(英):<u>\1</u>'], # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
            [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[a-z\d+\s\-\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除4(英):<u>\1</u>'],     # 特殊数字  排除可能出现的次幂情况
            [r'(.*(doi|DOI)\s?:.*)', r'通用删除5(英):<u>\1</u>'],  # 存在有DOI描述的句子
            [r'((\\)?\[[\d\s,\-\–—]{1,}(\\)?\])', r'通用删除6(英):<u>\1</u>'],  # 带有方括号的数字引用
            [r'((\\)?\([\d\s,\-\–—]{1,}(\\)?\))', r'通用删除7(英):<u>\1</u>'],  # 带有圆括号的数字引用
            [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(\\)?\])',r'通用删除8(英):<u>\1</u>'],   # 固定格式  带有[]的图片表格描述 附录描述 协议描述 无关网址描述
            [r'(^Full size.*)', r'通用删除9(英):<u>\1</u>'],  # Full size image/table 原文这里应该是一个图/表没识别出图形
            [r'(\([^\(\)]*(arrow|←|→)[^\(\)]\))', r''],  # ...箭头 描述图里面不同颜色的箭头

        ]
        return pattern_en

    # 通用中文正则
    def clean_pattern_zh(self):
        pattern_zh = [
            [r'([\(][^\)\(]*见?(图|表|详见)\s?\d+[^\)\(]*[\)])', r'通用删除1(中):<u>\1</u>'],  # 带有英文括号的
            [r'(（[^）（]*见?(图|表|详见)\s?\d+[^）（]*）)', r'通用删除2(中):<u>\1</u>'],
            [r'(致谢.*)',r'通用删除3(中):<u>\1</u>'],
            [r'(^[\*#]{0,4}点击查看.*)',r'通用删除4(中):<u>\1</u>'],     # 点击查看...
            # [r'(^[\*#]{0,4}(图|表)\s?\d+$)',r'通用删除5(中):<u>\1</u>'],   # 这一段中只有一个 表\d+
            [r'(.*利益冲突.*)',r'通用删除6(中):<u>\1</u>'],    # 文章末利益冲突
            [r'(^[\*#]{0,4}详见.*)',r'通用删除7(中):<u>\1</u>'],    # 详见...
            [r'(^[\*#]{0,4}阅读更多.*)',r'通用删除8(中):<u>\1</u>'],  # 阅读更多...
            [r'((\\)?\[[\d\s,\-\–—]{1,}(\\)?\])', r'通用删除9(中):<u>\1</u>'],  # 带有方括号的数字引用
            # [r'((\\)?\([\d\s,\-\–—]{1,}(\\)?\))', r'通用删除10(中):<u>\1</u>'],  # 带有圆括号的数字引用
            [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?[a-z\d+\s\-\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除11(中):<u>\1</u>'],  # 特殊数字  排除可能出现的次幂情况
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
                context[i] = "通用开头删除-1:<u>{}</u>".format(context[i])
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
                item = "通用结尾删除-1:<u>{}</u>".format(item)
                # item = ''
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
                context[i] = "通用间距删除-1:<u>{}</u>".format(context[i])
                # context[i] = ""
        return context