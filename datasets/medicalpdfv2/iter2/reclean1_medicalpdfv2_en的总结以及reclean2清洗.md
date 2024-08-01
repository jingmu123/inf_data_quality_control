reclean1_medicalpdfv2_en的总结以及reclean2清洗

### 有用性（有些误删问题也被标记有用性里面）

- 图片描述相关，补充出现的图片描述新情况

  ```
  这个规则不够灵活
  if item.strip() in ["##References","## References","## Suggested Readings","##Suggested Readings"]:
  ↓
  if re.search(r'^#{1,3}\s?(Reference|Suggested Reading)s?',item.strip()):
  ```

- 如果句子中出现©，一般是与版权相关的句子，可删除

### 误删解决

- 对参考文献的删除,之前做了一个开关当遇到这些特征之后认为后面的都是参考文献，对这个匹配规则进行修改，此时还出现一个问题就是如果说当页还有正常内容，那么删除整页会造成误删，添加一个判断，如果发现有这种情况不对整页进行删除，只让开关去删除

- 对模型判定进行优化，这里如果模型判定这一页是参考页，那么至少有一个是依据特征判断出来的参考，一个都没有肯定是误判了，对于删除标签版，参考删除的标签要在最后的合并处才能删除，需要添加一个删除的步骤

```
label = fasttext_model.predict(text.strip().replace('\n', ''))
print(label[0][0])
if label[0][0] in ['__label__cankao']  and not re.search(r'参考删除-4',text) and re.search(r'参考删除',text):
    context.insert(0, "(本页删除)本页被模型判断为参考页")
if label[0][0] in ['__label__mulu']:
    context.insert(0, "(本页删除)本页被模型判断为目录页")
```

- 对正则的优化

```
将带括号的一些网址先删掉，这样删除1就匹配不到这条，解决一些误删
[
    r'(\([^\(\)]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(http)|(\.html))[^\)\(]*\))',
    r'删除20:<u>\1</u>'
],
[
    r'([^\d][^\.\n]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(http)|(\.html))[^\n]*)',
    r'删除1:<u>\1</u>'
],
```



## 格式规范性





### 多余换行

修改现有的段内换行适配更多的情况，并添加一些换行新规则

```
if text.rstrip()[-1] in ['-','—',',']:

对标题处的多余换行解决
if re.search(r'^#{0,3}\s?(\d+[\.,\s]?){0,5}$', stripped_item) and re.search(r'^#{0,3}\s?[A-Z]',next_item):  # 匹配段落中只有序号且下一段是大写开头的情况 都可以带#


对于数字开头的换行要谨慎但是遇到有
Baseline pressure
60 mm Hg.
这种情况还是需要给换上去的，对这种情况加入了严格的条件
if re.search(r'^\d+\s?[^\.]',next_text) and self.is_merge_ngram(text, next_text):# 如果遇到 20 mm 这种情况的多余换行
在评分这里 合并完的分数要更严格更低
if re.search(r'^\d+',next_text) and (merge_text_sorce < text_score or merge_text_sorce < next_text_score) and merge_text_sorce < 2000:
            return True
elif not re.search(r'^\d+',next_text) and (merge_text_sorce < text_score or merge_text_sorce < next_text_score) and merge_text_sorce < 5000:
            return True


```



暂时搁置换行情况     比较危险

```
3. After 6 h of stimulation, remove the media and wash twice with|删除段内换行|PBS. Reconstitute a vial of MitoSOX in 13 µ L of DMSO
多余换行
(5-mM stock). Dilute MitoSOX 1:1000 in lift buffer (e.g.,|删除段内换行|5 µ L in 5 mL) to a final concentration of 5 µ M. You will need
多余换行
0.5 mL of diluted working stock per well
```

```
【21】The frequency of postcatheterization pseudoaneurysm (PA) increased in the 1990s due to increased use of large catheters and anticoagulation during vascular interventions. PA typically manifests with swelling and ecchymosis in the first day or two following the procedure. In this setting, a PA basically is a hematoma that maintains an internal area of extravascular blood flow via a patent neck that communicates with the femoral artery. With time, a fibrous capsule may develop around the PA.
On sonography, a PA appears as a collection of fluid
多于换行
The most basic aspect of color Doppler image interpretation is the determination of flow direction. 
```