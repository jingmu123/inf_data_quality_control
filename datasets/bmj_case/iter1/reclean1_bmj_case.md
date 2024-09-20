## reclean_1bmj_case

### 1.网址与无用网址介绍的删除

例如：
http://creativecommons.org/licenses/by-nc/4.0/

This is an open access article .....
http://dx.doi.org/10.1136/bcr-2022-251763

Statistics from Altmetric.com

增加删除1：

```
((?:https?[:：]\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?(?:(?:\n+This is an open access.*)|(?:\n+Statistics from Altmetric.com\n+-*)))
```

### 2.下载图片/打开选项 类的删除

例如:
<img/>

*   Download figure
*   Open in new tab
* Download powerpoint
  增加删除2：

  ```
  (?<=\n)((?:<img\/>\n+)(?:\** *(?:Download figure|Open in new tab|Download powerpoint)\n+)+)
  ```

  

### 3.图片索引删除

例如：
Figure 1

Photograph of the anterior segment of the eye at the first visit (blue sclerae). The sclera was blue in both eyes.
增加删除3：

```
(?<=\n)(\**F[iI][gG][sS]?(?:ures?|URES?|\.) ?[0-9]+([.-]\d*)*[:：.]?(?:\n+.*|.*))
```

### 4.表格类删除

例如：
Table 1

Blood test results
增加删除4：

```
(?<=\n)(Table ?[0-9]+([.-]\d*)*[:：.]?(?:\n+.*|.*))
```

### 5. 结尾固定句式的删除

例如：

Ethics statements（该标题下的所用内容都是无关文本）

Patient consent for publication

Obtained.
增加删除5：

```
(?<=\n)((?:Ethics statements?\n+-*)(?:.*(?:\n|$)*)*)
```

### 6.游览表格的删除

例如：
View this table:

*   View inline
* View popup
  增加删除6：

  ```
  (?<=\n)((?:View this table:\n+)(?:\** *(?:View.*)\n*)+)
  ```

  

### 7.请求权限类的删除

例如：
Request Permissions

If you wish to reuse ...

```
(?:\n|^)(Request Permissions?\n+-*\n+If you wish to.*)
```

### 8补充材料类的删除

例如：

Supplemental material

\[bcr-2023-254632supp001.pdf\]
增加删除8：

```
(?:\n|^)(#* *Supplemental material\n+\\\[.*\\\])
```

### 9.视频类的删除

2.9.1 介绍类例如：
Video 1 Neuro-ophthalmological examination in a 

增加删除11：

```
(?<=\n)(Video *\d+.*)
```

2.9.2 索引类例如：
 improvement in symptoms ( video 1 ). She continued 
增加删除10：

```
(\([^\n()]*(?:[Vv]ideos?|[Tt]able|F[iI][gG][sS]?(?:ures?|URES?)?) *\d+[^\n()]*\))
```

### 10. 页码数字删除

例如：
MFS can present after infections or following vaccinations. 1 Postvaccination

增加删除9：

```
([\.,]\s)(\d{1,3}[\s–,\d{1,3}]{0,20})([A-Z]|$)
```



### 11. 无用标题的删除

例如：

*   Retina
*   Orthopaedics
* Macula
  增加删除12：

  ```
  (?<=\n)((?:\* *.*\n){2,})
  ```

  