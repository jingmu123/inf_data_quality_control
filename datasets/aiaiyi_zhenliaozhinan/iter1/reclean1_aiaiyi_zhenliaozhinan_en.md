## reclean0_aiaiyi_zhenliaozhinan_en
### 无关文本：

1.**点击下载\*\*\*：《美国感染性疾病协会隐球菌治疗指南》**、完整下载 2010ACOG临床指南：产时胎儿心律监护的管理、**《哺乳女性抗抑郁药物的应用》完整版下载地址：**等。

正则删除：```[r'([\*\\]*[^\*\\\n]*(点击下载|完整版?下载|下载：)[^\n]+)', '']```。

2.句末（12）、（1）、（2）...等。

正则删除：```[r'( *[\(（](\d+([\s,，\-–\d]{0,100}))[\)）])([,，;；.。])', r'\4']```。

3.网址，如**  http://ziyuan.iiyi.com/source/down/1505558.html等。

正则删除：```[r'(\**[  ]*(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z\.]{2,6})([\/\w \.-]+)?\/?)', '']```。


4.（Smith et al, 2006）、（Snowden et al 2011）。

正则删除：```[r'([\(（][^\(\)（）]*(\set[\s\xa0]{1,3}al|\d{4})[^\(\)（）]*[\)）])', '']```。

5.表图注释(Figure 1)、(Table 1)、(table 1)等。

正则删除：```[r'(([\(（][^\(\)（）]{0,50})([fF]igure|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able) *([^\(\)（）]{0,50}[\)）]))', '']```。

6.句首8-17、8、2，3等。

正则删除：```[r'([,，;；.。] *)(\d+([\s，,\-–\d+]{0,20}) *)([A-Za-z])', r'\1\4']```。

7.句末\[1, 2\]、\[3–22\]、\[4\]等。

正则删除：```[r'(\\?\[[\d\s\-,，—\\]{0,100}\])', '']```。


### 0809补充：
解决单词粘连问题
``` 
def step5_sentence_segment(self, context):
        patter = r'([A-Za-z]{15,})'
        if re.search(patter, context):
            word_list = re.findall(patter, context)
            for wordl in word_list:
                # 使用 wordninja 进行分词
                words = wordninja.split(wordl)
                output_string = " ".join(words)
                words_escape = re.escape(wordl)
                context = re.sub(rf'{words_escape}', output_string, context)
        return context
```