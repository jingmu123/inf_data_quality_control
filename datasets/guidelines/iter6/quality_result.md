# 已解决
1. 975072：无关文本（带Refer的句子）：Refer to the NACI Supplemental Statement on Afluria  Tetra for additional information supporting this recommendation
                              Refer to the NACI Literature Review on the Comparative Effectiveness and Immunogenicity of Subunit and Split Virus Inactivated Influenza Vaccines in Adults 65 Years of Age and Older for additional information supporting this conclusion
        语义不完整:1（误删）  语义不完整#148#148#Key relevant details and differences between vaccine products are also highlighted in A   
                  原文：Key relevant details and differences between vaccine products are also highlighted in Appendix A.  (?:\.).*Appendix.*?\.
                    r'(\()?(Table|table|TABLE|Figure|figure|Section|diagram|Appendix|Box):?\s*(\d+)?(\.?).*?(\))?'   
                    正则把Appendix单独删掉了，但这句话属于细节参考类也应该删掉（已删除）
                 2（误删）  语义不完整#198#198#s
                  原文：Neurologic or neurodevelopment conditions (NNCs) include neuromuscular, neurovascular, neurodegenerative, neurodevelopment conditions, and seizure disorders (and, for children, include febrile seizures and isolated developmental delay), but exclude migraines and psychiatric conditions without neurological conditions. Based on reviews of evidence and expert opinion, NACI includes adults and children with NNCs among the groups for whom influenza vaccination is particularly recommended. Refer to the NACI Statement on Seasonal Influenza Vaccine for 2018-2019 for a summary of the rationale supporting this decision and the Literature Review on Individuals with Neurologic or Neurodevelopment Conditions and Risk of Serious Influenza-Related Complications for additional details of the evidence reviews
                    r'.*((in evidence review)|(evidence review)|(.*details.*evidence)).*?(\.)?'
                    正则开头无边界导致误删
2. 975070：多余标点（误删） , after conducting 28 years of research on the relationships and interactions between Mind and Matter
                    r'-?.*,\s*\b(19|20)\d{2}\b.*?(\.)?'
                    为了删Macmillan, 1973.\n- Copi, Irving. Introduction to Logic.  MacMillan, 1953.\n- Copi, Irving. Symbolic Logic.  MacMillan, 1979, fifth edition.
                    把原文A recent study within the Princeton Engineering Anomalies Research Lab (the PEAR lab), suggested that there is a small, though statistically measurable, link between human thought and patterns that occur in random data sets.  There is no evidence as to whether this is caused by individuals unintentionally recognizing complex patterns and then moulding their thoughts towards an unconsciously known result or the thoughts of the individual are themselves affecting the random patterns in a manner of individuation.  This studys results have not been replicated, and its methodologies are disputed. The PEAR lab closed at the end of February, 2007, after conducting 28 years of research on the relationships and interactions between Mind and Matter
                    年份以及前面的文本都删掉了
        无关文本：↑ “Snopes entry”
3. 975068：无关文本：# Footnotes
4. 974998：原文存在多处换行
        例：When submitting information about a\nforeign clinical study, it is helpful to clearly identify in the cover letter that the material is\nbeing submitted in accordance with 21 CFR 312.120. The submission requirements for\nsupporting documentation can be found at 21 CFR 312.120(b).\n===16. Should a new form be prepared and signed when the OMB expiration date is\nreached?===
5. 975052：标出来是缺少换行，其实是误删（问题同975072的语义不完整）：, work began on demolishing the old 5-story hospital building, beginning with the east end facing Blair Stone Road.
                原文：On Wednesday September 6, 2006, work began on demolishing the old 5-story hospital building, beginning with the east end facing Blair Stone Road.
            已调整正则避免此错误再次发生
6. 975022：无关文本：Please Take Over This Page and Apply to be Editor-In-Chief for this topic:
        之前写过类似的正则，没有处理掉的原因是，正则的右边界设置成了句号.而这里是冒号:，已将正则补充完整
7. 975017：语义不完整：Therefore, the Ledipasvir/Sofosbuvir + ribavirin arms are not presented in
                原文：Therefore, the Ledipasvir/Sofosbuvir + ribavirin arm is not presented in Table 10.
        把Table 10，因为Table 10的引用不是括号，所以导致删掉之后句子不完整，考虑把有Table \d的句子过滤掉
8. 974989：多余标点：Substance D can be cut with meth, cocaine, or seemingly any stimulant drug. ,
         . , 已添加pattern进行替换
9. 974988：语义不完整#0#176#全文多处存在语义不完整的情况
        原因是之前的精准去重函数句末误删句号.，已将精准去重函数删除
10. 975051：语义有效性#语义不完整#58#60#类似Common physical examination findings of  include , and多段落出现语义不完整
        原文：\n may be helpful in the diagnosis of . Findings suggestive of/diagnostic of  include , , and .\nOR
        在此处过滤掉结尾是介词且并非换行错误的不完整的句子
# 无法解决

1. 975074,975073,975071,975069,975066,975064,975061，975054：原文语义不完整,冒号后缺内容
2. 975050：多余空格(全文存在多处单词被空格分开的情况):P erio d ic e x am in atio n s shall be m ade a v ailab le a t le a s t annually, as determined by the responsible physician, and shall include:  Interim medical and work histories
        之前解决的空格是标题中的多余空格，如： 因为标题中的单词的首字母是大写，可以通过代码将空格删除再按照大写字母分隔，当遇到整句话的单词且有空格是小写字母的时候，无法找到特殊定位将空格删除
3. 975058,975019,975032,975038,975045,975056:全文与医疗无关

