backend/app/services
本目录负责：业务逻辑编排与基础能力组合。
不负责：HTTP 协议细节、数据库模型定义。声明：一旦本目录结构或职责发生变化，请更新本文件。

文件说明
`ai_logger_service.py` 地位：AI 日志服务。职责：把 AI 关键输入输出写入文件和数据库。
`article_parse_service.py` 地位：文章解析服务。职责：调用 LLM 提取文章分析结果。
`asset_service.py` 地位：素材服务。职责：管理素材记录与素材相关逻辑。
`cache_service.py` 地位：缓存服务。职责：封装缓存读写、键规范和失效逻辑。
`concurrency_manager.py` 地位：并发控制服务。职责：限制与协调任务并发执行。
`file_cleanup_service.py` 地位：文件清理服务。职责：清理生成产物和临时文件。
`job_log_service.py` 地位：任务日志服务。职责：记录任务阶段日志并同步文件日志。
`job_service.py` 地位：任务服务中枢。职责：创建任务、更新状态、协调队列与结果。
`project_service.py` 地位：项目服务。职责：创建项目、读取项目、维护项目缓存。
`scene_generate_service.py` 地位：分镜生成服务。职责：调用 LLM 输出视频分镜脚本。
`scene_service.py` 地位：分镜服务。职责：读取、编辑与版本化分镜。
`subtitle_service.py` 地位：字幕服务。职责：生成、处理和导出字幕数据。
`task_queue.py` 地位：任务队列服务。职责：封装 Redis 队列的推送和消费。
`template_mapping_service.py` 地位：模板映射服务。职责：把分镜映射到 Remotion 模板参数。
`tts_service.py` 地位：语音服务。职责：把旁白文本转换为音频文件。
