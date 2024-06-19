# -*- coding: utf-8 -*-
import json
type1={}
type2={}

file=""
save_file = f"../../../../full_data/{file}/.jsonl"
fw = open(save_file, 'w',encoding="utf-8")

with open(f"../../../../full_data/{file}/all_data_preformat.jsonl", "r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        item["tags"] = {
                        "id": item["seq_id"],
                        "clean_iters":"",
                        "quality_score":"",
                        "type1":type1,
                        "type2":type2,
                        }

        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")
