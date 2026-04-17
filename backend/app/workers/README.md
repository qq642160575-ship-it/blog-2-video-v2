backend/app/workers
本目录负责：后台常驻 worker 进程。
不负责：HTTP 接口与模板渲染命令。声明：一旦本目录结构或职责发生变化，请更新本文件。

文件说明
`pipeline_worker.py` 地位：生成 worker 主体。职责：消费生成队列并执行 LangGraph 流程。
