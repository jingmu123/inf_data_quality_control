import json
import os
import re
from tqdm import tqdm
from nltk import word_tokenize
import nltk

nltk.download('punkt')

pattern_list_en = [
    [r'\b(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b', ''],
    [r'(.*Case\s\d+)|((\bcs\b:.*)|(\bit\b:.*)|(\bsr\b:.*)|(ISBN(:?).*)|(\bde\b:.*)|(\bhe\b:.*))|((-\s*)?Copyright)|(.*copyright.*)|.*IU\.S\..*',''],
    # cs:13442112、it:1132313、ISBN2321311、...copyright...、...IU.S...
    ['\.(.*?)for detailed recommendations(.*?)\.', ''],
    ['(Return to top)|(Adapted from the FDA Package Insert)|(Loading. Please wait.)', ''],
    ['\(go to Results in Section \d+\)|(\(Recommendation.*?\))', ''],
    ['(\(\d\s*References)?(\(See)?.*\.\.\.\sread more\s*\)\.', ''],  # 1 References See...sread more.
    [r'(\((see|See)\s*(Table|table|Figure|figure|Section)?.*?\))', ''],
    [r'(\()?(Table|table|TABLE|Figure|figure|Section|diagram|Appendix|Box)\s*(\d+)?(\.?).*?(\))?', ''],
    [r'Additional information.*', ''],
    [r'# (Table|Price|((Re)?(S|s)ource(s?)(:(.*))?)|Notes)', ''],  ## Table、# Resource
    [r'.*Fig\.\d+\sPubic.*', ''],
    [r'\bOR\b|(.*\.{{Cite)|(.*further details.*)', ''],  # OR、...{{Cite、...further details...
    [r'((\.)?(.*?)(See|(see also)|also)(:?)(.*?)(\.)?)|(\.(.*?)can be found in(.*?)\.)', ''],
    # See:...、...can be found in...
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
    ['(F|f)or.*information.*', ''],
    [r'(\..*?http://.*\.)|\(.*?http://.*?\)|((\()?www\..*((/.*?\))|(g?)))', ''],
    ['\.\.\.', '\.'],
    ['\(DO NOT EDIT\)', ''],
    ['▶|●|©|®|(.*-\s↑.*)|(:-)|❑|†|¶|║|§|∧|™', ''],
    ['American Samoa.*', ''],
    ['(\(\s*\))|(\d+\s*\))', ''],
    # new
    [r'-?.*,\s*\b(19|20)\d{2}\b.*?(\.)?', ''],  # - Copi, Irving. Symbolic Logic.  MacMillan, 1979, fifth edition.
    [r'#?\s*References and notes.*', ''],  # References and notes
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
    ['You can find this information under the primary and secondary outcome report.', ''],
    ['Return to recommendations', ''],
    [r'Recommendations\s+\d+\.\d+\.\d+.*', ''],
    ['For more details refer to.*?\.', ''],
    ['For related.*?see.*?\.', ''],
    ['\.\.', ''],  # 去除..
    ['(A|a)lso see.*?\.', ''],
    ['refer to', ''],
    [r'-\s^.*', ''],# 去除- ^ Lee D.G. Chen T. . "Reduction of Manganate(VI) by Mandelic Acid and Its Significance to Development of a General Mechanism for Oxidation of Organic Compounds by High-Valent Transition Metal Oxides". Journal of the American Chemical Society. 115: 11231–11236. doi:10.1021/ja00077a023.
    [r'-.*\b(19|20)\d{2}\b.*?:.*?\.', '']# 去除参考文献：- G. Procter, S. V. Ley, G. H. Castle “Barium Manganate”  in Encyclopedia of Reagents for Organic Synthesis (Ed: L. Paquette) 2004, J. Wiley & Sons, New York. DOI: 10.1002/047084289.

]


class speicalProces:
    def __init__(self):
        pass

    def step1_duplicate_text(self, content):
        content1 = content.split("\n")
        for i in range(len(content1)):
            content1[i] = content1[i].lstrip("-").strip(" ")
        content = list(set(content1))
        content.sort(key=content1.index)
        for i in range(len(content)):
            if content[i][0].isalpha():
                content[i] = "- " + content[i]
        return "\n".join(content)

    def step2_resolve_space(self, sentences):
        words_list = word_tokenize(sentences)

        def is_not_upper(char):
            return not char.isupper()

        words_list_new = []
        position = 0
        for word_index in range(0, len(words_list)):
            if words_list[word_index][0].isupper():
                position = word_index
            if is_not_upper(words_list[word_index][0]):
                words_list[position] = words_list[position] + words_list[word_index]
        for word in words_list:
            if word[0].isupper():
                words_list_new.append(word)
        return '# ' + ' '.join(words_list_new)


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
        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)
        result.append(item)
        # 整合
    result_last = []
    for item_1 in result:
        result_1 = []
        item_1 = item_1.split("\n")
        for item_2 in item_1:
            if sum(1 for char in item_2 if char.isupper()) > 2 and item_2.startswith(
                    "#") and "," not in item_2 and "?" not in item_2 and "." not in item_2 and ":" not in item_2:
                item_2 = sp.step2_resolve_space(item_2)
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
with open("../../../../full_data/guidelines/guidelines_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        lang = item["lang"]
        context = clean_text(context, lang)
        context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")

