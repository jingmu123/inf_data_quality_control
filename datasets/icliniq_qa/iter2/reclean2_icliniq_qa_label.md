## reclean2_icliniq_qa_label

### 1.无关链接补充

例如：

For further queries consult an **obstetrician and gynaecologist online** \--> https://www.icliniq.com/ask-a-doctor-online/obstetrician-and-gynaecologist

For further doubts consult an **internal medicine physician online** \--> https://www.icliniq.com/ask-a-doctor-online/internal-medicine-physician

补充关键词doubts、queries，补充到删除4：

```
[r'(\n|^)( *For (?:more|further) (?:information|queries|doubts) consult a.*)',r'删除4:<u>\1\2</u>']
```

### 2.新一类的无关链接

例如：

Revert back with the reports to a medical gastroenterologist online.---> https://www.icliniq.com/ask-a-doctor-online/medical-gastroenterologist

Revert back with an image of the current skin condition to a dermatologist online.---> https://www.icliniq.com/ask-a-doctor-online/dermatologist

增加删除5：

```
[r'(\n|^)( *Revert back with (?:the|an).*-->.*)',r'删除5:<u>\1\2</u>']
```

### 3.欢迎来到XX网址的补充

补充是在开头有额外的欢迎词，例如：

Hi, Welcome to icliniq.com.

Hello, Welcome to icliniq.com.

其余一般都是存在缺字多字，例如：

Welcome back to to（多字） icliniq.com. 

Welome（缺字） to icliniq.com.

补充到删除3：

```
[r'(\n|^)(Answered by Dr\..*|#|(?:[Hh]i[,，] *|[Hh]ello[,，] *)?Welc?ome(?: back)? (?:to |in )*(?:the )?[Ii][cl][cl]iniq\.com *\.? *|You can always come back and reach me at icliniq\.com\. *|(?:Best |Kind )?[Rr]egards\.|Patient\'s Query|[Hh]i[,，] *|[Hh]ello[,，] *)',r'删除3:<u>\1\2</u>'],
```

### 4.答案来源类的补充

缺少符号*，导致没有匹配到，例如：

Answered by **Dr. Ramesh Kumar S**

Answered by **Dr. Bharat Udey**

补充符号到删除3：

```
[r'(\n|^)(Answered by \**Dr\..*|#|(?:[Hh]i[,，] *|[Hh]ello[,，] *)?Welc?ome(?: back)? (?:to |in )*(?:the )?[Ii][cl][cl]iniq\.com *\.? *|You can always come back and reach me at icliniq\.com\. *|(?:Best |Kind )?[Rr]egards\.|Patient\'s Query|[Hh]i[,，] *|[Hh]ello[,，] *)',r'删除3:<u>\1\2</u>'],
```