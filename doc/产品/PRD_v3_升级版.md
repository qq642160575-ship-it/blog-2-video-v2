# AI短视频生成系统 PRD v3（升级版）

**文档版本**: v3.0
**创建日期**: 2026-04-20
**目标版本**: v3.0 系统升级
**文档状态**: 待评审

---

## 1. 产品背景与目标

### 1.1 当前系统阶段

**系统状态**: 初级可用（MVP+）

当前系统已完成核心技术验证，可以稳定产出：
- ✅ 结构化视频脚本（6-10个场景）
- ✅ 自动语音合成（Edge TTS）
- ✅ 字幕生成与对齐
- ✅ 视频渲染与拼接（Remotion + FFmpeg）
- ✅ 分镜在线编辑与版本控制

**系统评分**: 5.9/10

### 1.2 当前核心问题（引用分析报告）

根据系统分析报告，当前最大问题不是工程失控，而是：

> **缺少"短视频内容设计中间层"**

具体表现为：

**问题1**: 系统直接从"文章理解"跳到"分镜生成"
- 当前流程：`Article Parse → Scene Generate → Render`
- 缺失环节：Hook设计、叙事曲线设计、注意力设计

**问题2**: Scene Schema过于轻量，只能支撑"文本讲解视频"
- 缺少情绪控制字段（emotion、energy_level）
- 缺少注意力设计字段（attention_pattern、hook_type）
- 缺少叙事结构字段（narrative_stage、scene_function）

**问题3**: 过度依赖模型自由生成
- Prompt给了原则，但没有强制结构
- 模型必须临场决定开头怎么抓人、中段怎么推进、结尾怎么收束
- 导致质量不稳定

**问题4**: 没有生成后评估层
- 无法自动检测Hook强度
- 无法识别内容重复
- 无法评估节奏失衡
- 无法验证叙事完整性

### 1.3 本次PRD目标（聚焦核心）

本次升级**只解决最关键问题**，不贪多：

🎯 **核心目标**: 引入"传播设计层"，让系统从"能生成视频"升级到"能生成有传播力的短视频"

**成功标准**:
- Hook强度提升：开头3秒完播率提升30%+
- 内容质量提升：用户修改率降低50%+
- 生成稳定性：质量方差降低40%+

**不做的事**:
- ❌ 不增加新模板（当前3个模板足够）
- ❌ 不重构视觉层（本次聚焦内容层）
- ❌ 不做多语言扩展（先把中文做好）

---

## 2. 产品定位（收敛）

### 2.1 产品是什么

**定位**: AI短视频内容增强引擎

不是简单的"文章转视频工具"，而是：
- 把文章内容改写成适合短视频传播的结构
- 自动设计Hook、叙事曲线、情绪递进
- 输出具备传播潜力的短视频脚本

### 2.2 核心价值

**不是**: 自动生成视频（这只是手段）

**而是**: 提升内容的传播能力
- 让好内容被更多人看到
- 让复杂内容变得易懂
- 让平淡内容变得有记忆点

### 2.3 目标用户

**主要用户**: 内容创作者
- 知识博主、自媒体作者
- 需要把文章/博客转成短视频
- 希望提高传播效率

**次要用户**: 运营人员
- 需要批量生产短视频内容
- 对质量有一定要求

---

## 3. 本次版本核心改动（4个关键升级）

### 改动1: 引入"传播设计层"（Hook + Story Director）

**为什么要做**:
- 当前系统直接从文章跳到分镜，缺少内容策略层
- 模型必须临场决定Hook、叙事结构，质量不稳定
- 对应分析报告问题1、8、9

**不做会怎样**:
- Hook继续不稳定，开头3秒流失率高
- 中段容易平铺，缺少节奏递进
- 结尾缺少收束，用户记不住核心信息

**做完会带来什么变化**:
- Hook质量可控：系统自动生成3-5个Hook方案并选择最优
- 叙事结构清晰：opening → build → turn → payoff → close
- 生成质量稳定：不再依赖模型瞬时发挥

---

### 改动2: 升级Scene Schema（新增12个控制字段）

