import json
import uuid
from langdetect import detect
from tqdm import tqdm
import hashlib

def detect_language(content):
    #print("context",content)
    lang = detect(content)
    if lang == "zh-cn":
        return "zh"
    if lang == "en":
        return "en"
    return "None"

base_dir = "../../../../full_data/baiduyidian/"
base_file = f"{base_dir}/all_data.jsonl"
save_file = f"{base_dir}/all_data_preformat.jsonl"
fw = open(save_file, "w",encoding="utf-8")

with open(base_file, "r",encoding="utf-8") as fs:
    data_dict = {}
    count = 0
    for items in tqdm(fs.readlines()):
        try:
            item = json.loads(items)
        except Exception as e:
            count += 1
            continue
        uid = str(uuid.uuid4())
        context = item["text"]
        lang = detect_language(context)
        md5 = hashlib.md5(context.encode(encoding='UTF-8')).hexdigest()
        if md5 not in data_dict:
            temp_attr = {
                "department": item["department"] if "department" in item else None,
                "src_url": item["url"] if "url" in item else None,
                "alias": item["alias"] if "alias" in item else None,
                "abstract": item["abstract"] if "abstract" in item else None,
            }

            new_data = {
                "seq_id": uid,
                "title": item["title"] if "title" in item else None,
                "text": context,
                "tags": {},
                "lang": lang,
                "attr": temp_attr,
                "ext": None,
                "dataset": "baiduyidian",
                "batch_name": "20240319",
                "version": "version1",
            }

        else:
            print("重复---",items)
        data_dict[md5] = new_data


    print("saving data....with error:",count)
    for key,val in data_dict.items():
        data = json.dumps(val, ensure_ascii=False)
        fw.write(data + "\n")
