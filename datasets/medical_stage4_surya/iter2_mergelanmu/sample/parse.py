import json
seq_id_list = []
with open("medical_stage4_surya_label.jsonl","r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item.strip())
        seq_id_list.append(item["seq_id"])
fw = open("../../../../../full_data/medical_stage4_surya/medical_stage4_surya_clean2.jsonl", "w", encoding="utf-8")
with open("../../../../../full_data/medical_stage4_surya/medical_stage4_surya_clean.jsonl","r",encoding="utf-8") as fs:
    for item in fs.readlines():
        items = json.loads(item.strip())
        if items["seq_id"] in seq_id_list:
            continue
        fw.write(item)