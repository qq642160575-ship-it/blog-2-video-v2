# AI短视频生成系统 - 技术方案文档 v3

**文档版本**: v3.0
**创建日期**: 2026-04-20
**负责人**: 技术经理
**状态**: 待评审

---

## 1. 技术目标

### 1.1 系统能力目标

本次升级需要支撑以下能力：

1. **Hook自动生成能力**
   - 为每个视频生成3种类型的开场Hook（question/reveal/contrast）
   - 自动选择最优Hook作为第1个场景
   - Hook生成成功率 ≥ 98%

2. **内容质量检测能力**
   - 检测Hook有效性（关键词/疑问句/数字）
   - 检测场景重复度（相邻场景相似度<70%）
   - 检测叙事结构完整性（opening/build/payoff/close）
   - 检测节奏平衡（必须有高峰场景）

3. **结构化分析能力**
   - 为每个场景标注角色（hook/body/close）
   - 为每个场景标注叙事阶段（opening/build/payoff/close）
   - 为每个场景标注情绪等级（1-5）

### 1.2 非功能需求

- **性能**: 生成时长 ≤ 70秒（从当前55秒增加15秒）
- **稳定性**: 生成成功率 ≥ 95%（含重试）
- **可维护性**: 新增代码 ≤ 500行，避免过度工程化
- **成本**: LLM调用增加1次（从2次到3次），成本+30%

---

## 2. 系统整体架构

### 2.1 架构类型

**单体模块化架构**（保持现有架构，不引入微服务）

理由：
- 当前系统已是单体架构，改造成本高
- 业务规模不需要微服务复杂度
- 模块化设计足以支撑扩展

### 2.2 核心服务列表

系统包含以下服务模块：

| 服务名 | 职责 | 状态 |
|--------|------|------|
| **ArticleParseService** | 解析文章，提取主题/关键点/受众 | 已存在 |
| **HookGenerateService** | 生成3个Hook方案并选择最优 | **新增** |
| **SceneGenerateService** | 生成6-10个场景（含叙事结构） | 已存在，需增强 |
| **EnhancedValidator** | 验证场景质量（4项检查） | **新增** |
| **TTSService** | 生成语音 | 已存在 |
| **SubtitleService** | 生成字幕 | 已存在 |
| **RenderService** | 准备渲染 | 已存在 |

### 2.3 流程编排

使用 **LangGraph** 进行流程编排（保持现有方案）

```
ArticleParseService
    ↓
HookGenerateService (新增)
    ↓
SceneGenerateService (增强)
    ↓
EnhancedValidator (新增)
    ↓ (不通过？重试1次)
    ↓
TTSService
    ↓
SubtitleService
    ↓
RenderService
```

---

## 3. 核心模块设计

### 3.1 HookGenerateService（新增）

**职责**: 生成3个不同类型的Hook，并选择最优方案

**输入**:
```python
{
    "theme": str,           # 文章主题
    "key_points": List[str], # 关键点列表
    "target_audience": str,  # 目标受众
    "tone": str             # 语气风格
}
```

**输出**:
```python
{
    "hooks": [
        {
            "type": str,      # question/reveal/contrast
            "content": str,   # Hook文本
            "score": float    # 0.0-1.0
        }
    ],
    "selected_index": int     # 选中的Hook索引
}
```

**内部逻辑**:
1. 构建Prompt（包含3种Hook类型的示例）
2. 调用LLM生成3个Hook
3. 解析JSON响应
4. 选择最优Hook（优先question > contrast > reveal）
5. 失败重试3次，仍失败则返回默认Hook

**依赖**:
- LLM服务（OpenAI/Claude API）
- ArticleParseService的输出

---

### 3.2 SceneGenerateService（增强）

**职责**: 生成6-10个场景，包含叙事结构和情绪控制

**输入**:
```python
{
    "article_analysis": dict,  # 文章分析结果
    "selected_hook": dict      # 选中的Hook
}
```

**输出**:
```python
{
    "scenes": [
        {
            "goal": str,
            "voiceover": str,
            "screen_text": str,
            "duration_sec": int,
            "pace": str,
            "transition": str,
            "scene_role": str,        # hook/body/close (新增)
            "narrative_stage": str,   # opening/build/payoff/close (新增)
            "emotion_level": int,     # 1-5 (新增)
            "hook_type": str          # question/reveal/contrast (新增，仅第1个场景)
        }
    ]
}
```

