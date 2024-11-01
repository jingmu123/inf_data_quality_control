## reclean2_pmc_patients_label

### 1.无关括号内容

例如：

status (
). Although括号内容是换行符

例如：

standstill (Video ).
 cancers (table ).

补充到删除3：

```
[r'([（\(\[] *(?:删除换行\d+(?: and 删除换行\d+)?|(?:Video|table|see) *\d*|\n)? *[\)\]）])',r'删除3:<u>\1</u>'],
```

### 2.患者提供书面知情同意类

例如：

The patient provided written informed consent for the publication of his clinical details and images.

增加删除6：

```
[r'(\n *|^ *|\. *)(The patient provided written informed[^\n\.]*\.? *(?:\n|$)|The imaging findings are presented in Figure *\.? *(?:\n|$))',r'\1删除6:<u>\2</u>']
```