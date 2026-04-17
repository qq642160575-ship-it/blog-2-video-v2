backend/app/core
本目录负责：底层基础设施适配，如配置、数据库、Redis、错误和日志。
不负责：业务编排、HTTP 路由细节。声明：一旦本目录结构或职责发生变化，请更新本文件。

文件说明
`config.py` 地位：配置中枢。职责：读取环境变量并生成全局设置。
`db.py` 地位：数据库底座。职责：创建 SQLAlchemy engine、session 和 Base。
`errors.py` 地位：错误码定义。职责：统一错误码与错误文案。
`logging_config.py` 地位：日志配置中枢。职责：配置根目录 logs 下的文件日志。
`redis.py` 地位：Redis 适配层。职责：提供 Redis 连接和基础访问能力。