**内部逻辑**:
1. 构建增强Prompt（包含叙事结构约束）
2. 将selected_hook注入到Prompt中
3. 调用LLM生成场景
4. 解析JSON响应，填充新增字段
5. 验证第1个场景是否使用了Hook

**依赖**:
- LLM服务
- HookGenerateService的输出

**关键改动**:
- Prompt中新增叙事结构约束（opening/build/payoff/close）
- Prompt中新增情绪控制约束（高-中-高-中）
- 强制第1个场景使用提供的Hook

---

### 3.3 EnhancedValidator（新增）

**职责**: 验证场景质量，检测4类问题

**输入**:
```python
{
    "scenes": List[Scene]  # 场景列表
}
```

**输出**:
```python
{
    "passed": bool,
    "errors": List[str],
    "quality_scores": List[float]  # 每个场景的质量分数
}
```

**内部逻辑**:

**检查1: Hook验证**
```python
def _validate_hook(scene: Scene) -> bool:
    text = scene.voiceover
    hook_keywords = ['为什么', '你知道吗', '原来', '竟然', '没想到',
                     '真相', '秘密', '误区', '方法', '技巧']
    has_keyword = any(kw in text for kw in hook_keywords)
    has_question = '?' in text or '？' in text
    has_number = bool(re.search(r'\d+', text))

    score = sum([has_keyword, has_question, has_number])
    return score >= 2  # 满足任意2个条件即通过
```

**检查2: 重复度检查**
```python
def _check_duplicate(scenes: List[Scene]) -> bool:
    for i in range(len(scenes) - 1):
        similarity = SequenceMatcher(
            None,
            scenes[i].voiceover,
            scenes[i+1].voiceover
        ).ratio()
        if similarity > 0.7:
            return True  # 发现重复
    return False
```

**检查3: 结构完整性**
```python
def _check_structure(scenes: List[Scene]) -> bool:
    stages = [s.narrative_stage for s in scenes]
    required = ['opening', 'build', 'payoff', 'close']
    return all(stage in stages for stage in required)
```

**检查4: 节奏检查**
```python
def _check_rhythm(scenes: List[Scene]) -> bool:
    energy_levels = [s.emotion_level for s in scenes]
    # 不能全是3（平淡），必须有至少1个高峰（≥4）
    return not all(e == 3 for e in energy_levels) and any(e >= 4 for e in energy_levels)
```

**依赖**:
- Python标准库（difflib.SequenceMatcher, re）

---

## 4. 数据流设计

### 4.1 完整数据流

```
用户上传文章
    ↓
[1] ArticleParseService
    输入: { "content": "文章全文" }
    输出: { "theme": "主题", "key_points": [...], "target_audience": "受众", "tone": "语气" }
    ↓
[2] HookGenerateService (新增)
    输入: ArticleParseService的输出
    输出: { "hooks": [...], "selected_index": 0 }
    耗时: ~8秒
    ↓
[3] SceneGenerateService (增强)
    输入: { "article_analysis": {...}, "selected_hook": {...} }
    输出: { "scenes": [6-10个场景] }
    耗时: ~30秒
    ↓
[4] EnhancedValidator (新增)
    输入: { "scenes": [...] }
    输出: { "passed": true/false, "errors": [...] }
    耗时: ~2秒
    ↓
    如果 passed == false 且 retry_count < 1:
        → 回到 [3] SceneGenerateService（带错误反馈）
    如果 passed == false 且 retry_count >= 1:
        → 降低标准到0.6，强制通过
    ↓
[5] TTSService
    输入: { "scenes": [...] }
    输出: { "audio_files": [...] }
    ↓
[6] SubtitleService
    输入: { "scenes": [...], "audio_files": [...] }
    输出: { "subtitles": [...] }
    ↓
[7] RenderService
    输入: { "scenes": [...], "audio_files": [...], "subtitles": [...] }
    输出: { "video_url": "..." }
```

### 4.2 关键数据结构

