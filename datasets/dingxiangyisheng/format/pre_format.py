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

file = "dingxiangyisheng"
batch_name="20240331"
version="version1"
base_dir = f"../../../../full_data/{file}/"
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
        if "lang" in item and item["lang"] != "":
            lang = item["lang"]
        else:
            lang = detect_language(context)
        md5 = hashlib.md5(context.encode(encoding='UTF-8')).hexdigest()
        if md5 not in data_dict:
            if "extra" in item:
                last_version = item["extra"]["last_version_time"] if "last_version_time" in item["extra"] else None
            temp_attr = {
                "category": [item["category"]] if "category" in item else None,
                "publish_time": item["publish_time"] if "publish_time" in item else None,
                "src_url": item["url"] if "url" in item else None,
                "scrape_time": item["scrape_time"] if "scrape_time" in item else None,
                "last_revision_time": last_version,
            }

            new_data = {
                "seq_id": uid,
                "title": item["title"] if "title" in item else None,
                "text": context,
                "tags": {},
                "lang": lang,
                "attr": temp_attr,
                "ext": None,
                "dataset": file,
                "batch_name":batch_name,
                "version": version,
            }

        else:
            category = item["category"] if "category" in item else None
            if category is None:
                print("---重复",items)
            else:
                data_dict[md5]["attr"]["category"].append(category)
                print("adding...")
                print(data_dict[md5]["attr"]["category"])
        data_dict[md5] = new_data


    print("saving data....with error:",count)
    for key,val in data_dict.items():
        data = json.dumps(val, ensure_ascii=False)
        fw.write(data + "\n")
