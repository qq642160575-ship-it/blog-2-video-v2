# Step 11 测试指南 - 真实 LLM 文章解析

## ✅ Step 11 已完成

已接入真实 LLM（GPT-4）进行文章解析，可以自动提取文章的主题、受众、关键要点等结构化信息。

## 📁 新增文件

```
backend/app/
├── schemas/
│   └── article_analysis.py      # ArticleAnalysis Pydantic Schema
├── services/
│   └── article_parse_service.py # 文章解析服务（LangChain + OpenAI）
└── scripts/
    └── test_article_parse.py    # 测试脚本
```

## 🔧 功能特性

### ArticleAnalysis Schema
包含以下字段：
- `topic`: 核心主题（5-15字）
- `audience`: 目标受众
- `core_message`: 核心信息
- `key_points`: 关键要点列表（3-5个）
- `tone`: 语气风格（professional/casual/educational）
- `complexity`: 复杂度（beginner/intermediate/advanced）
- `estimated_video_duration`: 建议视频时长（45-60秒）
- `confidence`: 置信度（0-1）
- `reasoning`: 分析推理（可选）

### ArticleParseService
- 使用 LangChain + OpenAI GPT-4
- 结构化 Prompt 设计
- JSON Schema 校验
- 自动重试机制（最多3次）
- 错误处理和降级

### Pipeline Worker 集成
- 优先使用真实 LLM
- 如果 API Key 未配置，自动降级到 Mock
- 如果 LLM 调用失败，自动降级到 Mock
- 保证系统稳定性

## 🧪 如何测试

### 方式 1: 单独测试文章解析

**前提条件：**
需要配置 OpenAI API Key：

```bash
# 编辑 .env 文件
cd backend
nano .env

# 添加或修改以下行
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**运行测试：**
```bash
cd backend
source venv/bin/activate
python scripts/test_article_parse.py
```

**预期输出：**
```
======================================================================
Test Article Parse Service (Real LLM)
======================================================================

Article content:
----------------------------------------------------------------------
# 什么是 RAG

RAG（Retrieval-Augmented Generation）是一种结合了检索和生成的 AI 技术...
----------------------------------------------------------------------

Parsing article with LLM...

✓ Article parsed successfully!

Analysis Result:
----------------------------------------------------------------------
Topic: RAG 检索增强生成技术
Audience: 技术开发者、AI 工程师
Core Message: RAG 通过结合检索和生成技术，解决了传统 LLM 的知识更新和可信度问题
Tone: professional
Complexity: intermediate
Estimated Duration: 50s
Confidence: 0.92

Key Points:
  1. RAG 结合外部知识库与大语言模型，提升准确性
  2. 解决知识截止日期限制，可获取最新信息
  3. 答案可追溯来源，减少幻觉问题
  4. 成本效益高，维护知识库比微调模型更经济
  5. 适合企业级应用，特别是需要准确性的场景
----------------------------------------------------------------------

✓ Test completed successfully!
```

### 方式 2: 端到端测试（带 LLM）

**启动服务：**
```bash
# 终端 1 - API Server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 终端 2 - Pipeline Worker（会自动使用 LLM）
cd backend
source venv/bin/activate
python scripts/run_worker.py

# 终端 3 - Render Worker
cd render-worker
npm start

# 终端 4 - 运行测试
cd backend
source venv/bin/activate
python scripts/test_milestone1.py
```

**观察 Pipeline Worker 输出：**
```
[1/6] Article Parse...
  ✓ Topic: RAG 检索增强生成技术 (Real LLM)
  ✓ Confidence: 0.92
```

如果看到 `(Real LLM)` 标记，说明使用了真实 LLM。
如果看到 `(Mock)` 标记，说明降级到了 Mock 数据。

## 🔍 验证

### 检查是否使用了真实 LLM

1. 查看 Pipeline Worker 日志，确认有 `(Real LLM)` 标记
2. 观察处理时间：真实 LLM 调用需要 2-5 秒，Mock 只需 1 秒
3. 检查分析结果的准确性和多样性

### 如果没有 API Key

系统会自动降级到 Mock 模式，不会报错：
```
[1/6] Article Parse...
  ✓ Topic: RAG 基础概念 (Mock)
  ✓ Confidence: 0.86
```

## ✨ 技术实现

### LangChain 集成
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOpenAI(model="gpt-4", temperature=0.3)
chain = prompt | llm | parser
result = chain.invoke({"article_content": content})
```

### Pydantic Schema 校验
```python
class ArticleAnalysis(BaseModel):
    topic: str = Field(description="...")
    audience: str = Field(description="...")
    # ... 其他字段
```

### 重试机制
```python
def parse_article_with_retry(content, max_retries=3):
    for attempt in range(max_retries):
        try:
            return parse_article(content)
        except Exception as e:
            if attempt < max_retries - 1:
                continue
            raise
```

## 🎯 下一步：Step 12

接入真实 LLM 进行分镜生成，根据文章分析结果生成 6-10 个视频场景。
