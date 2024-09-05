## reclean3_cdc问题
### 无关文本：
1.(** Table 1 **)带*的无关内容、(online Technical Appendix Table 4）、( E. chaffeensis [NR_037059], E. ewingii [NR_044747], and E. canis [NR_074386])、(ClinicalTrials.gov identifier NCT03117751)补充。
```
[r'([\(（][  \t\*]*(E\. |online|http:|toll|[Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|Technical)[^\(\)（）\n]*[\)）])', r'删除4-1:<u>\1</u>'],
[r'([\(（][^\(\)（）\n]*(TOX|comm\.|[Nn]o\.|Video|\.gov )[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>'],
```

2.( _10_ _,_ _14_ _,_ _15_ ; **M. Egervärn et al. unpub. data)、(ClinicalTrials.gov identifier NCT03117751)补充。
```
[r'([\(（][^\(\)（）\n]*(TOX|comm\.|[Nn]o\.|Video|\.gov |unpub\. data)[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>'],
```

3.\[** 25 **\]带*的无关内容补充。
```
[r'(\\?\[[\d\-,～~，;\*–—、\s\\_]+\])', r'删除10:<u>\1</u>'],
```

4.Members of the Spanish Fusariosis、94\. Flexner S . Experimental无关段落补充删除。
```
[r'(\n[  \t\*#]*(Of 107 manuscripts|Members of the CDC Brazil Investigation Team:|Top[ \n$]|Public Health and pharmacy:|On This Page|Dial |CAS#:|Image source:|Members of the Spanish Fusariosis|94\\. Flexner S . Experimental)[^\n]*)', r'删除8:<u>\1</u>'],
```

5.人物介绍规则补充。
```
[r'([^\n]*(\n[  \t\*]*(Drs?|M[sr][sr]?|Miss|Prof|Col\. G|Hanna Y|Carmen C\.H|S\.C\.A\.C)\.? (\w+\.)?[^\.]* ?(is|received|[Rr]esearch(ers)?|works?|qualified|directs) )[^\n]+)', r'删除9:<u>\1</u>'], 
```

6.结尾Top，补充：```[r'(\nTop$)', r'删除16:<u>\1</u>'],```

7.无关段落(4 5/16 × 3 7/16 in/11 × 8.7 cm)删除。
```
[r'([^\n]*\(4 5\/16 × 3 7\/16 in\/11 × 8\.7 cm\)[^\n]*)', r'删除17:<u>\1</u>']
```