**为什么要做**:
- 当前Schema只有goal、voiceover、screen_text等基础字段
- 无法表达情绪、注意力、叙事阶段等关键信息
- 对应分析报告问题4、5、6、7

**不做会怎样**:
- Scene之间只有"信息顺序"，没有"情绪顺序"
- 无法控制节奏和注意力
- 后续优化无法落地（因为协议不支持）

**做完会带来什么变化**:
- 每个Scene有明确的功能定位（hook/problem/payoff等）
- 情绪和节奏可控（emotion、energy_level）
- 为后续视觉层升级打好基础

---

### 改动3: 引入Scene Critic（质量评估层）

**为什么要做**:
- 当前系统生成后直接进入渲染，没有质量检查
- 无法自动识别Hook弱、内容重复、节奏失衡等问题
- 对应分析报告问题15

**不做会怎样**:
- 低质量内容直接渲染，浪费资源
- 用户需要手动修改，体验差
- 无法形成质量闭环

**做完会带来什么变化**:
- 自动检测4类质量问题（Hook/重复/节奏/收束）
- 不通过自动重试（最多2次）
- 质量分数可追踪，持续优化

---

### 改动4: 重构Pipeline流程（7步→10步）

**为什么要做**:
- 当前流程缺少内容策略层和评估层
- 新增的Hook、Story、Critic需要独立步骤
- 对应分析报告问题14

**不做会怎样**:
- 新功能无法落地
- 流程混乱，难以维护

**做完会带来什么变化**:
- 流程清晰：每一步职责单一
- 易于调试：可以单独测试每个环节
- 易于扩展：后续可以插入新步骤

**流程对比**:

```
旧流程（7步）:
Article Parse → Scene Generate → Validate → TTS → Subtitle → Render → Done

新流程（10步）:
Article Parse → Hook Generate → Story Director → Scene Generate →
Scene Critic → Validate → TTS → Subtitle → Render → Done
```

---

## 4. 核心功能设计（重点）

### 4.1 传播设计层（新增）

#### 4.1.1 整体架构

传播设计层位于"文章理解"和"分镜生成"之间，负责把文章内容改写成适合短视频传播的结构。

**输入**: ArticleAnalysis（文章分析结果）
```json
{
  "theme": "主题",
  "target_audience": "目标受众",
  "key_points": ["要点1", "要点2"],
  "tone": "语气",
  "complexity": "复杂度"
}
```

**输出**: StoryBlueprint（故事蓝图）
```json
{
  "hook": {
    "type": "question|reveal|contrast|countdown",
    "content": "Hook内容",
    "tension_level": 1-5,
    "curiosity_gap": "好奇缺口描述"
  },
  "narrative_structure": {
    "opening": "开场策略",
    "build": "推进策略",
    "turn": "转折点",
    "payoff": "收益点",
    "close": "收束方式"
  },
  "emotion_curve": [
    {"stage": "opening", "emotion": "surprise", "energy": 4},
    {"stage": "build", "emotion": "tension", "energy": 3}
  ]
}
```

#### 4.1.2 子模块设计

**Hook类型定义**:
- `question`: 提问式（"你知道为什么...吗？"）
- `reveal`: 揭秘式（"99%的人不知道..."）
- `contrast`: 反差式（"你以为...其实..."）
- `countdown`: 倒计时式（"3个方法让你..."）

**生成规则**:
1. 分析文章核心信息，提取最适合做Hook的点
2. 生成3-5个不同类型的Hook方案
3. 为每个方案评分（tension_level、curiosity_gap）
4. 选择得分最高的方案

**Prompt要点**:
```
你是短视频Hook设计专家。基于文章分析结果，生成3-5个开场Hook方案。

要求：
- 每个Hook必须在3秒内抓住注意力
- 必须制造好奇缺口或认知冲突
- 不能夸大或偏离文章事实
- 优先选择反常识、反直觉的点

输出格式：
{
  "hooks": [
    {
      "type": "question",
      "content": "为什么90%的人都用错了这个方法？",
      "tension_level": 4,
      "curiosity_gap": "用户想知道自己是否也用错了"
    }
  ],
  "selected_hook": 0
}
```

