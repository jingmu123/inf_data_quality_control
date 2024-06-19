import json
fw = open("medical_report_quality.jsonl", "w",encoding="utf-8")
with open("prompt_gpt4_gpt4_0.jsonl", "r",encoding="utf-8") as fs1:
    gpt4_con = fs1.readlines()
with open("reuslt_answer_med7.jsonl","r",encoding="utf-8") as fs2:
    med7_con = fs2.readlines()
for idx,item in enumerate(gpt4_con):
    if idx >= len(med7_con):continue
    med7_item = med7_con[idx]
    gpt4_item = json.loads(item)
    med7_item = json.loads(med7_item)
    for node in gpt4_item["raw_data"]["result"]:
        try:
            node["attr"]["note"] = ""
        except:
            node[",attr"]["note"] = ""
            node["attr"] = node[",attr"]
    for node in med7_item["result"]:
        try:
            node["attr"]["note"] = ""
        except:
            node[",attr"]["note"] = ""
            node["attr"] = node[",attr"]
    data = {
        "gpt4_data": gpt4_item,
        "med7_data": med7_item,
    }
    data = json.dumps(data,ensure_ascii=False)
    fw.write(data+"\n")




