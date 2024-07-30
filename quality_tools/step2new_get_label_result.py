# -*- coding: utf-8 -*-
import json
import os
# 定义不同类型的标注等级映射


class ParseLabelResult:
    def __init__(self,need_details=True,base_dir="./",file_name=""):
        # 读取并处理JSON文件
        self.need_details = need_details
        self.m = 10
        self.Beta = 0.01
        self.term_level={
            '错别字': 'level1', '缺少字母': 'level1', '数字误用': 'level1', '多余标点': 'level1', '缺少标点': 'level1', '标点错误': 'level1', '多余空格': 'level1', '空格代替标点': 'level1', '缺少空格-中文': 'level1', '换行空格': 'level1', '语句不通顺': 'level2', '缺少空格-英文': 'level2', '页码/数字': 'level2', '特殊符号': 'level2', '重复符号': 'level2', '缺少换行': 'level2', '序号格式不一致': 'level2', '多余换行': 'level3', '表格格式错误': 'level3', '公式格式错误': 'level3', '术语格式错误': 'level3', '无关文本': 'level3', '页眉': 'level3', '页脚': 'level3', '无关链接': 'level3', '语句/字词重复': 'level3','语句重复': 'level3', '有用性-轻': 'level3', '导航栏': 'level3', '栏目混乱-轻': 'level3', '数据安全': 'level3', '广告': 'level4', '有用性-重': 'level4', '准确性': 'level4', '侧栏': 'level4', '语义不完整': 'level4', '语义冲突': 'level4', '错误删除': 'level4', '表格正文混乱': 'level4', '完整性': 'level4', '栏目混乱-中': 'level4', '专业性': 'level4', '格式杂乱': 'level5', '乱码': 'level5', '文本碎片化/无意义': 'level5', '栏目混乱-重': 'level5', '违反医德': 'level5', '违法': 'level5', '负面价值观': 'level5', '歧视': 'level5', '政治敏感': 'level5'
        }
        self.level_param = {
            "level1": 0.5,
            "level2": 0.42,
            "level3": 0.26,
            "level4": 0.13,
            "level5": 0,
        }
        self.file_path = "{}/{}.jsonl".format(base_dir, file_name)
        self.save_dir = "{}/output".format(base_dir)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def init_val(self):
        self.score_list = []
        self.F = {}
        self.error_list = {}
        self.invalid_count = 0
        self.final_result = {}

    def get_label_info(self,result_info, text_len, ignore_key_list = []):
        # 获取标注结果
        label_info = []
        penaty = 0
        for label_values in result_info["text"]:
            if "province" not in label_values:
                continue
            [p_level1, p_level2] = label_values["province"]
            if p_level2 in ignore_key_list:
                continue

            problem_text = label_values["text"]
            comment = label_values["comment"] if "comment" in label_values else "无"
            assert len(problem_text) > 0

            level = self.term_level[p_level2]
            pena_val = self.level_param[level]
            ##todo: if comment=="全文"
            p_score = ((self.m/text_len)**pena_val)*(1+self.Beta*self.F[p_level2])*100
            penaty += p_score

            type_info = "{}#{}#{}#{}".format(p_level1, p_level2, problem_text, comment)
            label_info.append(type_info)
        result_score = 0 if penaty > 100 else 100-penaty
        return label_info, result_score

    def get_blobal_F(self, con):
        for line in con:
            data = json.loads(line)
            if not data.get("user_name"):
                continue
            # 标注规范性检查
            result_info = data.get("result_info",None)
            if result_info == None:
                continue
            for label_values in result_info["text"]:
                if "province" not in label_values:
                    continue
                [p_level1, p_level2] = label_values["province"]
                self.F[p_level2] = self.F.get(p_level2,0) + 1

    def write_info(self,label_info,user_name,text_info):
        type_all = "#".join(list(set([item.split("#")[1] for item in label_info])))
        type_all = type_all.replace("/","-")
        file_name = "{}/{}_{}_{}.txt".format(self.save_dir, type_all, text_info["seq_id"], user_name)

        with open(file_name, "w", encoding="utf-8") as fw:
            fw.write(text_info["text"])
            fw.write(user_name + "\n")
            fw.write("\n" + "=====" * 20 + "\n")
            try:
                fw.write("\n" + text_info["attr"]["obj_key"] + "\n")
            except:
                pass
            for item in label_info:
                fw.write(item + "\n")

    def process_data(self,ignore_key_list):
        with open(self.file_path, "r", encoding="utf-8") as fs:
            con = fs.readlines()

        self.get_blobal_F(con)
        for line in con:
            data = json.loads(line)
            if not data.get("user_name"):
                self.invalid_count+=1
                continue

            user_name, ids = data["user_name"], data["id"]
            text_info = data["source_info"]
            if "source_info" in text_info:
                text_info = text_info["source_info"]

            dataset = ""
            attr = {}
            if "dataset" in text_info:
                dataset = text_info["dataset"]
            if "attr" in text_info:
                attr = text_info["attr"]


            result_info = data.get("result_info",None)
            if result_info == None:
                self.error_list.setdefault(ids, {"name": user_name, "label_rel": data["result_info"]})
                self.invalid_count += 1
                continue


            # 获取标注结果
            text_len = len(text_info["text"])
            label_info,result_score = self.get_label_info(result_info,text_len,ignore_key_list)
            self.score_list.append(result_score)
            self.final_result[ids] = {
                "seq_id": "null" if "seq_id" not in text_info else text_info["seq_id"],
                "user_name": user_name,
                "label_info": label_info,
                "text":text_info["text"],
                "attr_info": attr,
                "dataset": dataset
            }
            if self.need_details:
                self.write_info(label_info,user_name,text_info)

        with open(f"{self.save_dir}/0000_final_result.json","w",encoding='utf-8') as fw:
            json.dump(self.final_result,fw,ensure_ascii=False,indent=4)

        return self.final_result

    def score_count(self, ignore_key_list=[]):
        self.init_val()
        final_result = self.process_data(ignore_key_list)
        clean_count = 0
        dirty_count = 0
        problem1 = {}
        problem2 = {}

        # for key,value in final_result.items():
        #     if len(value["label_info"]) == 0:
        #         clean_count += 1
        #     else:
        #         dirty_count += 1
        #         for item in value["label_info"]:
        #             item = item.split("#")
        #             level1 = item[0]
        #             level2 = item[1]
        #             problem1[level1] = problem1.get(level1,0) + 1
        #             problem2[level2] = problem2.get(level2,0) + 1

        for item in self.score_list:
            if item == 100:
                clean_count += 1
            else:
                dirty_count += 1

        S1 = round(clean_count/(clean_count+dirty_count),5)*100
        S2 = round(sum(self.score_list)/len(self.score_list),5)

        if len(ignore_key_list) == 0:
            print(f"干净文本:{clean_count}", f"脏文本:{dirty_count}")
            print(f"各纬度问题频次F={self.F}")
            print(f"合格率={S1}%")
        if len(ignore_key_list) == 0:
            print(f"质量分={S2}")
        else:
            print("忽略 \"{}\" 后质量分：{}".format("#".join(ignore_key_list),S2))
        return self.F, S2

def computer_ignore_1(problem_list):
    ignore_score = {}
    for key,val in problem_list.items():
        _, score = pr.score_count([key])
        ignore_score[key] = score
    ignore_score_sorted = sorted(ignore_score.items(),key=lambda x:x[1],reverse=True)
    print(dict(ignore_score_sorted))
    return ignore_score_sorted

def computer_ignore_2(ignore_score_sorted):
    ignore_score = {}
    k = 3
    for i in range(k):
        for j in range(i+1,k):
            ignore_list = [ignore_score_sorted[i][0],ignore_score_sorted[j][0]]
            _, score = pr.score_count(ignore_list)
            key = "#".join(ignore_list)
            ignore_score[key] = score
    ignore_score_sorted = sorted(ignore_score.items(),key=lambda x:x[1],reverse=True)
    print(dict(ignore_score_sorted))

if __name__ == '__main__':

    pr = ParseLabelResult(base_dir="../datasets/medicalpdfv2/iter0/sample", file_name="reclean1_medicalpdfv2_en")
    problem_list,score = pr.score_count() # 默认为空，不忽略key

    ignore_score_sorted = computer_ignore_1(problem_list)
    computer_ignore_2(ignore_score_sorted)