**Hook对象**:
```json
{
  "type": "question",
  "content": "为什么你每天忙到飞起，却总觉得没做什么？",
  "score": 0.85
}
```

**Scene对象（新增字段）**:
```json
{
  "goal": "抛出问题，建立好奇",
  "voiceover": "为什么你每天忙到飞起，却总觉得没做什么？",
  "screen_text": "为什么总觉得没做什么？",
  "duration_sec": 3,
  "pace": "fast",
  "transition": "cut",
  "scene_role": "hook",
  "narrative_stage": "opening",
  "emotion_level": 5,
  "hook_type": "question",
  "quality_score": 0.85
}
```

---

## 5. 关键技术选型

### 5.1 后端框架

**选择**: 保持现有框架（FastAPI 或 Flask）

**理由**:
- 避免重构成本
- 现有框架足以支撑需求

### 5.2 数据存储

**数据库**: PostgreSQL（保持现有）

**新增字段**:
```sql
ALTER TABLE scenes ADD COLUMN scene_role VARCHAR(20) NOT NULL DEFAULT 'body';
ALTER TABLE scenes ADD COLUMN narrative_stage VARCHAR(20) NOT NULL DEFAULT 'build';
ALTER TABLE scenes ADD COLUMN emotion_level INT NOT NULL DEFAULT 3;
ALTER TABLE scenes ADD COLUMN hook_type VARCHAR(20) NULL;
ALTER TABLE scenes ADD COLUMN quality_score FLOAT NULL;
```

**理由**:
- 5个字段不会影响性能
- 使用默认值保证向后兼容

### 5.3 LLM服务

**选择**: OpenAI GPT-4 或 Claude 3.5 Sonnet（保持现有）

**调用次数**:
- 当前: 2次（parse_article + generate_scenes）
- v3: 3次（parse_article + generate_hook + generate_scenes）

**成本**: +30%

**理由**:
- Hook质量提升60-70%，值得投入
- 不引入新的LLM服务，降低复杂度

### 5.4 流程编排

**选择**: LangGraph（保持现有）

**新增节点**:
- `generate_hook`: 调用HookGenerateService
- `validate_scenes`: 调用EnhancedValidator

**新增边**:
- `parse_article → generate_hook`
- `generate_hook → generate_scenes`
- `generate_scenes → validate_scenes`
- `validate_scenes → generate_scenes`（条件边，重试）

**理由**:
- LangGraph已在使用，无需引入新工具
- 支持条件跳转，满足重试需求

### 5.5 质量检测

**选择**: 规则检查 + 简单NLP（difflib.SequenceMatcher）

**不选择**: AI Critic（LLM评估LLM）

**理由**:
- AI评估AI不可靠，且增加5-30秒延迟
- 规则检查能覆盖80%的质量问题
- 成本低，速度快（~2秒）

---

## 6. 异常处理机制

### 6.1 Hook生成失败

**场景**: LLM返回格式错误、超时、或生成内容不符合要求

**处理策略**:
1. 重试3次（每次间隔2秒）
2. 仍失败：使用默认Hook
   ```python
   DEFAULT_HOOK = {
       "type": "reveal",
       "content": "接下来我要分享{theme}的关键方法",
       "score": 0.5
   }
   ```
3. 记录错误日志，继续流程

**代码示例**:
```python
def generate_hooks_with_retry(self, analysis: dict) -> HookResult:
    for attempt in range(3):
        try:
            return self.generate_hooks(analysis)
        except Exception as e:
            logger.warning(f"Hook生成失败 (尝试 {attempt+1}/3): {e}")
            time.sleep(2)

    # 使用默认Hook
    logger.error("Hook生成失败，使用默认Hook")
    return self._get_default_hook(analysis)
```

---

### 6.2 场景验证不通过

**场景**: EnhancedValidator检测到质量问题

**处理策略**:
1. 第1次不通过：重新生成场景（带错误反馈）
   ```python
   feedback = f"上次生成的场景存在以下问题：{errors}，请修正"
   ```
2. 第2次不通过：降低标准到0.6，强制通过
   ```python
   if retry_count >= 1:
       logger.warning("验证仍不通过，降低标准强制通过")
       return ValidationResult(passed=True, errors=[], forced=True)
   ```
