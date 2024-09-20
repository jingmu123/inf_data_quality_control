## reclean3_accr问题
### 无关文本：
1.文末段落删除补充，Funding Statement、Ethical Consideration、Compliance with Ethical Standards、Data Availability、Personal Communications等无关段落。
```
ending_starts = [
    [r'^[ #]*(Reference|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?m ?ent|Funding( Sources| Statement)?|Research Funding|Pseudomembranous Tracheobronchitis|Disclosure|Declaration|Permission|Institutional Review Board Statement|Consent( for Publication)?|Ethical( Approval| Consideration)?|Contributor|Acknowledgment Data availability statement|Compliance with Ethical Standard|Data Availability|Personal Communication)s?[ #]*($|\n)'],
]
```

2.补充删除参考文献格式，Press. 2016.p. 191-8.有空格情况
```
[r'(^\d+\\?\..*\d{4}[;；：\.]\w+(\(\d+\))?[:：；\.]?[\w \-]+.*)', r'删除6:<u>\1</u>'],
```

3.删除无关数字相关的零碎段落，Clin Case Rep int. 2022；6：1308.、Case Rep int. 2022；6：1359. Copyright C 2022 Ting-Han Tai.、Clin Case Rep Int.2022；6：1382、2022；6：1442.等
```
[r'(^(.{0,200})\d{4}[;；：\.]\w+(\(\d+\))?[:：；\.]?[\w \-]*.{0,50}$)', r'删除18:<u>\1</u>'],
```

4.句末无关数字删除，17，18、1|、7，17，18，31，32、17，19，20.、7-91.等。
```
[r'( ?[，\-\|]*(\d+[，\-\|])+([1-9]\d*)?(\.|$))', r'删除19:<u>\1</u>\4'],
```

5.补充删除年份结尾的参考文献段落，3. The helix COVID-19 surveillance dashboard. Helix. 2021.等。
```
[r'(^\d+\\?\..*\d{4}[;；：\.]$)', r'删除6-1:<u>\1</u>'],
```

6.删除其他零碎无关段落，Hao-Chiang|Ali S12\.、2CholistanUniversityy of、Pineta Grande Hospital等。
```
[r'(^(Hao-Chiang|Ali S12\.|2CholistanUniversityy of|Pineta Grande Hospital|The data used in this study|Youth Declare War|David Atallahiand|Maheswari VU，|Stray Cats New|Alassane Tourel，|Heraldo CB Inforzato，).*)', r'删除20:<u>\1</u>'],
```

7.一些零碎的段落，Fekede\.、India，、Kamble.、Elbey MAand UI Haq F2、Maheswari VUand Rajanikanth A、Dormon P等。
```
[r'(^(Fekede\.|India，|Kamble.|Elbey MAand UI Haq F2|Maheswari VUand Rajanikanth A|Dormon P|W13D L：43|Sibin Nair|Brazil\.)$)', r'删除21:<u>\1</u>'],
```


