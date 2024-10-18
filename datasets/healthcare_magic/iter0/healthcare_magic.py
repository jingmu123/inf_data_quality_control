import json
import re

from tqdm import tqdm








fw = open(r"C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\reclean0_healthcare_magic.jsonl", "w",encoding="utf8")
with open('C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\original_data\healthcare_magic_preformat.jsonl', 'r', encoding='utf8') as fr:
    lines = fr.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        content = item['text']
        updated_content = re.sub(r"(\*\*(Question|Answer)\*\*:)", r"\n\n\1", content)
        item["text"] = updated_content.strip().strip()
        item = json.dumps(item, ensure_ascii=False)
        print(item)
        fw.write(item + "\n")