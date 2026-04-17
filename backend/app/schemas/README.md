backend/app/schemas
本目录负责：接口和流程的结构化输入输出定义。
不负责：数据库持久化、直接业务执行。声明：一旦本目录结构或职责发生变化，请更新本文件。

文件说明
`article_analysis.py` 地位：文章分析 schema。职责：约束文章解析结果结构。
`project.py` 地位：项目 schema。职责：约束项目创建与返回数据。
`scene_generation.py` 地位：分镜生成 schema。职责：约束 LLM 分镜生成结果。
`subtitle.py` 地位：字幕 schema。职责：约束字幕片段及导出数据结构。
