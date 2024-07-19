# -*- coding: utf-8 -*-
import json
type1={}
type2={}

file="guidelines_wx"
save_file = f"../../../../full_data/{file}/{file}.jsonl"
fw = open(save_file, 'w',encoding="utf-8")

info_dict= {}
with open(f"../../../../full_data/all_guidelines/guidelines_wx/guideliens_collect_result.jsonl") as fs:
    for line in fs.readlines():
        item = json.loads(line)
        title = item["file"]
        info_dict[title] = item

with open(f"../../../../full_data/{file}/{file}_clean.jsonl", "r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        guide_info = info_dict[item["title"]]
        item["tags"] = {
                        "id": item["seq_id"],
                        "clean_iters":"",
                        "quality_score":"",
                        "type1":type1,
                        "type2":type2,
                        "publish_year": guide_info["year_info"],
                        "publish_org": guide_info["org_info"],
                        }

        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")
