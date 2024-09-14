## crsp_case的清洗

### 1.无关文本

### 1.1 作者贡献|校正 类的删除

例如：

Author contributions|Correction

xxx

xxx（标题以下内容为无关文本，全部删除）

增加删除1：

```
[r'(?:\n|^)(#* *(?:Author contributions|Correction)(?:\n+.*\n*)*)(?:\n|$)',r'删除1：<u>\1</u>']
```

### 1.2 图片索引删除

例如：

Figure 1:

Ultrasound Imaging of the myoma at the age 24. (A) The trans-rectal ultrasound showed a 46 × 35-mm-sized myoma, pressing the endometrium. (B) A 24 × 18-mm-sized myoma was seen at the posterior fundus area.

增加删除2：

```
[r'(?<=\n)(\**F[iI][gG][sS]?(?:ures?|URES?|\.) ?[0-9A-Z]+([.-]\d+)*[:：.]?(?:\n+(?:[^\n ]{1,} ){4,}.*|.*))',r'删除2：<u>\1</u>']
```

### 1.3协议版本 的删除

例如：

8 Protocol version

The study protocol version was 1.1.1; 30.09.2020. Important amendments to the study protocol or other changes will be periodically updated at the trial registration site.

增加到删除3

### 1.4内部审查委员会批准 的删除

例如：

Internal review board approval

--------------------------------------------------

The case report was reviewed and approved by the local Internal Review Board. The patient signed an informed consent form for all the procedures described in the manuscript and signed a consent form for its publication.

增加到删除3

### 1.5致谢内容的删除

例如：

Acknowledgements

---------------------------------

We thank the patient and his son for his cooperation in writing this case report.

增加到删除3

### 1.6知情同意书 / 未引用参考 / 补充信息 的删除

例如：

```
### 3.1 Uncited reference

<sup><a>[9]</a></sup>.

#### 4.3.1 Informed consent

The chief investigator (CI; AM) obtained consent from the participating pharmacists.

4\. Supplementary information
-----------------------------

**Checklist**: OA\_Guidelines checklist.

**Citation of Protocol Registration:** Binyam Tariku Seboka, Samuel Hailegebreal, Delelegn Emwodew Yehualashet, Belay Negasa, Getanew Aschalew Tesfa, Girum Gebremeskel Kanno, Robel Hussen Kabthymer. A systematic review of methods used in the spatial analysis of diarrhea. PROSPERO 2021 CRD42021292523

Available\_from: https://www.crd.york.ac.uk/prospero/display\_record.php?ID=CRD42021292523

```

这类的删除会持续到下一个小标题结束

增加删除3：

```
[r'(?:\n)((?: *\d* *Protocol version *\n-+\n|Internal review board approval *\n-+\n|Acknowledgements *\n-+\n|#* *\d+\.\d+ *Informed consent|#* *\d+\.\d+ *Uncited reference|\d+\\\. *Supplementary information\n-+\n)(?:.*\n)*?)(.*\n-+\n)',r'删除3：<u>\1</u>\n\2']
```

### 1.7参考类的删除

例如：

Available from: https://inplasy.com/inplasy-2022-1-0098/.

增加删除4：

```
[r'(?:\.)( *Available from:.*)',r'删除4：<u>\1</u>'],
```

### 1.8注册号的删除

例如： (registration number: CRD42021240027)

增加删除5：

```
[r'(\([^\n()]*(?:registration number|ANZCTR)[:：][^\n()]*\))',r'删除5：<u>\1</u>']
```

### 1.9参见图/附录类的删除

例如： (Graph 2)， (see Appendix 2 for imaging protocol, https://links.lww.com/MD-CASES/A12)

增加删除6：

```
[r'(\([^\n()]*(?:Graph|[Aa]ppendix)[^\n()]*\))',r'删除6：<u>\1</u>']
```

### 1.10无用数字的删除

例如:

```
<sup>[</sup><sup><sup><a>8</a></sup></sup><sup>]</sup> 
```

增加删除7：

```
[r'(<sup>\[<\/sup><sup><sup><a>\d+(?:[-,，\–\-—]\d+)*<\/a><\/sup><\/sup><sup>\]<\/sup>)',r'删除7：<u>\1</u>']
```