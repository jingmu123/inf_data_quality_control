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

file = "kepuyixia"
batch_name="20240321"
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
        #context = item["text"]
        context = json.loads(item["json_"])["description"]
        lang = ""
        md5 = hashlib.md5(context.encode(encoding='UTF-8')).hexdigest()
        if md5 not in data_dict:
            attr = {
                "scrape_time": item["scrape_time"] if "scrape_time" in item else None,
                "create_time": item["create_time"] if "create_time" in item else None,
                "src_url": item["src_url"] if "src_url" in item else None,
                "publish_time": item["publish_time"] if "publish_time" in item else None,
                "poster":item["extra"]["videoData"]["poster"] if "extra" in item and "videoData" in item["extra"] and "poster" in item["extra"]["videoData"] else None,
                "video": item["extra"]["videoData"]["video"] if "extra" in item and "videoData" in item["extra"] and "video" in item["extra"]["videoData"] else None
            }
            if attr["video"] == None:
                continue
            title = item["title"] if "title" in item else None
            if title is not None:
                title = title.replace("【科普一下】", "")
            new_data = {
                "seq_id": uid,
                "title": title,
                "text": context,
                "tags": {
                    "id": uid,
                },
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
