import re


class clean_pattern:
    def __init__(self):
        pass

    # 通用英文正则
    def clean_pattern_en(self):
        pattern_en = [
            [r'(\(\s?[^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www)s?[\s\.][^\(\)]*\))',r''],  # 固定格式  带有（）的图片表格描述 附录描述 协议描述 无关网址描述

        ]

        return pattern_en

    # 通用中文正则
    def clean_pattern_zh(self):
        pattern_zh = [
            [r'([\(][^\)\(]*见(图|表)\s?\d+[^\)\(]*[\)])', r''],  # 带有
            [r'(（[^）（]*见(图|表)\s?\d+[^）（]*）)', r''],
        ]
        return pattern_zh

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