---

**模块2: Story Director（叙事导演）**

职责：设计叙事曲线，把文章内容改写成短视频结构

1. **Opening（开场）**: 抛出Hook，建立好奇
   - 时长：3-5秒
   - 目标：抓住注意力，制造悬念

2. **Build（推进）**: 展开问题，建立认知
   - 时长：15-25秒
   - 目标：解释背景，铺垫信息

3. **Turn（转折）**: 认知冲突，打破预期
   - 时长：5-10秒
   - 目标：制造"原来如此"的顿悟感

4. **Payoff（收益）**: 给出答案，提供价值
   - 时长：10-15秒
   - 目标：交付核心信息

5. **Close（收束）**: 总结升华，强化记忆
   - 时长：3-5秒
   - 目标：留下记忆点

**控制变量**:
- `emotion_curve`: 情绪曲线（surprise → tension → relief → confidence）
- `energy_distribution`: 能量分布（开头高、中段稳、转折高、结尾中）
- `information_density`: 信息密度（前低后高，避免开头信息过载）

**Prompt要点**:
```
你是短视频叙事导演。基于文章分析和Hook，设计45-60秒的叙事结构。

要求：
- 必须包含opening/build/turn/payoff/close五个阶段
- 每个阶段明确目标和情绪
- 信息推进要有节奏，不能平铺
- 必须有至少一个认知转折点

输出格式：
{
  "narrative_structure": {
    "opening": "用Hook提问，制造好奇",
    "build": "解释为什么大多数人会犯这个错误",
    "turn": "揭示真正的原因（反直觉）",
    "payoff": "给出正确的方法",
    "close": "总结核心要点"
  },
  "emotion_curve": [...]
}
```

#### 4.1.3 技术实现

**新增文件**:
- `/backend/app/services/hook_generate_service.py`
- `/backend/app/services/story_director_service.py`
- `/backend/app/models/story_blueprint.py`

**新增LangGraph节点**:
- `generate_hook`: 调用HookGenerateService
- `direct_story`: 调用StoryDirectorService

**数据流**:
```
ArticleAnalysis → HookGenerator → StoryDirector → SceneGenerator
```

**兼容性策略**:
- StoryBlueprint作为中间数据，不存数据库
- 保存在GenerationState中，供后续节点使用
- 不影响现有Scene表结构

---

### 4.2 Scene Schema 升级

#### 4.2.1 新增字段定义

在现有Scene模型基础上，新增以下字段：

**内容控制字段**:

```python
# /backend/app/models/scene.py

scene_function = Column(String(50))
# 枚举值: hook | problem | explanation | misconception |
#        comparison | payoff | cta
# 说明: 该场景在视频中的功能定位

narrative_stage = Column(String(20))
# 枚举值: opening | build | turn | payoff | close
# 说明: 该场景在叙事结构中的阶段

carry_over = Column(Text, nullable=True)
# 说明: 如何承接上一个场景（文本描述）
```

**情绪与传播字段**:

```python
emotion = Column(String(30))
# 枚举值: surprise | urgency | clarity | tension |
#        confidence | relief | curiosity
# 说明: 该场景希望传达的主要情绪

energy_level = Column(Integer)
# 范围: 1-5
# 说明: 情绪强度（1=平静，5=高能）

surprise_type = Column(String(30), nullable=True)
# 枚举值: anti-common-sense | mistaken-belief |
#        hidden-cost | hidden-benefit
# 说明: 如果有认知冲突，是哪种类型
```

**视觉控制字段**（为后续视觉层升级预留）:

```python
shot_type = Column(String(30), nullable=True)
# 枚举值: title | list | compare | quote | timeline | focus
# 说明: 镜头类型（当前可选，后续强制）

motion_pattern = Column(String(30), nullable=True)
# 枚举值: fade | pop | slide | zoom | shake | flash | stagger
# 说明: 动效模式（当前可选，后续强制）

emphasis_words = Column(JSON, nullable=True)
# 格式: ["关键词1", "关键词2"]
# 说明: 需要视觉强调的词汇
```

