## reclean1_icliniq_qa

### 1.回答人员+文章由xxx审查 的删除

例如：

Answered by

**Dr. Sushil Kakkar**

and medically reviewed by iCliniq medical review team.

增加删除1：

```
[r'(\n|^)(Answered by *\n+\*+Dr\..*\*+ *\n+and.*)',r'删除1:<u>\1\2</u>'],
```

### 2.发布时间+审查时间 删除

例如：

This is a **premium question & answer** published on Jul 06, 2018 and last reviewed on: Jul 18, 2023

增加删除2：

```
[r'(\n|^)(Answered by *\n+\*+Dr\..*\*+ *\n+and.*)',r'删除1:<u>\1\2</u>'],
```

### 3.欢迎词类删除

例如：

Hi,

Hello,

Welcome back to icliniq.com.

Welcome to icliniq.com.

You can always come back and reach me at icliniq.com.

Regards.

Best regards.

Kind regards.

类似这类的无关文本，比较短句式比较固定，增加删除3

```
[r'(\n|^)(Answered by Dr\..*|#|[Hh]i[,，]|[Hh]ello[,，]|Welcome(?: back)? to icliniq\.com\. *|You can always come back and reach me at icliniq\.com\. *|(?:Best |Kind )?[Rr]egards\.|Patient\'s Query)',r'删除3:<u>\1\2</u>'],
```

### 4.更多信息、链接类的删除

例如：

For more information consult a hematologist online.

For further information consult a nephrologist online --> https://www.icliniq.com/ask-a-doctor-online/nephrologist

增加删除4

```
[r'(\n|^)( *For (?:more|further) information consult a.*)',r'删除4:<u>\1\2</u>']
```