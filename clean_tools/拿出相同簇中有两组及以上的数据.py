import json
import pandas as pd
from tqdm import tqdm
import re
tqdm.pandas()


# 清洗 title 的函数
def clean_title(title):
    new_title = re.sub(r'[\(（](\d+年?版?|更新版?|\.V|修订版?)[\)）]', '', title.strip())

    new_title = re.sub(
        r'(\([^\d\(\)]*\d{4}[^V\d\(\)]*\))|(（[^\d（）]*\d{4}[^V\d（）]*）)|(【[^【】]*领域[^【】]*】)|(\(\d{4}[^\d][^V\(\)]*\))|(（\d{4}[^\d][^V\(\)]*）)',
        r'', new_title)
    new_title = re.sub(r'\d+年版?|(-)|(更新解?读?)$', '', new_title)
    new_title = re.sub(r'(^[_]{0,}\d{4}[\s+-])|(^_)', r'', new_title)
    # new_title = re.sub(r'', '', new_title)
    new_title = re.sub(r'([^\d])(\d{4}$)', r'\1', new_title)
    new_title = re.sub(r'^[\+\-_]', '', new_title)
    new_title = re.sub(r'[\(（](V\s?\d)[\)）]',r'',new_title)
    return new_title


# 标记重复项的函数
def mark_is_delete(df):
    grouped = df.groupby('new_cluster')

    # 遍历每个簇
    for cluster_id, group in grouped:

        seen_titles = set()
        for idx, row in group.iterrows():
            new_title = re.sub(r'[\s／_+-]',r'',row['new_title'].lower().strip())
            # print(new_title)
            # 如果 new_title 没有出现过，记录为未删除（is_delete=0）
            if new_title not in seen_titles:
                seen_titles.add(new_title)
            else:
                # 如果已经出现过，则标记为重复（is_delete=1）
                df.at[idx, 'is_delete'] = 1
    return df
df = pd.read_csv('guidelines_ly_and_wx_0.8相似度.csv', encoding='utf-8')
df['new_title'] = df['title'].apply(clean_title)
df['is_delete'] = 0
clustered_groups = df.groupby('cluster').filter(lambda x: len(x) > 1)       # 这一步的过滤是过滤簇size=1的簇

# 初始化簇合并映射表
cluster_mapping = {}
# 遍历每个簇，合并相似的簇
for cluster_id, group in clustered_groups.groupby('cluster'):
    # 获取当前簇的所有 seq_id
    seq_ids = set(group['seq_id'])
    merged_into = None
    for existing_cluster, existing_seq_ids in cluster_mapping.items():
        if not seq_ids.isdisjoint(existing_seq_ids):
            # 如果找到有重叠的簇，合并簇
            cluster_mapping[existing_cluster] = existing_seq_ids.union(seq_ids)
            merged_into = existing_cluster
            break
    if merged_into is None:
        cluster_mapping[cluster_id] = seq_ids
merged_df_list = []
for cluster_id, seq_ids in cluster_mapping.items():
    # 获取当前簇的所有条目
    merged_group = clustered_groups[clustered_groups['seq_id'].isin(seq_ids)]
    # 为这些条目分配新的合并簇 ID
    merged_group['new_cluster'] = cluster_id
    merged_df_list.append(merged_group)
merged_df = pd.concat(merged_df_list)
merged_df = merged_df.drop_duplicates(subset=['seq_id'])
merged_df.to_csv('guidelines_ly_and_wx\guidelines_ly_and_wx_merged_clusters.csv', index=False, encoding='utf-8')             # 输出的是合并簇后的新表

# 对相同簇中的 new_title 进行对比，并生成 is_delete 列
merged_df = mark_is_delete(merged_df)
merged_df.to_csv('guidelines_ly_and_wx/guidelines_ly_and_wx_filtered1.csv', encoding='utf-8', index=False)   # 输出的是合并簇后且将重复的打上1

# 筛选 is_delete 字段为 1 的数据
filtered_df = merged_df[merged_df['is_delete'] == 1]
# 根据 seq_id 进行去重
unique_filtered_df = filtered_df.drop_duplicates(subset=['seq_id'])
# 统计去重后的数据条数
count = unique_filtered_df.shape[0]
print(count)

# 删除 is_delete 为 1 的行
merged_df = merged_df[merged_df['is_delete'] == 0]
# 再次过滤簇中数据只有1条的簇
merged_df = merged_df.groupby('new_cluster').filter(lambda x: len(x) > 1)   # 这两部操作将会过滤掉直接能通过代码清洗title字段 判断能输出的

merged_df.to_csv('guidelines_ly_and_wx/guidelines_ly_and_wx_filtered2.csv', encoding='utf-8', index=False)    # 输出的是再次过滤掉1之后的表

remaining_clusters = merged_df['new_cluster'].nunique()
print(remaining_clusters)
# 找出每个簇的大小
cluster_sizes = merged_df.groupby('new_cluster').size()
# 找出最大簇的大小
max_cluster_size = cluster_sizes.max()
print(max_cluster_size)

# 后续操作是为了连上text字段
merged_df = merged_df.groupby('new_cluster')
# 读取 JSONL 文件并存储 seq_id 和 text 到字典中
json_data = {}
with open('guidelines_ly_gptpdf.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line.strip())
        json_data[item['seq_id']] = item['text']

# 创建并写入 JSONL 文件
with open('guidelines_ly_and_wx/guidelines_ly_and_wx_clustered_data.jsonl', 'w', encoding='utf-8') as outfile:
    # 处理每个簇
    for cluster_id, group in merged_df:

        cluster_info = {'new_cluster': cluster_id,'cluster_item':[]}
        for idx, row in group.iterrows():
            seq_id = row['seq_id']
            title = row['title']
            new_title = row['new_title']
            text = json_data.get(seq_id, '')  # 从字典中获取文本
            # 将每条记录的信息添加到簇字典中
            cluster_item = {'seq_id': seq_id,'title': title,'new_title': new_title, 'text': text}
            # 将每个簇的项目添加到 cluster_info 中
            cluster_info['cluster_item'].append(cluster_item)
        # 将每个簇的 JSON 对象逐条写入 JSONL 文件
        json.dump(cluster_info, outfile, ensure_ascii=False)
        outfile.write('\n')