**质量辅助字段**:

```python
must_keep_fact = Column(Text, nullable=True)
# 说明: 必须保留的事实信息（防止AI改写时丢失）

duplicate_risk = Column(Float, default=0.0)
# 范围: 0.0-1.0
# 说明: 与其他场景的重复度（由Critic计算）

quality_score = Column(Float, nullable=True)
# 范围: 0.0-1.0
# 说明: 场景质量分数（由Critic计算）
```

#### 4.2.2 数据库迁移

**新增迁移文件**: `/backend/alembic/versions/xxx_upgrade_scene_schema_v3.py`

#### 4.2.3 Prompt适配

**SceneGenerateService升级**:

原Prompt只要求输出基础字段，现在需要同时输出新增字段：

```python
# 新增到Prompt中的要求

每个场景必须包含以下字段：

1. 基础字段（保持不变）:
   - goal, voiceover, screen_text, duration_sec, pace, transition

2. 内容控制字段（新增）:
   - scene_function: 该场景的功能（hook/problem/explanation等）
   - narrative_stage: 叙事阶段（opening/build/turn/payoff/close）
   - carry_over: 如何承接上一场景

3. 情绪字段（新增）:
   - emotion: 主要情绪（surprise/tension/clarity等）
   - energy_level: 能量等级（1-5）
   - attention_pattern: 注意力模式（question/reveal/contrast等）

4. 质量字段（新增）:
   - must_keep_fact: 必须保留的关键事实

约束：
- 第1个场景的scene_function必须是hook
- 最后1个场景的narrative_stage必须是close
- 相邻场景的energy_level变化不超过2
- 每个narrative_stage至少有1个场景
```

---

### 4.3 Scene Critic（质量评估层）

#### 4.3.1 执行时机

在Pipeline中的位置：

```
Scene Generate → Scene Critic → Validate → TTS
                      ↓
                  不通过？
                      ↓
                 重新生成（最多2次）
```

#### 4.3.2 评估指标

检查项：
- 第1个场景是否有明确的Hook（question/reveal/contrast等）
- Hook是否制造了好奇缺口或认知冲突
- 开场3秒内是否有足够的信息密度

评分标准：
- 优秀（0.8-1.0）：强Hook + 明确冲突 + 信息密集
- 合格（0.6-0.8）：有Hook但不够强
- 不合格（<0.6）：没有Hook或开场平淡

---

**指标2: 内容重复度检查**

检查项：
- 场景间的voiceover文本相似度
- 场景间的screen_text重复度
- 是否有信息冗余

评分标准：
- 优秀（0.8-1.0）：无重复，信息紧凑
- 合格（0.6-0.8）：轻微重复，可接受
- 不合格（<0.6）：明显重复，需要重写

---

**指标3: 节奏平衡检查**

检查项：
- energy_level分布是否合理（不能全是3）
- 是否有节奏高峰（至少1个场景energy≥4）
- 是否有节奏低谷（至少1个场景energy≤2）

评分标准：
- 优秀（0.8-1.0）：有明显起伏，节奏感强
- 合格（0.6-0.8）：有一定起伏
- 不合格（<0.6）：节奏平淡，全程一个调

---

**指标4: 叙事完整性检查**

检查项：
- 是否包含opening/build/payoff/close（turn可选）
- 最后一个场景是否有收束动作
- 是否有明确的价值交付（payoff）

评分标准：
- 优秀（0.8-1.0）：结构完整，收束清晰
- 合格（0.6-0.8）：结构基本完整
- 不合格（<0.6）：结构残缺或没有收束

#### 4.3.3 评估逻辑

**总分计算**:
```python
total_score = (
    hook_score * 0.35 +        # Hook最重要
    duplicate_score * 0.25 +   # 重复度次之
    rhythm_score * 0.20 +      # 节奏
    narrative_score * 0.20     # 完整性
)
```

**通过标准**:
- total_score ≥ 0.7: 通过，进入下一步
- total_score < 0.7: 不通过，重新生成

