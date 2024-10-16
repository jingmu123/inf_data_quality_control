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

file = "medicalpdf"
batch_name="20240628"
version="version0"
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
        if "seq_id" not in item:
            uid = str(uuid.uuid4())
        else:
            uid = item["seq_id"]
        context = item["text"]
        if "lang" in item and item["lang"] != "":
            lang = item["lang"]
        else:
            try:
                lang = detect_language(context)
            except:
                lang = "None"
        md5 = hashlib.md5(context.encode(encoding='UTF-8')).hexdigest()
        if md5 not in data_dict:
            # todo
            attr = item["attr"]
            attr["page_num"] = item["page"]
            attr["obj_key"] = item["attr"]["obj_key"].replace(".json","")
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
            continue
        data_dict[md5] = new_data

    print("saving data....with error:",count)
    for key,val in data_dict.items():
        data = json.dumps(val, ensure_ascii=False)
        fw.write(data + "\n")
