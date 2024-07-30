reclean2_uptodate_new_en

针对多段的无关文本删除,修改补充step3方法，主要是一些新出现的情况，某几段是与内容无关的有明显特征的
补充一些固定格式

```
    def step3_reference(self, context):
        new_context = []
        references_started = False   #定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        introduce = 0
        introduce_index = []
        Inc = 0
        Inc_index = []
        for index, item in enumerate(context):
            if re.search(r'^(References|参考文献|见参考文献|致谢|REFERENCES|ACKNOWLEDGMENT|The following organizations also provide reliable health information|More on this topic)', item.strip()):
                references_started = True
            if references_started:
                item = ""

            if re.search(r'^2024© UpToDate, Inc', item.strip()):
                Inc += 1
                Inc_index.append(index)
            if re.search(r'ALERT: ', item.strip()):
                Inc -= 1
                Inc_index.append(index)

            # 要删除从Author到引言 设定了两个条件在循环时同时出现Author和引言，记下index，对相应的index进行删除
            if re.search(r'^(Author)', item.strip()):
                introduce += 1
                introduce_index.append(index)
            if re.search(r'^(引言|简介)', item.strip()) or re.search(r'^INTRODUCTION', item.strip()) or re.search(r'^Please read the Disclaimer at the end of this page',item.strip()):
                introduce -= 1
                introduce_index.append(index)
            new_context.append(item)

        if introduce == 0 and len(introduce_index) == 2:
            start_index = introduce_index[0]
            end_index = introduce_index[1]
            new_context = new_context[:start_index] + new_context[end_index+1:]
        if Inc == 0 and len(Inc_index) == 2:
            start_index = Inc_index[0]
            end_index = Inc_index[1]
            new_context = new_context[:start_index] + new_context[end_index+1:]
        return new_context
```

目前有（References|参考文献|见参考文献|致谢|REFERENCES|ACKNOWLEDGMENT|The following organizations also provide reliable health information|More on this topic）之后的段落
2024© UpToDate, Inc到ALERT的段落

