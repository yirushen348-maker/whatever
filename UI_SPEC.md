# BioStats Helper 新交互与自动推断逻辑

## 主流程（尽量减少手动选择）
1. 上传 Excel/CSV。
2. 自动读取数据结构（宽表/长表）。
3. 自动推断 group / value / sample ID / paired / groups 数量。
4. 自动推荐统计方法。
5. 用户仅确认，必要时在 Advanced settings 修改。

## 自动判断规则
- 宽表（wide）
  - 优先将第一列或命中关键词 `Sample ID/Mouse ID/Replicate/Subject/Patient/Clone` 的列识别为 sample ID。
  - 其余数值列识别为 groups。
  - 若同一行在 2 个及以上 group 列同时有值，默认为 paired。
- 长表（long）
  - group 列关键词：`group/treatment/condition`
  - value 列关键词：`value/intensity/expression/ratio/relative expression`
  - sample 列关键词：`sample/replicate/mouse/patient/subject`
  - 若同一 sample ID 出现在多个 group 中，默认为 paired/repeated measures；否则 unpaired。

## 统计推荐规则
- 2 组：
  - paired → `paired t-test` / `Wilcoxon signed-rank test`
  - unpaired → `unpaired t-test` / `Mann–Whitney U test`
- >2 组：
  - paired → `repeated-measures ANOVA` / `Friedman test`
  - unpaired → `one-way ANOVA` / `Kruskal–Wallis test`

## UI 要求
主界面仅保留：
1. 上传文件
2. 自动识别结果（含 confidence: High/Medium/Low）
3. 推荐统计方法
4. p value
5. figure legend 统计写法

仅保留一个 **Advanced settings**（默认折叠）：
- group column
- value column
- sample ID column
- paired/unpaired
- normality assumption
