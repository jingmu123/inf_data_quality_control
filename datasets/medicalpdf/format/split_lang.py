import json
import sys
file = "medicalpdf"
base_dir = f"../../../../full_data/{file}/"
base_file = f"{base_dir}/{file}_preformat.jsonl"
save_file = f"{base_dir}/{file}_preformat.jsonl"

fw_zh = open(f"{base_dir}/{file}_preformat_zh.jsonl", "w", encoding="utf-8")
fw_en = open(f"{base_dir}/{file}_preformat_en.jsonl", "w", encoding="utf-8")

# fw_en = open("guidelines_liangyong_surya_preformat_en.jsonl","w",encoding="utf-8")
with open(base_file,"r",encoding="utf-8") as fs:
    item = fs.readline()
    count  = 0
    while item:
        count += 1
        if count % 10000 ==0:
            print(count)
    # for item in tqdm(fs.readlines()):
        items = json.loads(item.strip())
        if items["lang"] == 'zh':
            fw_zh.write(item)
        else:
            fw_en.write(item)
        item = fs.readline()