3. 记录质量分数，用于后续分析

**代码示例**:
```python
def validate_with_retry(self, scenes: List[Scene], retry_count: int) -> ValidationResult:
    result = self.validate_scenes(scenes)

    if not result.passed and retry_count >= 1:
        # 降低标准
        logger.warning(f"验证不通过（重试{retry_count}次），降低标准")
        result.passed = True
        result.forced = True

    return result
```

---

### 6.3 LLM输出格式错误

**场景**: JSON解析失败、缺少必填字段

**处理策略**:
1. 尝试修复JSON（去除多余逗号、补全括号）
   ```python
   def fix_json(text: str) -> str:
       text = re.sub(r',\s*}', '}', text)  # 去除多余逗号
       text = re.sub(r',\s*]', ']', text)
       return text
   ```
2. 仍失败：使用默认值填充缺失字段
   ```python
   DEFAULT_VALUES = {
       "scene_role": "body",
       "narrative_stage": "build",
       "emotion_level": 3,
       "hook_type": None,
       "quality_score": None
   }
   ```
3. 记录错误，继续流程

---

### 6.4 LLM超时

**场景**: LLM调用超过30秒无响应

**处理策略**:
1. 设置超时时间：30秒
2. 超时后重试1次
3. 仍超时：抛出异常，返回错误给用户

**代码示例**:
```python
response = self.llm.invoke(prompt, timeout=30)
```

---

### 6.5 数据库迁移失败

**场景**: 生产环境执行ALTER TABLE失败

**处理策略**:
1. 在测试环境先验证迁移脚本
2. 生产环境迁移前备份数据库
3. 迁移失败：立即回滚
4. 使用Alembic的版本控制

**回滚方案**:
```bash
alembic downgrade -1
```

---

## 7. 性能与扩展性设计

### 7.1 性能指标

**当前性能**:
- 生成时长: 55秒
- LLM调用: 2次
- 成功率: ~90%

**v3目标性能**:
- 生成时长: ≤ 70秒（+15秒）
- LLM调用: 3次（+1次）
- 成功率: ≥ 95%

### 7.2 瓶颈分析

**瓶颈1: LLM调用延迟**
- HookGenerateService: ~8秒
- SceneGenerateService: ~30秒
- 总计: ~38秒（占总时长54%）

**当前不优化的理由**:
- 先验证效果，再优化性能
- 70秒用户可接受
- 并行优化会增加复杂度

**未来优化方向**（v3.1）:
- Hook生成和文章解析并行（节省5-8秒）
- 使用更快的LLM模型（如GPT-4o-mini）

---

**瓶颈2: 场景验证重试**
- 首次通过率: 预计85%
- 重试1次: 增加~32秒（generate_scenes + validate）
- 15%的请求会触发重试

**当前不优化的理由**:
- 重试能提升质量，值得投入
- 大部分请求（85%）不会重试

**未来优化方向**（v3.1）:
- 优化Prompt，提升首次通过率到95%
- 减少重试概率

---

### 7.3 扩展性设计

**水平扩展**:
- 当前架构支持多实例部署
- 无状态服务，可通过负载均衡扩展
- 数据库连接池支持并发

**并发处理**:
- 当前不支持单个请求内并行
- 未来可优化：Hook生成 + 文章解析并行

**存储扩展**:
- 5个新字段不会影响数据库性能
- 索引建议：`scenes.scene_role`, `scenes.narrative_stage`（用于分析查询）

---

### 7.4 监控指标

**关键指标**:
1. Hook生成成功率（目标 ≥ 98%）
2. 场景验证首次通过率（目标 ≥ 85%）
3. 端到端生成时长（目标 ≤ 70秒）
4. 生成成功率（目标 ≥ 95%）

**监控方式**:
- 在每个服务中记录耗时和成功率
- 使用现有日志系统（不引入新工具）
- 每日生成报表

---

## 8. 风险与降级方案

### 8.1 风险1: Hook质量不达预期

**风险描述**: 生成的Hook不够吸引人，用户修改率仍然很高

**概率**: 中（30%）

**影响**: 高（核心功能失效）

**降级方案**:

