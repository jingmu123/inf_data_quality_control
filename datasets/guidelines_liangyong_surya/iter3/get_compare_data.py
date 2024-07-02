# import json
# uid_list = []
# with open("sample/guidelines_liangyong_surya_zh_label_fix.jsonl","r",encoding="utf-8") as fs:
#     for item in fs.readlines():
#         item = json.loads(item)
#         uid_list.append(item["seq_id"])
# fw = open("guid_ly_reclean3_fix_raw_data.jsonl","w",encoding="utf-8")
# with open("/Users/mirli/worker/code/code_work/full_data/guidelines_liangyong_surya/drop/guidelines_liangyong_surya_preformat_zh_sample.jsonl","r",encoding="utf-8") as fs:
#     for item in fs.readlines():
#
#         items = json.loads(item)
#         if items["seq_id"] in uid_list:
#             fw.write(item)


import json
uid_list = []
with open("/Users/mirli/worker/code/code_work/inf_data_quality_control/datasets/MSD/iter7/sample/reclean7_msd_en_label.jsonl","r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        uid_list.append(item["seq_id"])
fw = open("MSD_iter7_raw.jsonl","w",encoding="utf-8")
with open("/Users/mirli/worker/code/code_work/full_data/MSD/MSD_preformat.jsonl","r",encoding="utf-8") as fs:
    for item in fs.readlines():

        items = json.loads(item)
        if items["seq_id"] in uid_list:
            fw.write(item)