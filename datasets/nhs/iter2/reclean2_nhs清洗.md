## 1.nhs清洗

### 2.1分析

初次清洗合格率87.63%。分数94.8，{'错误删除': 13, '无关文本': 41}，出现部分新的无关文本，有些是漏掉的无关文本。错误删除主要是删除7造成的，可以解决。

### 2.2.信息（观看视频）类的删除

例如：
Information:
Watch videos xxxxx
补充到删除5：
(?:\n|^)(Information: *\n+(?:Find out more about.*|You can report any.*\n+Visit Yellow Card.*|(Watch.*\n*)+))

### 2.3更多信息类的删除（补充）

例如：

More information

To find out more about some common types of hernia surgery, see:
*   xxx
* xxx
  补充到删除4：

  ```
  (?:\n|^)(#* *(?:About this video[:：]?\n-*\n|Common questions[:：]?\n-*\n|Help us improve our website[:：]?\n-*\n|More information[:：]?\n-*\n)(?:.*\n*)*?)(?:(.*\n-+)|$)
  ```

  ### 2.4 阅读有关症状与访问类的删除

  例如：
  Read about the symptoms of rhesus disease in a baby.
  Visit the NIHR website to find out more
  增加删除12：
  (?:\n|^)(Read about the symptoms of.*|Visit .*(?:website|(?:more|further) information.|read more|\.org|\.com|\.cn|site).*)

  ### 2.5目录类的补充

  例如：
  On this page
------------
1.  About betamethasone
2.  Key facts
3. Who can and cannot use betamethasone
   补充到删除10：(?:\n|^)((?:Contents *|On this page *)\n-+(\n+\d{1,2}\..*)+)

   ### 2.6联系方式与更新日期类的删除

   例如：
   **Contact details:**
   Phone: 020 3447 5241
   Email: ohsfaregistrations@nhsbsa.nhs.uk
   Tel: 0191 218 1999, or +44 191 218 1999 from outside the UK
   Fax: 0113 206 6461
   Website: www.leedsth.nhs.uk/a-z-of-services/fgm
   增加删除13：
   (?:\n|^)(\**(?:Email|Phone|Tel|Website|Contact details|Fax|Updated)[:：].*)

   ### 2.7信贷类的删除（补充）

   例如：
   Credit:
   Don't Forget The Bubbles
   https://dftbskindeep.com/all-diagnoses/scarlet-fever/#!jig\[1\]/ML/4664  
   补充到删除9：
   (?:\n|^)(Credit:\n(\n.*(?:\n| )*(?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)? *)+)

   ### 2.8图像详细说明类的删除

   例如：
   Here is an image gallery ....
*    1: Hand, foot and mouth disease spots on white skin (thumbnail). 1
*    2: Hand, foot and mouth disease spots and patches on medium brown skin (thumbnail). 2
* 3: Hand, foot and mouth disease blister on white skin (thumbnail). 3
  补充到删除11：

  (?:\n|^)((?:More in.*\n-+| *Related conditions *\n-+| *Useful resources *\n-+|You can find more.*[:：]|Here is an image.*|Related information *\n-+)\n+(?:(?:\* *.*(?:\n|$))|(?: {2,}.*(?:\n|$)))+)

  ### 2.9描述图片与来自xxx社区内容的删除

  例如：
  Long description, image 1.
  <a>Community content from HealthUnlocked</a>
  增加删除14：
  (?:\n|^)((?:<a>Community content from HealthUnlocked<\/a>|Long description, image \d{1,2}\.))

  

  