import json
import os
#dict_keys(['id', 'user_id', 'user_name', 'task_id', 'source_info', 'result_info', 'finished', 'dropped', 'create_time', 'update_time'])
# 定义不同类型的标注等级映射
level_mapping = {
    "type1": "语法规范性",
    "type2": "格式规范性",
    "type3": "文本干净度",
    "type4": "语义有效性",
    "type5": "安全无毒性",
    "type6": "信息丰富性"
}


def get_label_info(result_info):
    # 获取标注结果
    label_info = []
    for label_name, label_values in result_info.items():
        if label_name == "type0": continue
        if label_name in ["startTime","endTime","cost"]:continue
        level_name = level_mapping[label_name]
        if label_values==None:
            label_values = ""
        for item in label_values.split("\n"):
            label_item = item.split("#")
            if len(label_item) == 2:
                label_item = [label_item[0],0,0,label_item[1]]
            if len(label_item) != 4:
                continue

            type_info = "{}#{}#{}#{}#{}".format(level_name, label_item[0].lstrip("").strip(""), label_item[1],
                                             label_item[2],label_item[3])
            # if "语义不完整" in type_info:
            #     continue
            # if "无关文本" in type_info:
            #     continue
            # if "有用性" in type_info: # version4 版本有做
            #     continue
            # if "多余换行" in type_info: # version4: 缺少： 不该换的地方换了
            #     continue
            # if "缺少换行" in type_info: # (## 换行)
            #     continue
            # if "错误删除" in type_info:
            #     continue
            # if "序号" in type_info:
            #     continue
            # if "栏目混乱" in type_info:
            #     continue
            if "序号格式" in label_info:
                continue
            label_info.append(type_info)
    return label_info



# 读取并处理JSON文件
final_result = {}
error_list = {}
# <<<<<<< HEAD
base_dir = "../datasets/medical_stage4_surya/iter8/sample"
file_path = "{}/{}.jsonl".format(base_dir,"reclean8_stage4_surya")
# =======
base_dir = "../datasets/medicalpdf/iter2/sample"
file_path = "{}/{}.jsonl".format(base_dir,"reclean2_medicalpdf_zh")
# >>>>>>> fd84715d2d176ac72b546c6039b7eca10cebc99c
save_dir = "{}/output".format(base_dir)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
with open(file_path, "r", encoding="utf-8") as fs:
    for line in fs.readlines():
        data = json.loads(line)
        if not data.get("user_name"):
            continue

        user_name, ids = data["user_name"], data["id"]
        text_info = data["source_info"]
        # if ids != 387962:continue
        if "source_info" in text_info:
            text_info = text_info["source_info"]

        dataset = ""
        attr = {}
        if "dataset" in text_info:
            dataset = text_info["dataset"]
        if "attr" in text_info:
            attr = text_info["attr"]

        # dataset, attr = text_info["dataset"], text_info["attr"]


        # 标注规范性检查
        result_info = data.get("result_info",None)
        # print(result_info)
        if result_info == None:
            error_list.setdefault(ids, {"name": user_name, "label_rel": data["result_info"]})
            continue
        # 获取文本
        # yema_info = extract_text(yema_info,text_info)
        #print(yema_info)
        # 获取标注结果
        label_info = get_label_info(result_info)
        print(label_info)

        final_result[ids] = {
            "seq_id": "null" if "seq_id" not in text_info else text_info["seq_id"],
            "user_name": user_name,
            "label_info": label_info,
            "text":text_info["text"],
            "attr_info": attr,
            "dataset": dataset
        }

        type_all = "#".join(list(set([item.split("#")[1] for item in label_info])))
        file_name = "{}/{}_{}_{}.txt".format(save_dir,text_info["seq_id"],type_all,user_name)
        with open(file_name, "w",encoding="utf-8") as fw:
            fw.write(text_info["text"])
            fw.write(user_name+"\n")
            fw.write("\n"+"====="*20+"\n")
            fw.write("\n"+text_info["attr"]["obj_key"]+"\n")
            for item in label_info:
                fw.write(item+"\n")



os.makedirs(save_dir, exist_ok=True)
with open(f"{save_dir}/en_0131.json","w",encoding='utf-8') as fw:
    json.dump(final_result,fw,ensure_ascii=False,indent=4)

clean_count = 0
dirty_count = 0
problem1 = {}
problem2 = {}
for key,value in final_result.items():
    #if value["user_name"] != "曾垂松": continue
    if len(value["label_info"]) == 0:
        clean_count += 1
    else:
        dirty_count += 1
        for item in value["label_info"]:
            item = item.split("#")
            level1 = item[0]
            level2 = item[1]
            problem1[level1] = problem1.get(level1,0) + 1
            problem2[level2] = problem2.get(level2,0) + 1
print(clean_count,dirty_count)
quality = round(clean_count/(clean_count+dirty_count),5)
print(f"干净文本:{clean_count}",f"脏文本:{dirty_count}",f"合格率={quality}")
print(problem1,problem2)

