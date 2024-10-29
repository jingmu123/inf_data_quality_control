## recean1_pmc_patients

### 1.多余换行

#### 小写字母与小写字母之间没有结尾符，例如：

Transvaginal imaging was performed to better evaluate the （多余换行）uterus and the adnexa.

增加删除换行1：

```
[r'([a-z，,0-9’;()/] *(?:>|<|\+|\–|%|\'|≥|=|≤|-|&|~|"|\*|)* *)(\n+(?: *\n)?)( *(?:>|<|\+|:|%|\'|≥|=|≤|&|~|"||×)* *(?:(?:["“,，./a-z‘)][^.])|(?:\$?\d+[^.\)][^.\\])|(?:[\(\[](?:[^\(\)\n]+[^\(\)\n0-9]+|[^\(\)\n0-9]+[^\(\)\n]+)[\)\]])))',r'\1 删除换行1 \3'],
```



#### 括号内容出现多余换行，例如：

There is a trace amount of fluid within the tract (less than （多余换行）1 cc).

增加删除换行2：

```
[r'(\n|^)(.*\([^\n()]*)(\n+)([^\n()]*\).*)',r'\1\2 删除换行2 \4'],#括号内容分离
```



#### 小写字母与大写字母之间没有结尾符，例如：

occurred, which extended antegradely and also retrogradely into the Sinus of
Valsalva (Dunning dissection class I) (). A 3.5×29 mm stent (Partner, Lepu Medical Technology,

增加删除换行3：

```
[r'(\n|^)( *(?:[^\n•●© ]{1,} +){4,}[^\n ]*[a-z，,0-9’;(/%\-+] *[-&*#]* *)(\n+)( *[A-Z][^.#\n•●©·:： ]*[^#\n•●©·:： ]*(?:(?: (?:(?:\d[:：]\d)*[^\n•●©·])*[^\n:：][^\n:：](?:\n|$))|(?: *\n| *$)))',r'\1\2 删除换行3 \4'],#小大写
```



#### 大写字母与小写字母之间没有结尾符，例如：

Once again CTA
was repeated, 

增加删除换行4：

```
[r'(\n|^)( *(?:[^\n•●©· ]{1,} +){5,}[^\n ]*[A-Z] *[-&]* *)(\n+)( *[-&]* *[a-z，,0-9’;)/][^.][^#\n•●©·:：.]+(?:(?:\d[:：]\d)*[^\n•●©·])*(?:\n|$))',r'\1\2 删除换行4 \4'],#大小写
```



#### 大写字母与大写字母之间没有结尾符，例如：

In the pathology department of UZ
Leuven, unusual or poorly

增加删除换行5：

```
[r'(\n|^)( ?(?:[^\n•●© ]{1,} +){5,}[^\n]+[A-Z] *)(\n+)( *[A-Z][^\n\. ]*[^:：\-] +(?:(?:(?:[^\n•●©:： ]{1,} +){5,}.*)|(?:[^\d\.\n:：]{2,}\. *(?:\n|$)))|(?: *\(.{3,}\)))',r'\1\2 删除换行5 \4'],#大大写
```



#### 小写字母与非序号数字之间没有结尾符，例如：

 diagnosis and treatment for nasal lymphoma
2.5 years prior. 

增加删除换行6：

```
[r'([A-Za-z，,0-9’;()/] *(?:>|<|\+|\–|%|\'|≥|=|≤|-|&)* *)(\n+(?: *\n)?)( *(?:>|<|\+|:|%|\'|≥|=|≤|&|~)* *(?:(?:\$?\d+\.\d+)|(?:\$?\d+ *[,，])|(?:\$?\d+ *\. *\n)) *)',r'\1 删除换行6 \3'],#数字
```



### 2.句末图片索引类

例如：

......lateral leads (ST elevation in V2, I, and augmented vector right (AVL)). （从这里开始是无关文本）See Figure .

增加删除1：

```
[r'([\.,，])( (?:See Figure|Fig) \.)',r'.删除1:<u>\2</u>'],
```



### 3.研究来源类的删除

例如：

This study was approved by the Ethics Committee of Orthopedic Surgery Department, Imam Khomeini Hospital, Tehran, Iran and a written consent was signed by the parents.

增加删除2：

```
[r'(\n|^)((?:The|This) (?:case report|study) was approved by.*)',r'\1删除2:<u>\2</u>'],
```



### 4.空序号与无关索引的删除

例如：

（）、[]、（Video 7）...

增加删除3：

```
[r'([（\(\[] *(?:删除换行\d+(?: and 删除换行\d+)?|Video *\d+)? *[\)\]）])',r'删除3:<u>\1</u>'],
```



### 5.研究遵循介绍类

例如：

This study adhered to the Declaration of Helsinki and was approved by the Ethics Committee of the Fudan University EENT Hospital Review Board (No. 2017060).

增加删除4：

```
[r'(Th(?:is|e) study adhered to.*?)(\. [A-Z])',r'删除4:<u>\1</u>\2']
```



### 6.日期类索引

例如：

 (ending in late May 2018)
 (from January 2011 to March 2011)

增加删除5：

```
[r'(\([^\n\(\)]{0,20}(?:January|February|March|April|May|June|July|August|September|October|November|December) [^\n\(\)]{0,20}\))',r'删除5:<u>\1</u>']
```