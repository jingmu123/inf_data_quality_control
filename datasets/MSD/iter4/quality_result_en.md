msd英文第四次清洗

#### 无关的引用

1. reference后面参考文献后面人名公司名难定位到结束的位置（√）

   ```
   ['(\d\.)?[^\.]{0,300}[rR]eference(.{0,300}\d\d[/]?\d\d\)?\.[^\d]?){1,5}','\n'],
   ```

2. this image/photo  （√）

   ```
   (Image[^\.]{0,100}\.)?[^\.？]*This ([iI]mage|photo)[^\.]*.   图片
   [^\.]*PHOTO [A-Z]{2,} 一些...图库
   ```

   英文的图片问题比较复杂，会出现很多的人名，公司名，会出现很多点很难去定位

   例： DR M.A. ANSARY/SCIENCE PHOTO LIBRARY Herpes Simplex Virus Infection in the Newborn This photo shows small fluid-filled blisters on the face of a newborn infected with herpes simplex virus. 

   例： DR P. MARAZZI/SCIENCE PHOTO LIBRARY Blister Rash in Herpes Simplex Virus Infection This photo shows a newborn who has acquired immunodeficiency syndrome (AIDS) and a rash of small fluid-filled blisters covering the entire body. DR M.A. ANSARY/SCIENCE PHOTO LIBRARY Herpes Simplex Virus Infection in the Newborn This photo shows small fluid-filled blisters on the face of a newborn infected with herpes simplex virus. 

3. PHOTO（√）

   ```
   ['[^\.]*PHOTO [A-Z]{2,}','\n'],
   ```

4. Image（√）

   例： Image courtesy of Karen McKoy, MD. 

5. read more问题的重新修改，read more问题和中文的阅读更多问题一样多一样复杂，总会有匹配不好的情况出现（√）

   ```
   [^\.]*([Ss]ee.{0,300})?(\.\.\.)? read more[^\.\(]*(\(.{0,300}?\)[^\.\(]{0,300}){0,3}[\.\)]{0,3}
   ```

   例： On occasion, however, respiratory acidosis Respiratory Acidosis Respiratory acidosis is primary increase in carbon dioxide partial pressure (Pco2) with or without compensatory increase in bicarbonate (HCO3−); pH is usually low but may be near... read more develops, some degree of which is accepted for the greater good of limitin g ventilator-associated lung injury and is generally well tolerated, particularly when pH is ≥ 7.15.  最后的小数点会让匹配到7.就结束  同样有小数点的情况都会有这种情况

   例：IgE levels are probably most helpful for following response to therapy in allergic bronchopulmonary aspergillosis Allergic Bronchopulmonary Aspergillosis (ABPA) Allergic bronchopulmonary aspergillosis (ABPA) is a hypersensitivity reaction to Aspergillus species (generally A. fumigatus) that occurs almost exclusively in patients with asthma... read more .    这个情况会匹配到A.

   例：(However, in liberating patients with low cardiac output from mechanical to noninvasive ventilation, the transition from positive to negative airway pressure can increase afterload and result in acute pulmonary edema or worsening hypotension. ) Noninvasive positive pressure ventilation (NIPPV) Noninvasive positive pressure ventilation (NIPPV) Mechanical ventilation can be Noninvasive, involving various types of face masks Invasive, involving endotracheal intubation Selection and use of appropriate techniques require an understanding... read more , whether continuous positive pressure ventilation or bilevel ventilation, is useful in averting endotracheal intubation in many patients because drug therapy often leads to rapid improvement.   这个情况会匹配到hypotension.这里的点，加上非右括号也不合适，加上之后就是匹配到 (NIPPV)这里的右括号

6. DR P这个不知道什么意思，（√）

   ```
   ['DR ([A-Z]+\.){1,}','\.']
   ```

7. Epub后面是日期（√）

   ```
   ['Epub[^\.]*\.(.{0,200}?\d+\.){0,6}','\n'],
   ```

   例：Epub 2015 Mar 17. PMID: 25794784.

   例：Epub 2019 Nov 5. 2. International Ovarian Tumor Analysis: IOTA Simple Rules and SRrisk calculator to diagnose ovarian cancer. Accessed 1/22/22.

8. see table问题  之前对英文匹配正则重写，重写忽略了see table问题（√）

   ```
   ['\(?[^\.\(]*?[sS]ee [tT]able[^\.\)]*.','\n'],
   ```

9. ©（√）

   例：© Springer Science+Business Media Diagnosis of Vitiligo A doctor's evaluation Vitiligo is recognized by its typical appearance.

10. By permission of the publisher. 经出版商许可问题 （√）

    例：By permission of the publisher. From Demmler G: Congenital and perinatal infections. In Atlas of Infectious Diseases: Pediatric Infectious Diseases. Edited by CM Wilfert. Philadelphia, Current Medicine, 1998.

11. see also(√)

    例：The schedule below is based on the ones recommended by the American Academy of Pediatrics (AAP) and the Centers for Disease Control and Prevention (CDC; see also the CDC schedule for infants and children [birth through 6 years] and the CDC schedule for older children [7 to 18 years old]).

12. for more information（√）

    ```
    ['\(?[^\.\(]*[Ff]or more information[^\.\(]*(\(.{0,300}?\)[^\.\(]{0,300}){0,5}\)?(\sA[^\.]*.)?','\n'],
    ```

    例：Immunization People with HIV infection should have the following vaccinations (for more information, see Centers for Disease Control and Prevention [CDC] immunization recommendations): Conjugate pneumococcal vaccine Pneumococcal Vaccine Pneumococcal vaccines help protect against bacterial infections caused by Streptococcus pneumoniae (pneumococci).

    例：For more information, see the COVID-19 Advisory Committee on Immunization Practices Vaccine Recommendations, the FDA prescribing information for the Pfizer-BioNTech COVID-19 vaccine and the FDA prescribing information for the Moderna COVID-19 vaccine, and the EUA fact sheets for vaccination providers (Pfizer-BioNTech, Moderna, Janssen/Johnson & Johnson, and Novavax).




干净文本:82 脏文本:43 合格率=0.656
{'格式规范性': 11, '文本干净度': 34, '语义有效性': 1} {'缺少标点': 8, '无关文本': 33, '多余标点': 2, '语义不完整': 1, '无关引用': 1, '多余空格': 1}

干净文本:83 脏文本:42 合格率=0.664
{'文本干净度': 53, '格式规范性': 2, '语义有效性': 1} {'无关文本': 53, '多余标点': 2, '语义不完整': 1}

