import json

import pandas as pd
from tqdm import tqdm


def calculate_char_similarity(title1, title2):
    # 将字符串转为集合，忽略大小写
    set1 = set(title1.lower())
    set2 = set(title2.lower())

    # 计算交集和并集
    intersection = set1.intersection(set2)
    total_chars = len(set1.union(set2))

    # 避免除以0的情况
    if total_chars == 0:
        return 0.0

    # 返回相似度百分比
    return len(intersection) / total_chars


# 加载JSON数据
with open('guidelines_ly_and_wx.jsonl', 'r', encoding='utf-8') as fs:
    lines = fs.readlines()
    print(len(lines))
    result = []
    # 设定相似度阈值
    similarity_threshold = 0.8  # 50% 的字符相似度

    # 初始化簇标志
    cluster_id = 1
    for i, items in enumerate(tqdm(lines)):
        item = json.loads(items.strip())
        item_result = {'seq_id': item['seq_id'], 'title': item['title']}  # 初始化结果
        result.append(item_result)



        if 'cluster' not in item:
            item['cluster'] = cluster_id
            item_result['cluster'] = cluster_id  # 保存簇ID
            cluster_id += 1

        for j in range(i + 1, len(lines)):
            other_item = json.loads(lines[j].strip())
            if 'cluster' not in other_item:
                similarity = calculate_char_similarity(item['title'], other_item['title'])

                if similarity > similarity_threshold:
                    other_item['cluster'] = item['cluster']  # 分配同一簇
                    # 将更新的 `other_item` 保存回到 result 中
                    result.append({
                        'seq_id': other_item['seq_id'],
                        'title': other_item['title'],
                        'cluster': other_item['cluster']
                    })
        print(result)
    # print(result)

    df = pd.DataFrame(result)

    # 将 DataFrame 保存为 CSV 文件
    df.to_csv('guidelines_ly_and_wx_0.8相似度.csv', index=False, encoding='utf-8')
    # 过滤只保留 seq_id, title, cluster 字段
    # filtered_data = [{'seq_id': item['seq_id'], 'title': item['title'], 'cluster': item['cluster']} for item in result]
    #
    # # 将过滤后的数据保存到新的JSON文件
    # with open('guidelines_clustered_filtered.json', 'w', encoding='utf-8') as w:
    #     json.dump(filtered_data, w, ensure_ascii=False, indent=4)
    #
    # print("Filtered clustering done and saved to 'guidelines_clustered_filtered.json'.")
# import json
# import pandas as pd
# from tqdm import tqdm
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
#
# # 加载JSON数据
# with open('guidelines_ly_and_wx.jsonl', 'r', encoding='utf-8') as fs:
#     lines = fs.readlines()
#
#     # 提取 seq_id 和 title
#     data = []
#     titles = []
#     for items in tqdm(lines):
#         item = json.loads(items.strip())
#         data.append({'seq_id': item['seq_id'], 'title': item['title']})
#         titles.append(item['title'])
#
#     # 使用 TfidfVectorizer 将标题转换为 TF-IDF 向量
#     vectorizer = TfidfVectorizer().fit_transform(titles)
#     vectors = vectorizer.toarray()
#
#     # 计算余弦相似度矩阵
#     cosine_sim_matrix = cosine_similarity(vectors)
#
#     # 设定相似度阈值
#     similarity_threshold = 0.7  # 设置余弦相似度的阈值
#
#     # 初始化簇标志
#     cluster_id = 1
#     clusters = [-1] * len(data)  # 初始化所有项的簇ID
#
#     # 开始分簇操作
#     for i in range(len(data)):
#         if clusters[i] == -1:  # 如果该项还没有分配簇
#             clusters[i] = cluster_id  # 分配一个新簇
#             cluster_id += 1
#
#         # 比较当前项与后续项的相似度
#         for j in range(i + 1, len(data)):
#             if clusters[j] == -1 and cosine_sim_matrix[i][j] > similarity_threshold:
#                 clusters[j] = clusters[i]  # 分配同一簇
#
#     # 将簇结果添加到 data 中
#     for i in range(len(data)):
#         data[i]['cluster'] = clusters[i]
#
#     # 转换为 pandas DataFrame
#     df = pd.DataFrame(data)
#     df = df.sort_values(by=['cluster'],ascending=True)
#     # 保存为 CSV 文件
#     df.to_csv('guidelines_ly_and_wx.csv', index=False, encoding='utf-8')
#     print(df['cluster'].max())
#     print("Clustering with TF-IDF and cosine similarity done and saved to 'uptodate_guidelines_tfidf_cosine_similarity.csv'.")

