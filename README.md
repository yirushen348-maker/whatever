# BioStats Helper Logic Update

本次改动实现了“上传后自动推断、最少手动配置”的核心逻辑。

- 自动识别 wide/long format
- 自动推断 group / value / sample ID / paired / group count
- 自动推荐统计方法
- 输出置信度（High/Medium/Low）
- UI 仅保留一个默认折叠的 Advanced settings（详见 `UI_SPEC.md`）

实现文件：`biostats_helper_logic.py`
说明文档：`UI_SPEC.md`
