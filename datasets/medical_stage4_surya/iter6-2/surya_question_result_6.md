# reclean5标注结果分析
## 一、无关文本
#### 共计384条

#### 1.每个句子或小句子之间有无关数字+空白或换行符
- blend of air and oxygen. <u>46
</u>In the absence of
- initiated with air. <u>44,45 </u>There are
- initiated with air, <u>44,45 </u>there are  (误删可能性大)
- initiated with air. <u>44–45 </u>There are  (误删可能性大)
- (initiated with air) <u>44–45 </u>  (误删可能性大)
- 
#### -已解决大部分问题
```
[r'([\.,，)]\s)(\d+(\s?[\.,–，]?\s?\d+)?[\s]?)([A-Za-z\s]?)',  r"\1删除无关数字:<u>\2</u>\4"]
```


## 二、多余换行
#### 共计328条

#### 1.两个单词之间多余换行符
- the National<u>\n</u>
Military Command System Information<u>\n</u>
Processing\n

#### 2. [,)]和单词之间多余换行
- (Elsevier B.V.,<u>\n</u>
Amsterdam, Netherlands)

#### -已解决大部分问题
```
[r'([A-Za-z,](\w+)?)(\n+(【\d+】)?)([A-Za-z,.](\w+)?)', r'\1删除多余换行:<u>\3</u>\5']
```

## 三、缺少换行
#### 共计180条

#### 1.在句末.后，是否需要换行没有明确规则，与多余换行没有明确界限，比较困难


## 四、错误删除
#### 共计143条


## 五、序号格式不一致
#### 共计127条

#### 1.缺少序号