**Plan A: 增加Hook候选数量**
- 从3个增加到5个
- 提供更多选择，提升命中率
- 成本: +3秒延迟，+1次LLM调用

**Plan B: 引入轻量级Hook评分模型**
- 使用小模型（如BERT）做二分类（是Hook/不是Hook）
- 过滤掉低质量Hook
- 成本: +2秒延迟，需训练模型

**Plan C: 人工审核模式**
- 生成后由人工选择最优Hook
- 适用于高价值用户
- 成本: 人力成本

---

### 8.2 风险2: 规则检查误杀率高

**风险描述**: EnhancedValidator误判，拒绝高质量场景

**概率**: 中（20%）

**影响**: 中（影响用户体验）

**降级方案**:

**Plan A: 调整阈值**
- Hook验证: 从2个条件降低到1个条件
- 重复度检查: 从70%提升到80%
- 成本: 无

**Plan B: 可配置的验证规则**
- 允许用户关闭某些检查项
- 提供"严格模式"和"宽松模式"
- 成本: ~50行代码

**Plan C: 移除验证**
- 完全移除EnhancedValidator
- 回退到v2行为
- 成本: 无

---

### 8.3 风险3: 生成时长超过70秒

**风险描述**: 实际延迟超过预期，用户体验下降

**概率**: 低（10%）

**影响**: 中（用户可能流失）

**降级方案**:

**Plan A: 并行优化**
- Hook生成和文章解析并行
- 节省5-8秒
- 成本: ~100行代码，增加复杂度

**Plan B: 使用更快的LLM模型**
- 从GPT-4切换到GPT-4o-mini
- 节省10-15秒
- 成本: 可能影响质量

**Plan C: 移除重试机制**
- 验证不通过也强制通过
- 节省~32秒（15%的请求）
- 成本: 质量下降

---

### 8.4 风险4: LLM输出不稳定

**风险描述**: LLM经常输出格式错误或缺少字段

**概率**: 中（25%）

**影响**: 高（生成失败率上升）

**降级方案**:

**Plan A: 强化Prompt**
- 在Prompt中增加更多示例
- 使用Few-shot learning
- 成本: 无

**Plan B: 使用结构化输出**
- 使用OpenAI的Function Calling或Structured Output
- 强制LLM输出符合Schema
- 成本: 需要适配代码

**Plan C: 降低字段要求**
- 从5个字段减少到3个（只保留scene_role, narrative_stage, emotion_level）
- 降低LLM输出难度
- 成本: 功能降级

---

### 8.5 风险5: 数据库迁移失败

**风险描述**: 生产环境执行ALTER TABLE失败，导致服务不可用

**概率**: 低（5%）

**影响**: 高（服务中断）

**降级方案**:

**Plan A: 立即回滚**
```bash
alembic downgrade -1
```
- 回退到v2版本
- 成本: 无

**Plan B: 使用默认值**
- 新字段使用默认值，不影响现有功能
- v2代码仍可正常运行
- 成本: 无

**Plan C: 灰度发布**
- 先在10%流量上测试
- 发现问题立即回滚
- 成本: 需要灰度发布机制

---

## 9. 对产品需求的挑战

作为技术经理，我必须对PRD中的某些决策提出质疑：

### 9.1 挑战产品经理

**质疑1: 是否真的需要3个Hook类型？**

PRD要求生成question/reveal/contrast三种类型，但：
- 增加了LLM输出复杂度
- 用户最终只会看到1个Hook
- 可以简化为：生成3个Hook，不限定类型

**建议**: 第一版只生成question类型（完播率最高），降低复杂度

**产品回应**: 如果数据显示question类型足够，可以在v3.1简化

---

**质疑2: 5个新字段是否都必要？**

PRD保留了5个字段，但：
- `hook_type`只有第1个场景使用，其他场景为NULL
- `quality_score`当前没有使用场景
- 可以先只加3个字段（scene_role, narrative_stage, emotion_level）

**建议**: 先加3个核心字段，hook_type和quality_score等需要时再加

**产品回应**: 同意，但为了数据分析，建议保留quality_score

---

**质疑3: 重试机制是否会导致延迟爆炸？**

PRD允许重试1次，但：
- 15%的请求会触发重试，增加32秒
- 用户体验会有明显差异（55秒 vs 102秒）
- 可能导致用户投诉

