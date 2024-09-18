## reclean2_crsp_case

### 1.图片索引正则修改

例如：

Figure 1:

Flowchart of Literature selection.

Figure 2.:

(A and B) Axial and .....

因为正则出错导致出现部分没有删除图片描述的情况，现在已经修复

```
(?<=\n)(\**F[iI][gG][sS]?(?:ures?|URES?|\.) ?[0-9A-Z]+([.-]\d*)*[:：.]?(?:\n+.*|.*))
```

### 2.致谢删除

出现一例致谢没有删除，原因是我把致谢与其他类似特征的无关标题与内容的删除放在一起，结果出现两个标题叠在一起，导致只删除了第一个

删除3：<u>8 Protocol version

The study protocol version was 1.1.1; 30.09.2020. Important amendments to the study protocol or other changes will be periodically updated at the trial registration site.

</u>

Acknowledgments（漏掉了）

The authors would like to acknowledge the ongoing support provided by Dr Gaetano Cardiel, President of SOFAD SRL, Dr Gioacchino Nicolosi, President of Federfarma Sicilia, the Sicily region, and Dr Antonio Gaudioso, Secretary-General of Active Citizenship. The research team is deeply thankful to Dr. Izabella Penier for editing the manuscript and Dr. Miland Joshi, a senior research fellow in statistics from the Lancashire Clinical Trial Unit, for checking the power calculation and sample size.

现在把致谢部分单独拿出来删除

```
[r'(?<=\n)((?:Acknowledge?ments *\n-+\n)(?:.*\n)*?)(.*\n-+\n)',r'删除8：<u>\1</u>\n\2'],
```

### 3.页码删除

有一个上一次清洗没有注意到的格式，例如：

```
<sup>[</sup><sup><sup><a>2</a></sup></sup><sup>,</sup><sup><sup><a>3</a></sup></sup><sup>]</sup>
```

展示在标注平台上是[2,3],但是实际上是一类新的格式，现在补充到删除7：

```
[r'(<sup>\[(<\/sup><sup><sup><a>\d+(?:[-,，\–\-—]\d+)*<\/a><\/sup><\/sup><sup>,?)+\]<\/sup>)',r'删除7：<u>\1</u>'],
```

### 4.无用表格的删除

例如：

Table 1:

Time schedule.

Table 1:

The time schedule of the study. AGEs: advanced glycation end products; d-ROMs: diacron-reactive oxygen metabolites; isCGM: intermittently scanned continuous glucose monitoring.

增加删除9：

```
[r'(?<=\n)(\**Table ?[0-9A-Z]+(?:[.-]\d*)*[:：](?:\n+.*))',r'删除9：<u>\1</u>']
```