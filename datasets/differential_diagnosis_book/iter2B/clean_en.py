
import json
from tqdm import tqdm
import re
import random

pattern_en = [
    [r'(■|©|●|◆)', r''],
    # 固定格式  带有（）的图片表格描述 附录描述 协议描述   顺序不能打乱
    [r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:]?[^\(\)]*\))', r''],  # 1. 这些固定的词语紧贴左括号
    [r'(\(\s?[^\(\)]*)([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))', r'\1)'],  # 这些固定的词语在句子中间但是前半句可能有用 用[\.;]\s来判断前半句是否结束
    [r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+)s?[\s\.:][^\(\)]*\))', r'通用删除1(英):<u>\1</u>'],  # 最广泛的形式从左括号匹配到右括号
    # [r'(.*,\s?et[\s\xa0]{1,3}al.*)', r'通用删除2(英):<u>\1</u>'],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
    [r'^\b(\w+(\s\w+){0,})\s+(\1)\b', r'\1'],  # 解决句首出现的单词重复的问题
    [r'(^[\*#]{0,4}(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news|You can find more information at|See also|Adapted by|For more information).*)', r'通用删除3(英):<u>\1</u>'],  # 开头固定这种情况较多这种固定开头后面都能添加 (时事通讯|获取克罗恩资讯|专家提示|了解最新动态|注册获取最新冠状病毒新闻|你可以寻找更多消息在...|另请参见...|改编自...|更多信息)
    [r'(?<![\dm\s])(\s{0,}<sup>(<a>)?\s{0,}\d+[\d\s\–—,\(\)\[\]]{1,20}(</a>)?</sup>)', r'通用删除4(英):<u>\1</u>'],  # 特殊数字  排除可能出现的次幂情况
    [r'(.*(doi|DOI)\s?:.*)', r'通用删除5(英):<u>\1</u>'],  # 存在有DOI描述的句子
    [r'((\\)?\[[\d\s,\\，\–\-—]{1,}(\\)?\])', r'通用删除6(英):<u>\1</u>'],  # 带有方括号的数字引用
    # [r'((\\)?\([\d\s,\\，\-\–—]{1,}(\\)?\))', r'通用删除7(英):<u>\1</u>'],  # 带有圆括号的数字引用
    [r'((\\)?\[\s?[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(\\)?\])', r'通用删除8(英):<u>\1</u>'],  # 固定格式  带有[]的图片表格描述 附录描述 协议描述 无关网址描述
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
    [r'(^[#\*_·]*\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*\n?.*)', r'通用删除16(英):<u>\1</u>'],  # 删除开头为Figure的描述

    # 以上为通用正则库
    # ========================================================================================
    # 以下补充对此组数据清洗的特定正则
    [r'([\(（][^（）\(\)]+[，；,; ]+\d{4}[A-Za-z]?[）\)])', r'删除1:<u>\1</u>'],  # 括号内带et al\.的参考
    [r'([\(\{（][^\{\}（）\(\)]*([Ff]i ?g ?\.?(ure)?|[Ss]ee|[Pp]age|[Ee]xhibit|[Pp]icture|[Cc]hapter|[Bb]ox|[Tt]able|[，；,;]+ ?\d{4}[，；,; ]+|[ ，；,;]pp?\. ?\d+)[^（）\{\}\(\)]*[）\}\)])', r'删除2:<u>\1</u>'],  # 括号内图、表、页、年份等
    [r'(^[\*_]*(\w{1,2}( \w{1,2})+|(\w[，\.]?\w{0,1})|[\d_ ]+)[\*_]*$)', r'删除3:<u>\1</u>'],  # 无关零碎段，B、a bC、_a_ bC、C21等
    [r'(^[\*\.]*[\d _]*(?:(\d+\\?\.)|([A-Z][A-Z\-\'a-z]+[，,]? [A-Z ]{1,4}[\.，,：\(])).*(\d+(?:\(\d+\))?[：:； ]+[a-zA-Z]?\d+|[a-zA-Z]?\d+\-[a-zA-Z]?\d+[，\.]|et al\.|https?：\/\/|[， ]+p ?\d+|ed \d+，|[\.，][A-Za-z_ ]+\d{4}[，;；\._]+).*)', r'删除4:<u>\1</u>'],  # 参考文献
    [r'(^[\\\*_ ]*(\d+|[A-Z]{1,2}|SUGGESTED READING|Suggested Reading|ACKNOWLEDGMENT|Acknowledge?ments?|I. INTRODUCTION|[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc] ?[Ee][Ss]?|(Selected )?References?|FURTHER READING|Further reading|5\'\-\-CACGTAAGCTATGCAGGCTT\-\-3\'|Useful websites)[\*_]*$)',  r'删除5:<u>\1</u>'],  # 参考文献标题及穿插的标题
    [r'(^(?=[\w\W]{0,150}$)[A-Z][a-z]+ [A-Z\.]{1,6}，.*\n?.*)', r'删除6:<u>\1</u>'],  # 删除4参考遗留的段落
    [r'(^[\*_]*(del\(13q\).{0,10}|This page intentionally left blank|( ?\([a-z]\) ?_?)+|[a-z_\d]{1,3} [a-zA-Z])[\*_]*$)', r'删除7:<u>\1</u>'],  # 一些零碎的无关段落
    [r'(^[\*_]*(www\.|E?mail:|[Hh]ttp).*)', r'删除8:<u>\1</u>'],  # 网址、邮箱
    # [r'(^(?=.{50,350}$)(.*(?:\([a-zA-Z]\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*(?:\([a-zA-Z]\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*))', r'删除9:<u>\1</u>'],  # 图注换行部分
    [r'(^(?=.{0,200}$)(?:\d+\.|\(\d+\)) ?.*[,，] ?[A-Za-z]{2,}[,，] ?[A-Za-z]{2,}$)', r'删除10:<u>\1</u>'],  # 人物介绍，地名结尾
    [r'(^(The authors? (would like to )?thanks?).*)', r'删除11:<u>\1</u>'],  # 致谢段落
    [r'(^[\*_]*(Also[,，]? [Ss]ee [Cc]hapter|For more details?[,，]|Acknowledgements are).*)', r'删除12:<u>\1</u>'],  # 一些特殊无关段
    [r'(^[\*_]*([Ff]rom：|Source：).*)', r'删除13:<u>\1</u>'],  # 文献来源
    [r'([a-z]\.)( ?[\|\d]+([， \.\-\|]\d*)*$)', r'\1删除14:<u>\2</u>'],  # 段末无关数字
    ]