**建议**: 降低验证标准，减少重试概率到5%以下

**产品回应**: 同意，初期设置宽松阈值，逐步收紧

---

### 9.2 挑战程序员

**质疑1: 是否需要单独的HookGenerateService？**

可以将Hook生成合并到SceneGenerateService中：
- 减少1个服务文件
- 减少1次LLM调用
- 降低系统复杂度

**反驳**:
- Hook太重要，值得独立服务
- 独立服务便于后续优化（如缓存、A/B测试）
- 合并会导致SceneGenerateService职责过重

**决策**: 保持独立服务

---

**质疑2: 规则检查是否过于简单？**

当前的规则检查（关键词匹配）可能不够准确：
- 误杀率可能很高
- 可以引入轻量级NLP模型

**反驳**:
- 先用简单规则验证效果
- 如果误杀率高，再引入模型
- 避免过度工程化

**决策**: 先用规则，监控误杀率

---

## 10. 实施建议

### 10.1 开发顺序

**阶段1: 数据层（Day 1-2）**
1. 创建数据库迁移脚本
2. 在测试环境执行迁移
3. 更新Scene模型定义

**阶段2: 服务层（Day 3-4）**
1. 实现HookGenerateService（含重试逻辑）
2. 增强SceneGenerateService的Prompt
3. 实现EnhancedValidator（4项检查）
4. 编写单元测试

**阶段3: 流程层（Day 5-6）**
1. 在LangGraph中新增generate_hook节点
2. 更新generate_scenes节点
3. 新增validate_scenes节点
4. 实现条件跳转（重试逻辑）
5. 编写集成测试

**阶段4: 测试与调优（Day 7）**
1. 端到端测试（至少20个真实文章）
2. Prompt调优（根据测试结果）
3. Validator阈值调整

**阶段5: 上线（Day 8）**
1. 在测试环境最终验证
2. 准备回滚方案
3. 生产环境数据库迁移
4. 灰度发布（10% → 50% → 100%）

---

### 10.2 测试策略

**单元测试**:
- HookGenerateService: 测试3种类型生成、选择逻辑、重试逻辑
- EnhancedValidator: 测试4项检查的边界条件
- 覆盖率目标: ≥ 80%

**集成测试**:
- 端到端流程测试（正常流程）
- 重试流程测试（验证不通过）
- 异常流程测试（LLM失败、超时）

**人工测试**:
- 准备20个真实文章
- 对比v2和v3的输出质量
- 盲测胜率目标: ≥ 65%

---

### 10.3 上线检查清单

**代码检查**:
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码Review完成
- [ ] 无明显性能问题

**数据库检查**:
- [ ] 迁移脚本在测试环境验证
- [ ] 生产环境数据库已备份
- [ ] 回滚脚本已准备

**监控检查**:
- [ ] 日志记录完整（耗时、成功率）
- [ ] 错误告警配置完成
- [ ] 性能指标监控配置完成

**回滚准备**:
- [ ] 回滚脚本已测试
- [ ] 回滚流程已文档化
- [ ] 团队成员知晓回滚步骤

---

## 11. 总结

### 11.1 核心改动

1. **新增HookGenerateService**: 生成3个Hook，选择最优
2. **增强SceneGenerateService**: Prompt中加入叙事结构约束
3. **新增EnhancedValidator**: 4项规则检查
4. **扩展Scene Schema**: 新增5个字段
5. **更新LangGraph流程**: 新增2个节点，1个条件边

### 11.2 技术债务

**当前不处理，留待后续**:
- 并行优化（Hook生成 + 文章解析）
- 使用结构化输出（Function Calling）
- 引入轻量级评分模型
- 灰度发布机制

### 11.3 成功标准

**必须达到**:
- 生成成功率 ≥ 95%
- 生成时长 ≤ 70秒
- Hook生成成功率 ≥ 98%
- 用户修改率降低 ≥ 35%

**如果达不到**:
- 执行风险降级方案（见第8章）
- 考虑回滚到v2

---

**文档状态**: 待评审
**下一步**: 技术评审会议
**预计开发时间**: 8个工作日
**风险等级**: 中