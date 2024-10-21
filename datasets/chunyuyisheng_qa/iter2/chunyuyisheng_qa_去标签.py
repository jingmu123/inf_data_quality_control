
import json
from tqdm import tqdm
import re
import random

pattern_en = [


    ]


pattern_zh = [
    [r'^(病人|医生)：[🐶😍😟✌😷😪😐🙄👃🙊🏸🙄🐷🤗🌝🙂😙😋😌😀🚶🤭🤣🐠😴👋😳😃💔🐑😯🔥😔😱🌹😎❤💪🍼㊗️㊗😞👀👌🏻😜😨🏻💝🙏￼💊👍😁😂😄😛😊👌😓😭☺😘😢🍀]{1,}$', r''],  # 单行只有表情包
    [r'[🐶😍😟✌😷😪😐🙄👃🙊🏸🙄🐷🤗🙂🌝😙😋😌😀🚶🤭🤣🐠😴👋😳😃💔🐑😯🔥😔😱🌹😎❤💪🍼㊗️㊗😞👀👌🏻😜😨🏻💝🙏￼💊👍😁😊👌😄😓😂☺😘😛😢😭🍀]{1,}',r''], #表情包
    [r'^(医生：.*(注册|二维码|评价|自动回复|好评|主页|加我|https?|关注我).*)', r''],   # 匹配一个句子又‘医生：’开头句子中有'评价'
    [r'(.*语音文件.*)',r''],    # 语音对话
    [r'(^(病人|医生)：\s{0,}$)',r''],   # 空行 只有前面的人
    [r'(_\(:з\)∠\)_，麻蛋了)',r''],   #
    [r'（(\s?[？。，：；]){1,5}）',r''], # 空括号

    [r'(\()?(\^_\^|&quot;▔㉨▔|╮(╯▽╰)╭|T.T|＠_＠!!!)(\))?',r''],
    [r'(^(病人|医生)：(\/\:\:[^\u4e00-\u9fa5]*|emm{1,}？?|[^\u4e00-\u9fa5\d\.？]*)$)',r''],
    [r'(\/\:\:[^\u4e00-\u9fa5]*|emm{1,}？?)',r''],
    [r'(.*无法显示.*)',r''],        # 一些无法显示的文件
    [r'🐏',r'阳'],
    [r'🦋',r'蝴蝶'],
    [r'🈶',r'有'],
    [r'⭕',r'圈'],
    [r'(^(病人|医生)：https?.*)',r''],
]
Line_feed_rules = [
    [r'^(病人|医生)：',r'^(?!病人：|医生：).+']
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
            [r'^[#\*]{0,4}\s?(References?：?|Funding( Sources| Statement| and Disclosure)?|Polls on Public|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?ment|Conflicts? of [Ii]nterest|Source of (Support|Funding))s?[#\*]{0,4}\s{0,}($|\n)'],
            [r'病人：医生啊，我最近心慌，咋回事，老是做噩梦，晚上睡不好'],
        ]

        for start in ending_starts:
            references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
            for index, item in enumerate(context):
                if re.search(start[0], item.strip()):
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
                    if index + 1 < len(context) and re.search(current_line_rule, stripped_item) and re.search(next_line_rule, context[index + 1].strip()):
                        # 合并当前段和下一段
                        # context[index] = item.rstrip() + "|删除段之间换行|" + context[index + 1].lstrip()
                        context[index] = item.rstrip() + context[index + 1].lstrip()
                        # 删除下一段
                        del context[index + 1]
                        index = index-1
                        break

                # 如果规则长度为 1，只需要匹配当前行
                elif len(line_feed_rule) == 1:
                    if index + 1 < len(context) and re.search(current_line_rule, stripped_item):
                        # 合并当前段和下一段
                        # context[index] = item.rstrip() + "|删除段之间换行|" + context[index + 1].lstrip()
                        context[index] = item.rstrip() + context[index + 1].lstrip()
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





def clean_text(context, lang):
    split_token = "\n"
    cp = clean_pattern()
    sp = speicalProces()
    context = context.split(split_token)

    # 若有需要再补充正则并调用，正则在对应的函数里补充
    context = cp.delete_page_start(context)
    context = cp.delete_page_ending(context)
    # context = cp.delete_page_middle(context)
    context = cp.more_line_feed(context,Line_feed_rules)

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
    context = re.sub(r'([。，？；])(\s?[？。，：；]){1,5}',r'\1',context)
    context = re.sub(r'([,\.?])(\s?[?,\.]){1,5}',r'\1',context)
    return context




fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean2_chunyuyisheng_qa.jsonl", "w", encoding="utf-8")
with open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\chunyuyisheng_qa_preformat.jsonl", "r", encoding="utf-8") as fs:
    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "96dce1c6-4852-4356-b0de-b7fe1305243c":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0', r' ', context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        print(item)
        fw.write(item + "\n")
# fw.close()