Author到中文中的(引言|简介),英文里的(INTRODUCTION 、Please read the Disclaimer at the end of this page）这几个固定特征的叙述

无关文本

```
1.带有括号的algorithm的描述
[r'\([^\(\)]{0,100}algorithm\s[^\(\)]{0,100}\)','']
2.无关人名，或者是地名   某一年的谁或哪里
[r'\(\s?[A-Z][^\(\)]{0,50}\s\d{4}[^\(\)]{0,50}\)','']
```

句子中含有Links to related guidelines are provided separately这句话的里面的内容都有问题，且这条数据会很短，我选择了跳过这条数据，这样的数据有635条，基本都是这样的内容


例：

"Society guideline links: Recurrent pregnancy loss\n\nIntroduction —\n\nThis topic includes links to society and government-sponsored guidelines from selected countries and regions around the world. We will update these links periodically; newer versions of some guidelines may be available on each society's website. Some societies may require users to log in to access their guidelines.\n\nThe recommendations in the following guidelines may vary from those that appear in UpToDate topic reviews. Readers who are looking for UpToDate topic reviews should use the UpToDate search box to find the relevant content.\n\nLinks to related guidelines are provided separately. (See \"Society guideline links: Pregnancy loss (spontaneous abortion)\" .)\n\nCanada\n\n● Choosing Wisely Canada: Don't prescribe corticosteroids, IVIG, leukemia inhibitory factor or lymphocyte immunization therapy for patients undergoing IVF, those with a history of recurrent implantation failure or patients with recurrent pregnancy loss (2022)\n\n● Canadian College of Medical Geneticists (CCMG): Practice guidelines for cytogenetic analysis – Recommendations for the indications, analysis and reporting of constitutional specimens (peripheral blood, solid tissues) (2021)\n\n● Society of Obstetricians and Gynaecologists of Canada (SOGC): Clinical practice guideline on cervical insufficiency and cervical cerclage (2019)\n\n● SOGC: Clinical practice guideline on the use of first trimester ultrasound (2019)\n\n● SOGC: Clinical practice guideline on advanced reproductive age and fertility (2017)\n\n● SOGC: Clinical practice guideline on the management of uterine fibroids in women with otherwise unexplained infertility (2015)\n\nUnited States\n\n● American College of Obstetricians and Gynecologists (ACOG): Technology assessment on sonohysterography (2016, reaffirmed 2023)\n\n● American Society for Reproductive Medicine (ASRM): Definition of infertility – A committee opinion (2023)\n\n● Society for Maternal-Fetal Medicine (SMFM): Choosing Wisely – Don't do an inherited thrombophilia evaluation for women with histories of pregnancy loss, fetal growth restriction (FGR), preeclampsia and abruption (2022)\n\n● ACOG: Practice bulletin on early pregnancy loss (2018, reaffirmed 2021)\n\n● American College of Radiology (ACR): ACR Appropriateness Criteria on female infertility (revised 2019)\n\n● ASRM: Evaluation and treatment of recurrent pregnancy loss – A committee opinion (2012)\n\nEurope\n\n● European Society of Human Reproduction and Embryology (ESHRE): Guideline on recurrent pregnancy loss (2023)\n\nUnited Kingdom\n\n● National Institute for Health and Care Excellence (NICE): Guideline on ectopic pregnancy and miscarriage – Diagnosis and initial management (2019, updated 2023)\n\n● Royal College of Obstetricians and Gynaecologists (RCOG): Green-top guideline on recurrent miscarriage (2023)\n\n● NICE: Interventional procedures guidance on laparoscopic cerclage for cervical incompetence to prevent late miscarriage or preterm birth (2019)\n\n● Choosing Wisely UK: Royal College of Obstetricians and Gynaecologists (RCOG) – Parental karyotyping is not routinely indicated in recurrent miscarriage. Information should be given to the patient, any questions answered, and their individual circumstance and preferences discussed (2018)\n\n● NICE: Interventional procedures guidance on hysteroscopic metroplasty of a uterine septum for recurrent miscarriage (2015)\n\n● NICE: Quality standard on ectopic pregnancy and miscarriage (2014)\n\n● RCOG: Green-top guideline on late intrauterine fetal death and stillbirth (2010)\n\nAustralia–New Zealand\n\n● Royal Australian and New Zealand College of Obstetricians and Gynaecologists (RANZCOG): Best practice statement for the use of misoprostol in obstetrics and gynaecology (2021)\n\n● RANZCOG: Progesterone support of the luteal phase and in the first trimester (2018)\n\n● New South Wales Ministry of Health (NSW Health): Maternity – Management of early pregnancy complications (2012)\n\nJapan\n\n● \\[In Japanese\\] Japan Society of Obstetrics and Gynecology (JSOG): Obstetrics and gynecology clinical practice guidelines – Obstetrics edition (2023)\n\n● \\[In English\\] JSOG and Japan Association of Obstetricians and Gynecologists (JAOG): Guidelines for obstetrical practice in Japan, 2020 edition (published 2023)\n\n● \\[In Japanese\\] Choosing Wisely Japan: Blood tests to check for the risk of miscarriage – When the test helps and when it doesn't (2015)\n\nUse of UpToDate is subject to the Terms of Use .\n\nTopic 114520 Version 22.0", "tags": {}, "lang": "en", "attr": {"oid": "114520", "out_text": "Outline\n-------\n\n*   Introduction\n*   Canada\n*   United States\n*   Europe\n*   United Kingdom\n*   Australia–New Zealand\n*   Japan\n\nRELATED TOPICS\n--------------\n\n*   Society guideline links: Pregnancy loss (spontaneous abortion)

```
if re.search("Links to related guidelines are provided separately", context):
    continue
```





特殊符号❤️
在标注平台上有出现，在The use of be后面出现了，但是在数据中并没有这个心
The use of benzodiazepines, including triazolam, exposes users to risks of abuse, misuse, and addiction, which can lead to overdose or death. Abuse and misuse of benzodiazepines commonly involve concomitant use of other medications, alcohol, and/or illicit substances, which is associated with an increased frequency of serious adverse outcomes. Before prescribing triazolam and throughout treatment, assess each patient's risk for abuse, misuse, and addiction.