import json
import os
import re
# from langdetect import detect
# from langdetect import detect_langs
from tqdm import tqdm

pattern_list_zh = ['（?另见[^）]*.',
                   r'看?法? 进行患者培训\s?',
                   '[^\。]*参考(文献)*.?doi: [^\s]+',
                   '[^\。]*参考(文献)?[^，。]*.\)?）?',
                   r'[^。]*?(\.\.\. )?阅读更多[^。]*。[\)）]?',
                    '阅读更多[^\u4e00-\u9fa5]*',
                   '更多信息[^，。,\.]*.',
                   'www\.\w+\.\w+[^\s]*\s',
                   '会在这本.*点击此处',
                   '[（\(][^\)）]{0,10}(也可)?(另请)?(也)?(请)?参(见|阅)(概述)?[^\.）\)。]*.[）\)]?',
                   '[^。]*参见[^。]*',
                   # '[（(]?[^)）]{5}(也可)?(另请)?(也)?(请)?参见(概述)?[^\.,。）)]*。）?',
                   '[^\.,]*\.\.\. Common.TooltipReadMore',
                   '(表格)?(Table)? \$\(document\).ready.*?(\} \}\); \} \}\);)',
                   '(\$\(document\))?.ready.*?console',
                   # '(表格)?(Table)? \$\(document\).*\);',
                   '请注意，本手册.*',
                   '\(又见 .*[^ ]概述{1,3}',
                   '\(s?S?ee[^\)]*.\.?',
                   '观看这些视频.*',
                   # r'(\p{L}+)\s+\1(\s+\1)*',
                   ' ?\(?（?见表 ?[^。]*',
                   ' ?（?\(?见图 ?[^。]*',
                   ' ?（?\(?也见 ?[^。]*',
                   '[\(（ 也可同样]+见 ?[^。]*。?',
                   '[^\u4e00-\u9fa5-。]{10,1000}'
                   ]

pattern_list_en = [
                   # '[^\.]*R?r?eferences? [^，。]*.?doi:?\.? ?[^\s]+',
                   # r'\b(\w+)\s+\1\b(\s+\1)*',
                   # '[^.]*\(S?s?ee[^\.]*\)?(...)?( Common.TooltipReadMore)?[^\.]*\.',
                   # '\(\s+?s?S?ee[^)]*?read more \)',
                   #1
                   '(\(\s?s?S?ee[^\.]*)?\.?\(?[^\.]*[\.]{0,3} read more [^A-Z\.]*(\.\))?',
                   '[^\.]*?View Patient Education\s?',
                   'More Information The following.*',
                   '(表格)?(Table)? \$\(document\).ready.*?\} \}\); \} \}\);',
                   '(\$\(document\))?.ready.*?console',
                   '[^\.]*?[\.]{0,3}?\s?Common.TooltipReadMore[^\.]*\.?\)?',
                   '\(\s?[sS]?ee[^\)\.]*[\.\)]?\)?',
                   '[^\.]*r?R?eference(?:(?!r?R?eference).)*?(doi\s?:\s?[^\s]*)(.{0,500}?doi\s?:\s?[^\s]*){0,10}',
                   '\.(\d+–\d+)*?.{0,150}(\.doi\s?:?\s?[^\s]*)(.{0,500}?doi\s?:\s?[^\s]*){0,5}',
                   '^\.'


                   # '[\(](see)?[^\)]{0,1000}TooltipReadMore \)[\.,]?',
                   # '[^\.\)]*?[\.]{0,3}\s?Common.TooltipReadMore [^\.]*?\.'



                   ]

pattern_ngram_en = r'([A-Za-z]+)\s+\1(\s+\1)*'
pattern_ngram_zh = r'\b(\w+)\s+\1\b(\s+\1)*'
pattern_ngram_punc = r'([\.。]+\s?)\1*'


def mv_ngram_repeat(content, pattern_ngram, lang):
    part = re.findall(pattern_ngram, content, flags=re.IGNORECASE)
    if not part:
        return content
    if lang == "zh":
        for p in part:
            content = re.sub(rf'({p[0]})\s+\1(\s+\1)*', p[0], content, flags=re.IGNORECASE)
            # content=re.sub('通常需要精神病转诊。|AAABBBCCC|<><><>|ABCBCABAC|又见 脊髓病变疾病概述.）...|','',content)
    if lang == "en":
        for p in part:
            content = re.sub(rf'\b({p[0]})\s+\1\b(\s+\1)*', p[0], content, flags=re.IGNORECASE)
            # item=re.sub('© Springer Science+Business Media|Did You Know...','',item)
    return content


def process_cite(context, pattern_list, pattern_ngram, lang):
    result = []
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    for item in context.split(split_token):
        item = item.strip(split_token)
        item = mv_ngram_repeat(item, pattern_ngram, lang)
        item = re.sub('通常需要精神病转诊。|AAABBBCCC|<><><>|ABCBCABAC|又见 脊髓病变疾病概述.）...|', '', item)
        item = re.sub('© Springer Science+Business Media|Did You Know...', '', item)
        for pattern_item in pattern_list:
            item = re.sub(pattern_item, '', item)
            # item = re.sub(pattern_item, '', item, flags=re.IGNORECASE)
            # item = re.findall('([^-.\dwIX]{1,10})\1{2,}', item, flags=re.IGNORECASE)
            # print(pattern_item, "\t",item)
            item = item.strip(" ").strip("\n").strip(" ").strip("\n")
        result.append(item)
    return split_token.join(result)


def rm_last_paragh(text):
    context = text.split("。")
    if len(context[-1]) < 5:
        context = context[:-1]
        context[-1] = context[-1] + "。"
    new_context = []
    for item in context:
        if len(item) > 4:
            new_context.append(item)
    return "。".join(new_context)


def rm_special_char(text):
    if text[-2:] == "了解":
        return text[:-2]
    return text

base_dir = "../../../../full_data/MSD/msd_full.jsonl"
fw = open("reclean2_msd_full.jsonl", "w", encoding="utf-8")
with open(base_dir, "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        # if item["seq_id"] != 9165:
        #     continue
        # print(context)
        # lang = detect_language(item["text"])
        lang = item["lang"]
        # print(context)
        # print("========================================")
        if lang == "zh":
            # continue
            clean_text = process_cite(context, pattern_list_zh, pattern_ngram_zh, lang)
            clean_text = re.sub(pattern_ngram_punc, "。", clean_text)
            clean_text = clean_text.replace("。，", "。")
            clean_text = rm_last_paragh(clean_text)
        else:
            clean_text = process_cite(context, pattern_list_en, pattern_ngram_en, lang)
            clean_text = re.sub(pattern_ngram_punc, ".", clean_text)
            # 替换标点连用
            clean_text = re.sub(r"\.\s?,\s?", ".", clean_text)
        # print(clean_text)
        clean_text = rm_special_char(clean_text)
        item["text"] = clean_text
        #print(item["text"])
        item["lang"] = lang
        item["tokens"] = ""
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
    # fw.close()
    # break