**重试策略**:
- 第1次不通过：重新调用SceneGenerateService，传入Critic反馈
- 第2次不通过：再重试1次
- 第3次仍不通过：降低标准到0.6，强制通过（避免死循环）

#### 4.3.4 技术实现

**新增文件**:
- `/backend/app/services/scene_critic_service.py`

**核心方法**:
```python
class SceneCriticService:
    def evaluate_scenes(self, scenes: List[SceneData]) -> CriticResult:
        """评估场景质量"""
        hook_score = self._check_hook_strength(scenes[0])
        duplicate_score = self._check_duplicate(scenes)
        rhythm_score = self._check_rhythm(scenes)
        narrative_score = self._check_narrative(scenes)

        total_score = self._calculate_total(...)

        return CriticResult(
            passed=(total_score >= 0.7),
            total_score=total_score,
            feedback="具体问题描述"
        )
```

**新增LangGraph节点**:
- `critique_scenes`: 调用SceneCriticService
- 如果不通过，回到`generate_scenes`节点

---

### 4.4 Pipeline 升级

**完整流程图**:

```
1. load_project
   ↓
2. route_by_job_type
   ↓
3. parse_article (已有)
   ↓
4. generate_hook (新增)
   ↓
5. direct_story (新增)
   ↓
6. generate_scenes (升级)
   ↓
7. critique_scenes (新增)
   ↓ 不通过？→ 回到步骤6（最多2次）
   ↓ 通过
8. validate_scenes (已有)
   ↓
9. generate_tts (已有)
   ↓
10. generate_subtitles (已有)
    ↓
11. prepare_render (已有)
    ↓
12. END
```

#### 4.4.2 节点详细说明

**节点4: generate_hook**
- 输入：ArticleAnalysis
- 输出：HookData（包含选中的Hook方案）
- 耗时：约5-8秒
- 失败处理：重试3次，失败则使用默认Hook

**节点5: direct_story**
- 输入：ArticleAnalysis + HookData
- 输出：StoryBlueprint（叙事蓝图）
- 耗时：约8-12秒
- 失败处理：重试3次，失败则降级为简单结构

**节点6: generate_scenes（升级）**
- 输入：ArticleAnalysis + StoryBlueprint
- 输出：SceneData[]（包含新增字段）
- 耗时：约15-25秒
- 变化：Prompt中新增StoryBlueprint约束

**节点7: critique_scenes**
- 输入：SceneData[]
- 输出：CriticResult（passed + score + feedback）
- 耗时：约3-5秒
- 失败处理：不通过则回到节点6，最多重试2次

#### 4.4.3 GenerationState升级

在现有State基础上新增字段：

```python
# /backend/app/graph/generation_state.py

class GenerationState(TypedDict):
    # 已有字段（保持不变）
    job_id: str
    project_id: str
    analysis: Optional[dict]
    scenes_data: Optional[List[dict]]
    # ...

    # 新增字段
    hook_data: Optional[dict]           # Hook生成结果
    story_blueprint: Optional[dict]     # 叙事蓝图
    critic_result: Optional[dict]       # 评估结果
    retry_count: int                    # 重试次数
```

#### 4.4.4 时长影响

**旧流程总耗时**: 约40-60秒
**新流程总耗时**: 约60-90秒（增加30秒）

增加的时间主要来自：
- Hook生成：+8秒
- Story导演：+12秒
- Critic评估：+5秒
- 可能的重试：+0-30秒（如果需要重试）

**优化方案**（后续可做）:
- Hook和Story可以并行生成（节省10秒）
- Critic可以用更快的模型（节省2秒）

---

## 5. 数据模型定义

### 5.1 StoryBlueprint（故事蓝图）

```python
# /backend/app/models/story_blueprint.py

class StoryBlueprint(BaseModel):
    hook: HookData
    narrative_structure: NarrativeStructure
    emotion_curve: List[EmotionPoint]
    target_duration: int  # 目标时长（秒）

class HookData(BaseModel):
    type: Literal["question", "reveal", "contrast", "countdown"]
    content: str
    tension_level: int  # 1-5
    curiosity_gap: str

class NarrativeStructure(BaseModel):
    opening: str
    build: str
    turn: Optional[str]
    payoff: str
    close: str

class EmotionPoint(BaseModel):
    stage: str
    emotion: str
    energy: int  # 1-5
```

