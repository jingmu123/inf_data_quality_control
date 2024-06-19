import nltk
from nltk.tokenize import word_tokenize


# 示例文本，其中包含粘连的单词
text = "Howtosplitthesentencewhere there isnospacebetweenin thesentence"

# 使用word_tokenize函数分割文本
words = nltk.word_tokenize(text)

# 输出结果
print(words)