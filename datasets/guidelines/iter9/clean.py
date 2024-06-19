import json
import os
import re
from tqdm import tqdm
import Levenshtein

pattern_list_en = [
    [r'[^\.\n]*\b(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b[^\n]*', ''],
    [r'([^\.\n]*Case\s\d+)|((\bcs\b:.*)|(\bit\b:\d+)|(\bsr\b:.*)|(ISBN(:?).*)|(\bde\b:.*)|(\bhe\b:))|(\bnl\b:[^\n])|(\bda\b):[^\n]|((-\s*)?Copyright)|([^\.\n]*copyright[^\.\n]*)|[^\.\n]*IU\.S\..*',''],  # cs:13442112、it:1132313、ISBN2321311、...copyright...、...IU.S...
    [r'[^\.\n]*(F|f)or\s*detailed\s*(recommendations)?[^\.\n]*', ''],
    [r'[^\(\.\n]*recommendation \d+\.\d+\.\d+\.\d+[^\.\n\)]*',''],
    [r'(Return to top)|(Adapted from the FDA Package Insert)|([^\.\n]*(P|p)lease[^\.\n]*)', ''],
    [r'\(go\s*to\s*(R|r)esults\s*in\s*(S|s)ection(s?)\s*\d+.*?\)', ''],
    ['(\(\d\s*References)?(\(See)?.*\.\.\.\sread more\s*\)\.', ''],  # 1 References See...sread more.
    [r'(\((see|See)\s*(Table|table|Figure|figure|Section)?.*?\))', ''],
    [r'(\()\b(Table(s?)|table(s?)|TABLE|Figure(s?)|figure(s?)|Section|diagram|Appendix|Box|(S|s)ource(s?)|Fig|p)\b:?\.?\s*(\d+)?(\.?).*?(\))', ''],
    [r'[^\.]*\b(\b(T|t)able(s?)\b|TABLE|(F|f)igure(s?)|FIGURE|(S|s)ection(s?)|diagram(s?)|(A|a)ppendix|APPENDIx|Box|Fig)\b[^\n]*', ''],
    [r'(Re)?(S|s)ource(s?):?\s*of\s*evidence',''],
    [r'# (Table|Price|((Re)?(S|s)ource(s?):?\s*)|Notes|((F|f)urther information))', ''],  ## Table、# Resource
    [r'[^\.\n]*Fig.*?Pubic[^\.\n]*', ''],
    [r'\bOR\b|(\{\{Cite)', ''],  # OR、...{{Cite
    [r'[^\.\n]*(see\s*also)[^\.\n]*', ''],  # See:...、...can be found in...
    [r'[^\.\n]*\b(R|r)eference(s?)\b[^\.\n]*', ''],
    [r'[^\.\n]*§.*-\s*-\s*-[^\.\n]*', ''],  # §...- - -...
    [r'[^\.\n]*Cavernous\s*sinus\s*aneurysm[^\.\n]*', ''],
    [r'([^\.\n]*Image Gallery[^\.\n]*)|(\(.*?MRI.*?\))', ''],  # ...Image Gallery...、(...MRI...)
    [r'(\(Images.*of.*?\)|(.*M1\s4BT.*)|Contact NICE)', ''],  # (Images...of...)、...M1 4BT...、Contact NICE
    ['(.*\d{4}.*(ISBN|Retrieved).*)', ''],  # ...1970...ISBN...、...1970...Retrieved...
    [r'\(\s*#?((\d+-\s*\d+)|(\d+(,|，)\s*\d+.*)|(\d+))\)', ''],  # ( #(12-44))、( #(12.asdf))
    [r'(via:.*)|(el ta(\(\d+.*?\))?)', ''],  # via:...、el ta(66english)
    [r'\(\d{4}-\d{4}\s*update.*?et al.\)?', ''],  # (1980-1998 update in et al
    [r'\([a-zA-Z]+\s*.*et\s*al.*\d{4}(.*?\))?', ''],  # (today et al 1980 ,1999)
    [r'[^\.\n]*(A|a)dditional\s*information[^\.\n]*', ''],
    [r'[^\.\n]*(\..*?http://.*\.)|\(.*?http://.*?\)|((\()?www\..*((/.*?\))|(g?)))[^\.\n]*', ''],

    ['\.\.\.', '.'],
    ['\(DO NOT EDIT\)', ''],
    ['▶|●|©|®|(.*-\s↑.*)|(:-)|❑|†|¶|║|§|∧|™', ''],
    ['American Samoa.*', ''],
    ['\(\s*\d+\s*\)', ''],

    # new
    [r'#?\s*Reference(s?)\s*and\s*notes.*', ''],  # References and notes
    [r'.*(M\.D\.)?,\s*Ph\.\D.', ''],  # Steven C. Campbell, M.D., Ph.D.
    [r'[^\.\n]*((M|m)ore\s*information)[^\.\n]*', ''],  # For more information, call 1-800-445-3235 or go to .
    # [r'[^\.\n]*following[^\.\n]*',''],

    # new
    [r'Taken\s*from.*\+[^\.\n]*', ''],  # 去掉Taken from Shapiro  .   Taken from Monson  . + Taken from Thomas et a I.,
    ['🔗|❤️|⦁|►|||➥', ''],
    [r'\*$', ''],  # 去除结尾的*
    [r'[^\.\n]*(C|c)lick\s*here[^\.\n]*', ''],  # 去除For the WikiDoc page for this topic, click here
    [r'[^\.\n]*Report\s*format[^\.\n]*', ''],
    [r'[^\.\n]*can.*?find[^\.\n]*', ''],
    [r'[^\.\n]*Return\s*to\s*recommendation(s?)[^\.\n]*', ''],
    [r'[^\.\n]*Recommendation(s?)\s*\d+\.\d+\.\d+\s*(to\s*\d+\.\d+\.\d+)?[^\.\n]*', ''],
    [r'[^\.\n]*detail(s?)[^\.\n]*', ''],
    [r'[^\.\n]*(F|f)or\s*related.*?see[^\.\n]*', ''],
    ['\.\.', ''],  # 去除..
    [r'[^\.\n]*(\b(A|a)lso\b\s*\bsee\b)|(\bSee\b)|(\b(S|s)ee\b\s*\balso\b)[^\.\n]*', ''],
    [r'[^\.\n]*(R|r)efer to[^\.\n]*', ''],
    [r'-\s^[^\.\n]*',''], #去除- ^ Lee D.G. Chen T. . "Reduction of Manganate(VI) by Mandelic Acid and Its Significance to Development of a General Mechanism for Oxidation of Organic Compounds by High-Valent Transition Metal Oxides". Journal of the American Chemical Society. 115: 11231–11236. doi:10.1021/ja00077a023.
    [r'-?.*\d{4}.*?(DOI|doi):[^\.\n]*', ''],# 去除参考文献：- G. Procter, S. V. Ley, G. H. Castle “Barium Manganate”  in Encyclopedia of Reagents for Organic Synthesis (Ed: L. Paquette) 2004, J. Wiley & Sons, New York. DOI: 10.1002/047084289.

    # new
    [r'↑.*', ''],  # 去除无意义片段 ↑ Jump up to: 14.0 14.1 14.2
    [r'[^\.]*(P|p)age[^\n]*',''],
    [r'[^\.]*(J|j)oin[^\n]*',''],
    [r'\bnn\b:.*', ''],  # 去除nn:Pulmonalklaff.....
    [r'(,\s*,\s*,)|(,\s*,)|(\.\s*\.)', ','],

    # new
    [r'[^\.\n]*evidence(s?)\s*review(s?)[^\.\n]*', ''],# 去掉evidence review E1: management options for mild to moderate acne – network meta-analyses
    [r'(".*?"),\s*[A-Za-z]*\s*\d{4}.*\.', ''],# 去除类似格式的参考文献，特征是文章题目用双引号引出，并有年份：'Interventional procedure overview of corneal implants for the correction of refractive error', November 2006.
    [r'(\'.*?\'),\s*[A-Za-z]*\s*\d{4}.*\.', ''],
    [r'#[^\.\n]*(Images|(Template:[^\.\n]*)|Acknowledgements)', ''],#去除 #Images  #Acknowledgements
    [r'[^\.]*\b(APPENDIX|appendix|Appendix|(T|t)able(s?)|TABLE|Figure|diagram|figure|Box|FIG|Fig|fig)\b[^\n\.]*', ''],#去除带有Appendix、Table等的这句话，如：The current OSHA standards and the NIOSH-recommended exposure limits, as well as pertinent health effects, are listed in Appendix B.

    [r'\nfig\n',''],
    ['{{{indicationType}}} ',''],
    [r'[^\.\n]*(C|c)hapter[^\.\n]*',''],
    [r'[^\.\n]*Editor[^\.\n]*',''],#去掉Assistant Editor-In-Chief: Michelle Lew 编辑人名
    [r'[^\.\n]*NDC[^\.\n]*',''],
    [r'[^\.\n]*\d+-\d+-\d+[^\.\n]*',''],#去掉NDC 0065-0023-15
    [r'[^\d\(]*pictured[^\)]*',''],
    [r'(\d{1,2}\s*[,\.]\s*)?\d{1,2}\s*\.?$(?:$|[^(\d{4})])',''], #去除句末无关数字引用，如：# TEAM BRIEFING 3,4
    [r'[^\(\.\n]*see\s*illustration[^\)\.\n]*',''],
    [r'[^\.\n]*thank[^\.\n]*',''],
    [r'#\s*Disclaimer',''],
    [r'[^\.\n]*WikiDoc[^\.\n]*',''],
    [r'[^\n]*Books[^\n]*',''],
    [r'[^\.\(\n]*[A-Z][a-z]*\s*&[^\n\)]*',''],
    [r'(?:^|[^#])#(?:$|[^#])', '\n\n#'],  # 解决#之后文本未换行问题，如：AF and interventional procedures# TEAM BRIEFING
    [r'(\.\s*,)|(\.\.)|(,\s*\.)', '.'],
    [r'^[\.,:\\]*\s*',''],#去除句首多余的标点
    [r'[^\.\n]*\b(and|AND|or|with|for|on|to|about|as|by|of)\b\s+\.[^\n]*',''],
    [r'\s{3,}',' '],
    [r'\(information\s*available\s*at.*?\)',''],
    [r'\(\s*\)',''],
    [r'^n\s',''],#去除句首的n,如：n Human rights and gender equality must be placed at the centre of a comprehensive approach to health programming, in particular in relation to sexuality and sexual health.
    [r'#\s*Warnings',''],
    [r'(\bsv\b:[^\n])|(\buk:\b[^\n])',''],
    [r'[^\n]*-\s*-\s*-\s*[^\n]*',''],
    [r'[^\.\n]*\d{4};\s*[A-Za-z]*\s*\d+:?\s*\d+(-|–|;)\d+[^\.\n]*',''], #去除页码：Bioscience and Microflora, 2001; Vol 20: 43-48.
    [r'[^\n]*[A-Z][a-z]+\s*[,\.]?\s*[A-Z]?\s*[,\.]?\s*&\s*[A-Z][a-z]+[^\n]*',''],#去除带人名的参考文献
    [r'-\s*$',''],
    [r'[^\.\n]*Image\s*courtesy[^\.\n]*',''],
    [r'[^\.\n]*Google\s*Scholar[^\.\n]*',''],
    [r'[^\.\n]*at\s*\.$',''],
    [r'[^\.\n]*Images\s*shown[^\.\n]*',''],
    [r'(\d{4}\s*[A-Z]?([a-z]+)?;\s*)?\d+\s*:\s*\d+\s*(-|–)\s*\d+',''],
    [r'[^\n]*((Manufactured for)|(AUTHORS)|(External link)|(Classes and members))[^\n]*',''],
    [r'[^\n]*[A-Z][a-z]+,\s*([A-Z]\.)?\s*[A-Za-z]*\s*[A-Z][a-z]+[^\n]*',''],
    [r'[^\n]*(\bpp\b\.?)?\s*((\d+\s*:)|(\s*\bpp\b\s*))s*\d+-\d+[^\n]*',''],
    [r'[^\n]*(PMID:)|(GeneID)[^\n]*',''],
    [r'[^\.\n]*in\s*the\s*following\s*document[^\.\n]*',''],
    [r'(?<=[^0-9]\.)\s*\d+(?:,\d+)*\s*(?=[A-Z])',''],#去除句子前的无关数字引用：26 Bedside ultrasound is operator dependent; therefore, the diagnostic accuracy may vary depending on the level of training.
    [r'[^\n]*Recommendations[^\n]*',''],
    [r'[^\.\n]*Links[^\.\n]*','']
        ]

