# -*- coding: utf-8 -*-
import json
type1={}
type2={}
file="nihaixia_zhongyi"
save_file = f"../../../../full_data/{file}/{file}.jsonl"
fw = open(save_file, 'w',encoding="utf-8")

with open(f"../../../../full_data/{file}/{file}_clean.jsonl", "r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        item["tags"] = {
                        "id": item["seq_id"],
                        "clean_iters":"3",
                        "quality_score":"89.6%",
                        "note":"倪海厦中医教授书籍，比较口语化",
                        "type1":type1,
                        "type2":type2,
                        }

        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")