### 5.2 CriticResult（评估结果）

```python
# /backend/app/models/critic_result.py

class CriticResult(BaseModel):
    passed: bool
    total_score: float  # 0.0-1.0
    hook_score: float
    duplicate_score: float
    rhythm_score: float
    narrative_score: float
    feedback: str  # 具体问题描述
    suggestions: List[str]  # 改进建议
```

### 5.3 SceneData升级（输出格式）

```python
# /backend/app/services/scene_generate_service.py

class SceneData(BaseModel):
    # 基础字段（已有）
    goal: str
    voiceover: str
    screen_text: List[str]
    duration_sec: int
    pace: Literal["fast", "medium", "slow"]
    transition: Literal["cut", "fade", "slide"]
    template_type: str
    visual_params: dict

    # 新增字段
    scene_function: Literal["hook", "problem", "explanation",
                           "misconception", "comparison", "payoff", "cta"]
    narrative_stage: Literal["opening", "build", "turn", "payoff", "close"]
    carry_over: Optional[str]
    emotion: Literal["surprise", "urgency", "clarity", "tension",
                    "confidence", "relief", "curiosity"]
    energy_level: int  # 1-5
    attention_pattern: Literal["question", "reveal", "contrast",
                               "countdown", "escalation", "list"]
    surprise_type: Optional[Literal["anti-common-sense", "mistaken-belief",
                                    "hidden-cost", "hidden-benefit"]]
    must_keep_fact: Optional[str]
```

---

## 6. API变化

### 6.1 现有API（无变化）

所有现有API保持不变，向后兼容：
- `POST /projects`
- `GET /projects/{id}`
- `POST /projects/{id}/jobs/generate`
- `GET /jobs/{id}`
- 等等...

### 6.2 新增响应字段

**GET /projects/{id}/scenes** 响应中新增字段：

```json
{
  "scenes": [
    {
      "id": "sc_xxx",
      // 已有字段...
      "scene_function": "hook",
      "narrative_stage": "opening",
      "emotion": "surprise",
      "energy_level": 4,
      "attention_pattern": "question",
      "quality_score": 0.85
    }
  ]
}
```

**GET /jobs/{id}** 响应中新增stage值：

```json
{
  "id": "job_xxx",
  "status": "running",
  "stage": "generate_hook",  // 新增stage值
  "progress": 0.3
}
```

新增的stage值：
- `generate_hook`
- `direct_story`
- `critique_scenes`

---

## 7. 前端影响

### 7.1 进度展示升级

**GenerationProgress.jsx** 需要新增3个阶段：

```javascript
const STAGE_LABELS = {
  // 已有
  'article_parse': '分析文章',
  'scene_generate': '生成分镜',
  'tts_generate': '生成配音',
  // ...

  // 新增
  'generate_hook': '设计开场钩子',
  'direct_story': '设计叙事结构',
  'critique_scenes': '质量评估'
}
```

### 7.2 分镜编辑器增强（可选）

**EditScene.jsx** 可以展示新字段（但不强制）：

- 显示场景功能标签（hook/problem/payoff等）
- 显示情绪和能量等级
- 显示质量分数

这些字段只读，不支持编辑（由AI生成）。

---

## 8. 测试策略

### 8.1 单元测试

**新增测试文件**:
- `test_hook_generate_service.py`
- `test_story_director_service.py`
- `test_scene_critic_service.py`

**测试重点**:
- Hook生成的多样性和质量
- Story结构的完整性
- Critic评分的准确性

### 8.2 集成测试

**测试场景**:
1. 正常流程：文章 → Hook → Story → Scene → Critic通过 → 渲染
2. 重试流程：Critic不通过 → 重新生成 → 通过
3. 降级流程：多次重试失败 → 降低标准 → 强制通过

### 8.3 质量验证