context_pattern=[
    ['see illustration',''],
    ['Pre-delivery 1',''],
    ['Loading',''],
    ['Loadin',''],
    ['# List of contributors:','']

        ]
class speicalProces:
    def __init__(self):
        pass

    # 判断首字母非大写字母
    def is_not_upper(self, char):
        return not char.isupper()


    def step1_remove_duplicates(self, text, lang):  # 模糊去重
        # 分割文本成句子
        sentences = text.split("\n")

        # 定义Jaro-Winkler相似度阈值
        threshold = 0.8

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

    def step2_removeLinefeed(self, nums):  #去除多余换行
        slow, fast = 0, 1
        while fast < len(nums):
            nums[slow] = nums[slow].strip()
            nums[fast] = nums[fast].strip()
            if (nums[slow].endswith("and") or nums[slow].endswith("of") or nums[slow].endswith("any") or nums[
                slow].endswith("a") or nums[slow].endswith("is") or nums[slow].endswith("for") or nums[slow].endswith(
                "the") or nums[slow].endswith("or") or nums[slow].endswith(",")) and self.is_not_upper(nums[fast][0]):
                nums[slow] = nums[slow] + " " + nums[fast]
            elif "#" not in nums[slow] and "*" not in nums[slow] and re.match(r'.*[a-z]$', nums[slow]) and re.match(
                    r'^[a-z]', nums[fast]):
                nums[slow] = nums[slow] + " " + nums[fast]
            else:
                slow = slow + 1
                nums[slow] = nums[fast]
            fast = fast + 1
        return nums[0:slow + 1]

    def step3_is_last_word_preposition(self,sentence): # 过滤结尾是介词、不完整的的句子
        sentence = re.sub(r'[^\w\s]', '', sentence)  # 去除标点符号
        words = sentence.split()
        prepositions = ["and", "in", "on", "at", "for", "with", "about", "as", "by", "to", "from", "of","AND","or"]  # 介词列表
        return words[-1] in prepositions

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
        # print(item)
        if "REFERENCES" in item:
            # print(1)
            continue
        if "Additional resources" in item:
            continue
        if "Additional images" in item:
            continue
        if "Additional Links" in item:
            continue
        if "Information for patients" in item:
            continue
        if "Sources of evidence" in item:
            continue
        if "Associated Documents" in item:
            continue
        item = re.sub(r"#\n","# ",item)
        item = item.strip(split_token).strip()
        item = sp.step1_remove_duplicates(item, "en")
        item = item.strip().split("\n")
        item = sp.step2_removeLinefeed(item)

        for i in range(len(item)):

            for pattern_item in pattern_list:
                item[i] = re.sub(pattern_item[0], pattern_item[1], item[i])
                item[i] = sp.step4_repair_parentheses(item[i])
                item[i] = item[i].strip()
            for pattern_item in context_pattern:
                item[i] = re.sub(pattern_item[0], pattern_item[1], item[i])

        for i in range(len(item)-1,-1,-1):
            if item[i].strip().startswith("#") or item[i].strip().startswith("*"):
                item.pop()
            else:
                break
        item = ("\n".join(item)).strip()
        result.append(item)
    context = split_token.join(result)
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
        context = clean_text(context, "en")
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")