pattern_zh = [
    [r'(\*{2,})', r''],
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
            [r'(^[#\s]*(Preface)：?\s*$)', 0],
            # [r'(^[#\s]*(Background|1\. Introduction).*)', 0],
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
                    context[i] = "通用开头删除-1:<u>{}</u>".format(context[i])
                    # context[i] = ""
            if flag:
                break
        return context

    # 通用句中某一部分的删除
    def delete_page_middle(self, context, lang):
        """
        通用删除某一部分方法
        :param context: 切分过的内容，列表结构
        :param start_to_end的每一项[0]: 从某一段开始的特征
        :param start_to_end的每一项[1]: 到某一段结束的特征
        :param start_to_end的每一项[2]: 根据结束段是否删除设置1或0
        :return: 返回打过标签的列表
        """
        start_to_end_en = [
            [r'(^[\*_ ]*(ACKNOWLEDGE?MENTS?|Acknowledge?ments?)[\*_ ]*$)', r'(^\*{2}[_\- ]*([A-Z][a-zA-Z\- ]+)[_ ]*\*{2}$)', 0],
        ]
        start_to_end_zh = [
            # 样例
            # [r'funding|...', r'Acknowledgments', 1],
        ]

        start_to_end = start_to_end_en if lang == 'en' else start_to_end_zh
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


class speicalProces:
    def __init__(self):
        pass

    def page_number_duan(self, context):
        new_list = []
        for con in context:
            if len(re.findall(r'([，；] ?\d+[a-z]?[\d\-]*[a-z]?)|( _\d+_ )', con)) > 25:
                con = f'此段无关页码删除:<u>{con}</u>'
                new_list.append(con)
                continue
            if re.search(r'([^\d][，；\._ ]+\d+[a-z]?[\d\-]*[a-z]?[\*_]*$)|(^[\*_]*[a-z\\\-A-Z ]+\d+[\*_]*$)', con) and len(con)<150:
                if re.search(r'(^(CASE|[Cc]ase))', con):
                    new_list.append(con)
                    continue
                con = f'此段无关页码删除:<u>{con}</u>'
                new_list.append(con)
                continue
            new_list.append(con)
        return new_list


    def move_ref(self, context):
        new_list = []
        patterns = [
            r'^[\*\.]*[\d _]*(_\d+_ ?|\d+\\?\.|[A-Ze][A-Z\-\'a-z]+[， ,]?[A-Z ]{1,4}[\.，,：\(])',  # 参考文献开头，序号或者人名
            r'([\s\.，,]+et al?[\.:：，,]+)',  # et al
            r'(\d+(\(\d+\))?[：:；; ,，]+[a-zA-Z]?\d+)|([a-zA-Z\d]{1,4}[\-–][a-zA-Z\d]{1,4}[，,\.])|(\d+\([a-zA-Z\d]{1,4}([\-–][a-zA-Z\d]{1,4})?\)[：:；; ,，])|(\([^\(\)]*p[p\. ]*\d+[\-–][a-zA-Z\d]{1,4}\)[，,\.])',  # 页码范围格式
            r'([Dd]oi[：:])',  # DOI
            r'([Vv]ol\.?\s*\d+)',  # 卷号
            r'(no\.?\s*\d+)',  # 期号
            r'([，, ]+p[p \.]*\d+|p[p \.]*\d+[：,，\- ]+)',  # 页码
            r'(ht ?tps?[：:])',  # 网址
            r'([，,；;][A-Za-z_ ]*\d{4}[，,\._]+)|([A-Z][\.，]? ?(\(\d{4}\)|\(\d{4}，[^\(\)]*\))\.)|([\.;；：:，, ]\d{4}[;；：:，,\.])',  # 年份
            r'(ed \d+[，,])|((2nd|1st|3rd|\d+th) ?ed)|(\([Ee]ds?\.?\))',  # 版本号
            r'(Accessed|editor：|Pub\-?lishing|Germany：|London：|book)',  # 访问、出版、编辑、地点
            r'(， ?[A-Z]{2,3}[，,：\.])'  # 地名，缩写
            r'(ISBN：)'  # ISBN
        ]
        for con in context:
            p_sum = 0
            for pat in patterns:
                if re.search(pat, con):
                    p_sum += 1

            if (p_sum >= 3 and len(con) < 400) or (p_sum == 2 and len(con) < 200):
                con = "参考删除-1:<u>{}</u>".format(con)
            # print(con, f'|{p_sum}|', '\n')
            new_list.append(con)

        return new_list


    def move_hang(self, context, lang):
        if lang == 'en':
            context = re.sub(r'([^|\n]{45,}[a-z，\-\d])([ \*]*\n+\n[ \*]*)(([a-z&][^\.\)]|\d+[^\.\d\\\)s]).{45,})', r'\1|删除1换行|\3', context)
            context = re.sub(r'([^|\n]{45,}[a-z，\-\d])([ \*]*\n+\n[ \*]*)((\( ?[^\d]).{45,})', r'\1|删除2换行|\3', context)
            context = re.sub(r'([a-z，\d\--])([ \*]*\n+\n[ \*]*(Table) [\W\w]*?)(\n+\n[ \*]*)([a-z][^ \--].{45,})', r'\1|删除表格换行|\5\2', context)
            context = re.sub(r'([^|\n]{45,}[a-z，\-\d])(\n+\n)([ \*]*[A-Ze][A-Z\-\'a-z]+(?: [A-Ze][A-Z\-\'a-z]+)?[ \*]*\n+\n)((?:[a-z&][^\.\)]|\d+[^\.\d\\\)s]).*)', r'\3\1|删除标题插入换行|\4', context)

            # context = re.sub(r'([^|\n]{50,}[^\.])(\n+\n[ \*]*)([a-z][^\)\.]|\d+ ?[^\.\\\)s])', r'\1|删除2换行|\3', context)
            # context = re.sub(r'([^|\n]{50,}[，,a-z])(\n+\n[ \*]*)([A-Z][a-z]{3,}[,，].{40,})', r'\1|删除5换行|\3', context)
            # context = re.sub(r'([a-z\-\d])(\n+\n[ \*]*)(\.)', r'\1删除3换行\3', context)
            # context = re.sub(r'([^|\n]{50,}[,，a-z])(\n+\n[ \*]*)((?!Table)[A-Z][^|\n]{35,}\.[^|\n]{200,})', r'\1|删除4换行|\3', context)

        return context


    def move_hang2(self, context, lang):
        if lang == 'en':
            context = re.sub(r'(\n\n[\*_ ]*(?:\d+\.|\(\d+\)))([\*_ ]*\n\n[\*_ ]*)([A-Z].*)', r'\1|删除序号换行|\3', context)  # 引用序号换行删除
            context = re.sub(r'(\-|[^|\n]{45,}[A-Za-z，\d→\)])([ \*]*\n+\n[ \*]*)(([\“a-z0&\(]|\d+[^\.\d\\\)s]).{45,})', r'\1|删除0换行|\3', context)
            context = re.sub(r'(\n[\* _]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)? (?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)?)([ _\*]*\n+\n[ _\*]*)(.*)([ _\*]*\n+\n[ _\*]*)(.*)', r'\1|删除3图换行|\7|删除3图换行|\9', context)

            context = re.sub(r'(\n\n[\*_]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+.{50,})([ \*]*\n+\n[ \*]*)(.*(?:\([a-z](?:，[a-z])?\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*(?:\([a-z](?:，[a-z])?\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*)', r'\1|删除1图换行|\5', context)
            context = re.sub(r'([ \*_]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)?)([ _\*]*\n+\n[ _\*]*)(.*[^\)\.\?？][ _\*]*\n)', r'\1|删除2图换行|\5', context)

        return context


def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    cp = clean_pattern()
    sp = speicalProces()
    if lang == 'en':
        context = re.sub(r'([\u4e00-\u9fff]+)', r'', context)
        context = re.sub(r'\n\n(# ?(\d+\. ?.*)[\w\W]*?\n\n)(\2[\w\W]*?\n\n)(Keywords)', r'\n\n\2\n\n\4', context)
        context = sp.move_hang2(context, lang)
    context = context.split(split_token)

    # 若有需要再补充正则并调用，正则在对应的函数里补充
    context = cp.delete_page_start(context)
    # context = cp.delete_page_middle(context, lang)
    context = sp.move_ref(context)
    context = sp.page_number_duan(context)


    final_results = []
    for item in context:
        # 1.正则
        if lang == "en":
            for pattern_item in pattern_en:
                src = pattern_item[0]
                tgt = pattern_item[1]
                item = re.sub(src, tgt, item)
        else:
            item = item.strip('').strip('*')
            for pattern_item in pattern_zh:
                src = pattern_item[0]
                tgt = pattern_item[1]
                item = re.sub(src, tgt, item)
        final_results.append(item)

    final_results = [con for con in final_results if con.strip()]
    context = split_token.join(final_results)
    context = sp.move_hang(context, lang)

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




fw = open(r"C:\Users\Administrator\Desktop\original_data\differential_diagnosis_book\differential_diagnosis_book_preformat_en_chunk_clean2B.jsonl", "w", encoding="utf-8")
with open(r"C:\Users\Administrator\Desktop\original_data\differential_diagnosis_book\differential_diagnosis_book_preformat_en_chunk.jsonl", "r", encoding="utf-8") as fs:
    num = 3
    lines = fs.readlines()#[num-1:num]
    lines = random.sample(lines, 300)
    for items in tqdm(lines):
        item = json.loads(items.strip())
        seq_id = item["seq_id"]
        pattern = r'769957bc-60ea-4021-a12e-b985711e02d1_3$'
        # if re.search(pattern, seq_id):
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0', r' ', context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context, '\n---------换页----------')
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
fw.close()