**验证指标**:
- Hook强度：人工评估前100个生成结果，Hook优秀率≥70%
- 重复度：自动检测，重复率<10%
- 节奏感：人工评估，节奏单调率<20%
- 完整性：自动检测，结构完整率≥95%

**对比测试**:
- 使用相同文章，对比v2和v3生成结果
- 盲测：让用户选择更喜欢哪个版本
- 目标：v3胜率≥70%

---

## 9. 实施计划

### 9.1 开发任务拆解

**阶段1: 数据层（1-2天）**
- [ ] 升级Scene模型，新增12个字段
- [ ] 创建数据库迁移文件
- [ ] 创建StoryBlueprint、CriticResult模型
- [ ] 升级GenerationState

**阶段2: 服务层（3-4天）**
- [ ] 实现HookGenerateService
- [ ] 实现StoryDirectorService
- [ ] 实现SceneCriticService
- [ ] 升级SceneGenerateService（适配新Prompt）

**阶段3: 流程层（2-3天）**
- [ ] 新增generate_hook节点
- [ ] 新增direct_story节点
- [ ] 新增critique_scenes节点
- [ ] 实现重试逻辑
- [ ] 更新流程图

**阶段4: 测试与优化（2-3天）**
- [ ] 单元测试
- [ ] 集成测试
- [ ] 质量验证
- [ ] Prompt调优

**阶段5: 前端适配（1天）**
- [ ] 更新进度展示
- [ ] 更新分镜编辑器（可选）

**总计**: 9-13天

### 9.2 风险与应对

**风险1: LLM输出不稳定**
- 应对：增加重试机制，设置降级策略

**风险2: 生成时长增加30秒**
- 应对：优化Prompt，后续考虑并行化

**风险3: Critic标准过严**
- 应对：可配置阈值，初期设为0.6

**风险4: 新字段兼容性**
- 应对：所有新字段nullable，旧数据不受影响

---

## 10. 成功指标

### 10.1 技术指标

- ✅ 生成成功率≥95%（含重试）
- ✅ Critic通过率≥80%（首次）
- ✅ 平均生成时长≤90秒
- ✅ 系统稳定性：无崩溃

### 10.2 质量指标

- ✅ Hook优秀率≥70%（人工评估）
- ✅ 内容重复率<10%（自动检测）
- ✅ 节奏单调率<20%（人工评估）
- ✅ 结构完整率≥95%（自动检测）

### 10.3 用户指标

- ✅ 用户修改率降低50%（对比v2）
- ✅ 盲测胜率≥70%（v3 vs v2）
- ✅ 用户满意度≥4.0/5.0

---

## 11. 后续规划（不在本次范围）

本次PRD聚焦核心问题，以下功能留待后续版本：

**v3.1 - 视觉层升级**:
- 重构visual_params为结构化协议
- 新增视觉映射层
- 扩展模板动效能力

**v3.2 - 多语言支持**:
- 英文内容生成
- 多语言TTS
- 国际化UI

**v3.3 - 批量处理**:
- 多项目并发生成
- 批量导入文章
- 任务队列优化

**v4.0 - AI素材推荐**:
- 图像生成集成
- 视频素材推荐
- 背景音乐匹配

---

## 12. 附录

### 12.1 关键文件清单

**新增文件**:
```
/backend/app/services/hook_generate_service.py
/backend/app/services/story_director_service.py
/backend/app/services/scene_critic_service.py
/backend/app/models/story_blueprint.py
/backend/app/models/critic_result.py
/backend/alembic/versions/xxx_upgrade_scene_schema_v3.py
```

**修改文件**:
```
/backend/app/models/scene.py
/backend/app/graph/generation_graph.py
/backend/app/graph/generation_state.py
/backend/app/services/scene_generate_service.py
/frontend/src/pages/GenerationProgress.jsx
```

### 12.2 参考资料

- 系统分析报告：`/doc/策略/out_1.md`
- 当前架构文档：`/doc/README.md`
- LangGraph文档：https://langchain-ai.github.io/langgraph/

---

**文档结束**

**下一步**: 评审本PRD，确认后进入开发阶段
