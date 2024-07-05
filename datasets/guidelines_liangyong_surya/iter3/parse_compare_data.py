import json
context_list = []
with open("20240628105901330gm1p67x016_R2_1_1_0_0-0_TableSink1","r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        context = item["text"]
        context_list.append(context)

fw = open("Mguid_ly_reclean3_fix_raw_data_pipe.jsonl","w",encoding="utf-8")
with open("guid_ly_reclean3_fix_raw_data.jsonl","r",encoding="utf-8") as  fs:
    for item in fs.readlines():
        items = json.loads(item)
        if items["text"] in context_list:
            fw.write(item)
