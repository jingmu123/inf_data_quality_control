import json
import os
import re
from tqdm import tqdm
from nltk import word_tokenize
import nltk

nltk.download('punkt')
#r'(it:)\d+','\1'
pattern_list_en = [
    [r'\b(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b', ''],
    [
        r'(.*Case\s\d+)|((\bcs\b:.*)|(\bit\b:.*)|(\bsr\b:.*)|(ISBN(:?).*)|(\bde\b:.*)|(\bhe\b:.*))|((-\s*)?Copyright)|(.*copyright.*)|.*IU\.S\..*',
        ''],  # cs:13442112、it:1132313、ISBN2321311、...copyright...、...IU.S...
    ['\.(.*?)for detailed recommendations(.*?)\.', ''],
    ['(Return to top)|(Adapted from the FDA Package Insert)|(Loading. Please wait.)', ''],
    ['\(go to Results in Section \d+\)|(\(Recommendation.*?\))', ''],
    ['(\(\d\s*References)?(\(See)?.*\.\.\.\sread more\s*\)\.', ''],  # 1 References See...sread more.
    [r'(\((see|See)\s*(Table|table|Figure|figure|Section)?.*?\))', ''],
    [r'(\()?(Table|table|TABLE|Figure|figure|Section|diagram|Appendix|Box):?\s*(\d+)?(\.?).*?(\))?', ''],
    [r'# (Table|Price|((Re)?(S|s)ource(s?)(:(.*))?)|Notes)', ''],  ## Table、# Resource
    [r'.*Fig\.\d+\sPubic.*', ''],
    [r'\bOR\b|(.*\.{{Cite)|(.*further details.*)', ''],  # OR、...{{Cite、...further details...
    [r'((\.)?(.*?)(See|(see also)).*)|(\.(.*?)can be found in(.*?)\.)', ''],  # See:...、...can be found in...
    [r'.*\b(R|r)eference(s?)\b.*', ''],
    [r'.*§.*-\s*-\s*-.*', ''],  # §...- - -...
    [r'.*Cavernous\ssinus\saneurysm.*', ''],
    [r'(.*Image Gallery.*)|(\(.*?MRI.*?\))', ''],  # ...Image Gallery...、(...MRI...)
    [r'(\(Images.*of.*?\)|(.*M1\s4BT.*)|Contact NICE)', ''],  # (Images...of...)、...M1 4BT...、Contact NICE
    ['(.*\d{4}.*(ISBN|Retrieved).*)', ''],  # ...1970...ISBN...、...1970...Retrieved...
    [r'\(\s*#?((\d+-\s*\d+)|(\d+(,|，)\s*\d+.*)|(\d+))\)', ''],  # ( #(12-44))、( #(12.asdf))
    [r'(via:.*)|(el ta(\(\d+.*?\))?)', ''],  # via:...、el ta(66english)
    [r'\(\d{4}-\d{4}\s*update.*?et al.\)?', ''],  # (1980-1998 update in et al
    [r'\([a-zA-Z]+\s*.*et\sal.*\d{4}(.*?\))?', ''],  # (today et al 1980 ,1999)
    [r'\..*?(A|a)dditional information.*?\.', ''],

    [r'(\..*?http://.*\.)|\(.*?http://.*?\)|((\()?www\..*((/.*?\))|(g?)))', ''],
    ['\.\.\.', '\.'],
    ['\(DO NOT EDIT\)', ''],
    ['▶|●|©|®|(.*-\s↑.*)|(:-)|❑|†|¶|║|§|∧|™', ''],
    ['American Samoa.*', ''],
    ['\(\s*\d+\s*\)', ''],
    # new
    [r'-?.*,\s*\b(19|20)\d{2}\b.*?(\.)?', ''],  # - Copi, Irving. Symbolic Logic.  MacMillan, 1979, fifth edition.
    [r'#?\s*Reference(s?) and notes.*', ''],  # References and notes
    [r'.*(M\.D\.)?,\s*Ph\.\D.', ''],  # Steven C. Campbell, M.D., Ph.D.
    [r'(For more information,)?\s*call\s*\d+-\d+-\d+-\d+.*?\.', ''],
    # For more information, call 1-800-445-3235 or go to .

    # new
    [r'(\(|\[)\n', '\n'],  # 去除不匹配括号(
    [r'Taken from.*\+.*?(\.)?,?', ''],  # 去掉Taken from Shapiro  .   Taken from Monson  . + Taken from Thomas et a I.,
    ['🔗|❤️', ''],
    ['\*$', ''],  # 去除结尾的*
    ['(-\s*)?(To|For).*click here(\.)?', ''],  # 去除For the WikiDoc page for this topic, click here
    ['Report format', ''],
    ['You can find.*?.', ''],
    ['Return to recommendation(s?)', ''],
    [r'Recommendation(s?)\s+\d+\.\d+\.\d+.*', ''],
    ['For.*details.*?\.', ''],
    ['For related.*?see.*?\.', ''],
    ['\.\.', ''],  # 去除..
    ['(A|a)lso see.*?\.', ''],
    ['refer to', ''],
    [r'-\s^.*', ''],
    # 去除- ^ Lee D.G. Chen T. . "Reduction of Manganate(VI) by Mandelic Acid and Its Significance to Development of a General Mechanism for Oxidation of Organic Compounds by High-Valent Transition Metal Oxides". Journal of the American Chemical Society. 115: 11231–11236. doi:10.1021/ja00077a023.
    [r'-?.*\b(19|20)\d{2}\b.*:.*?\.', ''],
    # 去除参考文献：- G. Procter, S. V. Ley, G. H. Castle “Barium Manganate”  in Encyclopedia of Reagents for Organic Synthesis (Ed: L. Paquette) 2004, J. Wiley & Sons, New York. DOI: 10.1002/047084289.

    # new
    [r'-\s*\n', ''],  # 去掉只有 ”-  ”没有文字的行
    [r'↑.*(\d|\.)', ''],  # 去除无意义片段 ↑ Jump up to: 14.0 14.1 14.2
    [r'(-\s*)?Please.*(Join|Page).*\.', ''],
    # 去除无关文本 Please Join in Editing This Page and Apply to be an Editor-In-Chief for this topic:
    [r'\bnn\b:.*', ''],  # 去除nn:Pulmonalklaff.....
    [r'(,\s*,\s*,)|(,\s*,)|(\.\s*\.)', ','],
    [r'.*((in evidence review)|(evidence review)|(.*details.*evidence)).*?(\.)?', '']
    # 去掉evidence review E1: management options for mild to moderate acne – network meta-analyses

]


