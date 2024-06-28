from sklearn.feature_extraction.text import CountVectorizer
import re
import jieba
import numpy as np

stopwords = [line.strip() for line in open('hit_stopwords.txt', 'r', encoding='utf-8').readlines()]

def common_ngrams(text1, text2, ngram_range=(1, 3)):
    """找出两个文本中共有的N-grams"""
    text1_list = list(jieba.cut(text1, cut_all=False))
    text1_list = [w for w in text1_list if w not in stopwords]
    text2_list = list(jieba.cut(text2, cut_all=False))
    text2_list = [w for w in text2_list if w not in stopwords]
    if len(text1_list) < 5:
        return [], 0, 0
    print((text1_list))
    print(text2_list)
    text1 = " ".join(text1_list)
    text2 = " ".join(text2_list)
    vectorizer = CountVectorizer(analyzer="word", ngram_range=ngram_range)
    matrix = vectorizer.fit_transform([text1, text2])
    feature_array = np.array(vectorizer.get_feature_names_out())

    # 获取两个文本的特征向量
    text1_vector, text2_vector = matrix.toarray()

    # 找出两个向量都有的特征（即N-grams）
    common_ngrams = feature_array[
        np.logical_and(text1_vector > 0, text2_vector > 0)
    ]
    common_ngrams_list = list(common_ngrams)

    common_length = 0
    for common_ngrams in common_ngrams_list:
        common_length += len(common_ngrams)
    common_ratio = common_length / len("".join(text1_list))
    if common_ratio < 0.5:
        return [], 0, 0
    return common_ngrams_list, common_length,common_ratio


from scipy.spatial import distance
def jaccard(text1, text2):
    """找出两个文本中共有的N-grams"""
    text1_list = list(jieba.cut(text1, cut_all=False))
    text1_list = [w for w in text1_list if w not in stopwords]
    text2_list = list(jieba.cut(text2, cut_all=False))
    text2_list = [w for w in text2_list if w not in stopwords]
    return 1 - distance.jaccard(text1_list, text2_list)


def get_jaccard_score(source_text, target_text):
    def jaccard_similarity(set1, set2):
        intersection_cardinality = len(set1.intersection(set2))
        union_cardinality = len(set1.union(set2))
        return intersection_cardinality / union_cardinality

    text1_list = list(jieba.cut(source_text, cut_all=False))
    text1_list = set([w for w in text1_list if w not in stopwords])
    if len(text1_list) < 2:
        return 0
    text2_list = list(jieba.cut(target_text, cut_all=False))
    text2_list = set([w for w in text2_list if w not in stopwords])
    if len(text2_list) < 3:
        return 0
    try:
        score = jaccard_similarity(text1_list, text2_list)
    except:
        print(text1_list, text2_list)
        exit(0)
    return score

# text1 = "由于我是一个模型"
# text2 = "小肠肿瘤由于恶变率高，局限于小肠或伴有局部转移的，治疗室需行小肠及肠系膜淋巴根治术在模型分析问题与搜索资料的时候 或者 在模型流式回答的时候 ，切换至其他的历史对话，再切换回来，这时候会提示已停止生成，想问下这个可以容许吗@韩潇潇   emm主要也是我看手机端报告解读那里，在解读时候哪怕会话切走了，但是再切回来也是可以正常展示解读的"
# # res = common_ngrams(text1,text2)
# res = jaccard(text1,text2)
# print(res)
# a={'原发性', '发生', '内', '简称', '胆管', '恶性肿瘤', '肝', '肝癌', '肝细胞', '细胞'}
# b={'2%', '恶性肿瘤', '一种', '~', '5%', '少见', '阴蒂', '类型', '发生', '病理', '上皮细胞', '所有', '鳞', '癌', '仅', '状', '外阴', '占', '阴唇', '主要', '小阴唇', '部位', '女性', '如大', '生殖系统', '癌症', '癌是'}
a="总的来说，尽管许多患者预后良好，但一部分重症患者可能存在某些后遗症。"
b="# 新型冠状病毒感染\n"
score = get_jaccard_score(a, b)
print(score)