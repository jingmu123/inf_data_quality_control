## 1.无关文本 

### 1.1中括号里有数字或者字母类的无关文本，特征出现在句子结尾或单独一行。

例如：D0.02 ~0.13 µ g/L . 2 >0.2 µ g/L 为临界值。 3 >0.5 µ g/L 可以诊断 AMI .[ [ [ [ [ 7 ]【 [ [ [ 4 ][iiiii]| 窄、右肺门肿勃律纵隔增定,右上肺多发班片影”, 子“消炎”治疗效果不佳。发病以未,一般状态可,体重下降不明显。既往身体徒康,无特珠内科合并症。吸烟支 40 支/日×40 年,饮自酒 300ml/dx40 年。家族中无貯痛患者。 [ 2 ]

出现次数较多，整合到之前的删除9里面。

```
([[【][…[\.\* ‘’\"]*?[\dA-Za-z]+ ?\])(?=\n|$) *
```



### 1.2新增英文类的图片索引：

a. Figure10.10

```
 (?<=^)([A-Za-z ]*[Ff]i[Gg](ures?)?[A-Za-z 0-9]*\.?[0-9 ]*?)(?=\n|$)|(?<=\n|。|\.)([A-Za-z ]*[Ff]i[Gg](ures?)?[A-Za-z 0-9]*\.?[0-9 ]*?)(?=\n|$)
```

b. 中文遗漏的图片索引的补充： 图  7-1

补充到删除36里 

### 1.3新增文本中Chapter无关文本的删除

例如：Chapter 3.3.4、Chapter1（切割开正常的序号，避免误删） 6. 定期随访复査,密切关注组织愈合情况,追踪患者外貌及功能的恢复情况。

```
(Chapter[ 0-9]*(\.\d)*[ \n]) 
```

### 1.4 在存在序号的文本前有一串非中文的无关文本

现在根据序号这个特征给它删除。

例如：is the product of evil （无关文本）1. 社交 : 初人社交界

ht（无关文本） 3. 肺部感染 / 早期中央型肺癌所致阻塞性

 ( - ) * W W （无关文本）1. 生殖器官的变化饱满 

### 1.5对无关数字的补充

与之前的页码删除合在一起

例如：放马滩秦简所载死而复生的志怪故事，描绘着与虢太子医案中异质性的复活图像。 ① 

### 1.6 对单独一行的文字以及字母符号删除

 现在在处理换行前对单独一行的文字（允许出现一次），以及字母符号-.(允许出现两次)删除，这些在新的后处理后单独一行一般都是侧边的标题或者其他识别错误。包括部分时候还会被识别成带#标题，一样会去删除。

```
(?<=\n)((##)? ?[A-Za-z.\-]{1,2}|[\u4e00-\u9fa5])(?=\n|$)|(?<=^)((##)? ?[A-Za-z.\-]{1,2}|[\u4e00-\u9fa5])(?=\n|$) 
```

### 1.7增加单独一行出现的疑似人名的无关文本的删除

例如：

( 刘哥作 )

(何黎 )

```
(?<=^)(\( ?[\u4e00-\u9fa5]{1,3} ?\))(?=\n|$)|(?<=\n)(\( ?[\u4e00-\u9fa5]{1,3} ?\))(?=\n|$) 
```

### 

##  2.缺少换行 

### 2.1选择题换行问题

在出现选择题内容的pdf页码时，会出现很多的缺少换行，检查发现部分在全量里是有换行符的，被is_complete错误删除了，现在检查条件增加大写字母A-E.的条件。对全量里就缺少换行的选项。

例如：

C.分泌物经导管排出的称外分泌腺D.分泌物直接入血液的称内分泌腺E.由大量的腺上皮组成

43.能增加细胞接触面积的是 (    )A.基膜

对原数据就缺少换行的添加正则检查换行

### ([\u4e00-\u9fa5)）])([A-E] ?\. ?[\u4e00-\u9fa5]) 

### 2.2在step7里添加换行限制

上一段文本小于等于9长度时，不删除换行，解决了很多的缺少换行问题。 

### 2.3因为上一段文本是英文结尾导致了后面的序号文本缺少换行。

例如：

(1) 患者,女性,25 岁。因“头痛 1 天伴恶心呕吐”就诊,头痛位于右侧,程度较重,呈持续性,有搏动感,爬楼时头痛症状加重.jt (2) 患者既往有类似发作史,休息后头痛症状可缓解,否认有慢性疾病史,否认食物,药物过敏史。

补充增加换行正则，可以解决一部分缺少换行问题 

### 2.4由于is_complete连接词判断导致的换行问题

多音字“的”在作为词语“目的"出现时不是连接词，导致错误连接。

例如：一、实验目的 （需要换行）掌握蛋白质沉淀的常用方法，几种蛋白质沉淀方法的原理。

现在多增加一层判断，创建一个匹配列表（）来避免这类问题。