class speicalProces:
    def __init__(self):
        pass

    # 判断首字母非大写字母
    def is_not_upper(self, char):
        return not char.isupper()

    def step1_duplicate_text(self, content):  # 精准去重
        content1 = content.split("\n")
        for i in range(len(content1)):
            content1[i] = content1[i].lstrip("-").rstrip(".").strip(" ")
        # 去掉重复项
        content = list(set(content1))
        content.sort(key=content1.index)
        # 去掉上一行以介词结尾的多余换行
        temple_list = []
        for cur in range(len(content) - 1):
            if ("#" not in content[cur] or "*" not in content[cur]) and (
                    content[cur].endswith("and") or content[cur].endswith("of") or content[cur].endswith(
                "any")) and self.is_not_upper(content[cur + 1][0]):
                temple_list.append(cur + 1)
                content[cur] = content[cur] + " " + content[cur + 1]
        for i in temple_list:
            try:
                content.pop(i)
            except Exception as e:
                pass
        # print(content)
        for i in range(len(content)):
            if content[i] == '' or content[i].startswith("#") or content[i].startswith("*"):
                continue
            else:
                try:
                    if content[i][0].isalpha():
                        content[i] = "- " + content[i]
                except Exception as e:
                    pass
        return "\n".join(content)

    def step2_remove_duplicates(self, text, lang):  # 模糊去重
        # 分割文本成句子
        sentences = text.split("\n")

        # 定义Jaro-Winkler相似度阈值
        threshold = 0.9

        # 初始化已见句子集合
        seen_sentences_set = set()

        # 初始化唯一句子列表
        unique_sentences = []

        # 遍历所有句子
        for sentence in sentences:
            old_sentence = sentence
            sentence = sentence.strip(" ").strip("\n")  # 去除空格和换行符
            # 检查当前句子是否与已见句子集合中的任何句子足够相似
            is_duplicate = False
            for seen_sentence in seen_sentences_set:
                # 计算Jaro-Winkler相似度
                jaro_winkler_distance = Levenshtein.jaro_winkler(sentence, seen_sentence)
                # 如果相似度超过阈值，则认为是重复
                if jaro_winkler_distance > threshold:
                    is_duplicate = True
                    break
            # 如果不是重复的，则添加到唯一句子列表和已见句子集合中
            if not is_duplicate:
                unique_sentences.append(old_sentence)
                seen_sentences_set.add(sentence)

        # 重新组合文本
        context = "。".join(unique_sentences) if lang == "zh" else "\n".join(unique_sentences)
        return context

    def step3_resolve_space(self, sentences):  # 去掉标题中单词间的多余空格
        words_list = word_tokenize(sentences)
        words_list_new = []
        position = 0
        for word_index in range(0, len(words_list)):
            if words_list[word_index][0].isupper():
                position = word_index
            if self.is_not_upper(words_list[word_index][0]):
                words_list[position] = words_list[position] + words_list[word_index]
        for word in words_list:
            if word[0].isupper():
                words_list_new.append(word)
        return '# ' + ' '.join(words_list_new)

    def step4_repair_parentheses(self, context):  # 去除不匹配的括号
        stack = []
        # 将文本转换为列表，方便对着索引删除
        list_text = list(context)
        for i, char in enumerate(context):
            if char == '(' or char == "（" or char == '[' or char == '{':
                stack.append(i)
            elif char == ')' or char == "）" or char == ']' or char == '}':
                if not stack:
                    # 没有出现左括号,右括号直接删除
                    list_text[i] = ''
                else:
                    stack.pop()
        # 不为空说明有多余括号存在
        while stack:
            index = stack.pop()
            # 去除的括号用逗号代替
            list_text[index] = ','
        return ''.join(list_text)


def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"

    if lang == 'en':
        pattern_list = pattern_list_en

    result = []
    sp = speicalProces()

    for item in context.split(split_token):
        item = item.strip(split_token).strip()
        item = sp.step1_duplicate_text(item)
        item = sp.step2_remove_duplicates(item, "en")
        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)
        item = sp.step4_repair_parentheses(item)
        result.append(item)
        # 整合
    result_last = []
    for item_1 in result:
        result_1 = []
        item_1 = item_1.split("\n")
        for item_2 in item_1:
            if sum(1 for char in item_2 if char.isupper()) > 2 and item_2.startswith(
                    "#") and "," not in item_2 and "?" not in item_2 and "." not in item_2 and ":" not in item_2:
                item_2 = sp.step3_resolve_space(item_2)
            result_1.append(item_2)
        result_last.append("\n".join(result_1))
    context = split_token.join(result_last)
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
    return context


fw = open("../../../../full_data/guidelines/guidelines_clean.jsonl", "w", encoding="utf-8")
with open(
        "../../../../full_data/guidelines/guidelines_preformat.jsonl",
        "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        lang = item["lang"]
        context = clean_text(context, lang)
        context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")

