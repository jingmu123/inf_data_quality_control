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

file = "drug_detail_zh"
batch_name="20240328"
version="version1"
base_dir = f"../../../../full_data/{file}/"
base_file = f"{base_dir}/{file}_all.jsonl"
save_file = f"{base_dir}/{file}_preformat.jsonl"
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
        if "lang" in item and item["lang"] != "":
            lang = item["lang"]
        else:
            lang = detect_language(context)
        md5 = hashlib.md5(context.encode(encoding='UTF-8')).hexdigest()
        if md5 not in data_dict:
            # todo
            attr = {}
            new_data = {
                "seq_id": uid,
                "title": item["title"] if "title" in item else None,
                "text": context,
                "tags": {},
                "lang": lang,
                "attr": attr,
                "ext": None,
                "dataset": file,
                "batch_name":batch_name,
                "version": version,
            }
        else:
            print("重复---",items)
        data_dict[md5] = new_data

    print("saving data....with error:",count)
    for key,val in data_dict.items():
        data = json.dumps(val, ensure_ascii=False)
        fw.write(data + "\n")
