# 程序员实现方案：PRD v3 技术落地分析

**角色**: 程序员（落地者 + 吐槽者）
**日期**: 2026-04-20
**输入文档**: PRD_v3_升级版.md + out_3_pro.md
**评审结论**: ⚠️ 两个方案都有问题，我有第三个方案

---

## 0. 开场吐槽（必须先说）

看完产品和技术的文档，我的第一反应是：

**产品经理**: 想法很好，但你是在写科幻小说吗？
- 12个新字段？LLM能稳定输出我直播吃键盘
- AI评估AI？这是套娃还是递归？
- "Hook强度提升30%" - 这数字是抽奖抽出来的吧？

**技术经理**: 你说得都对，但你的方案也有坑
- "Prompt优化2小时搞定" - 你是没调过Prompt吧？
- "规则检查能解决80%问题" - 剩下20%怎么办？用户投诉？
- "4天完成" - 不包括我debug到凌晨3点的时间对吧？

**我的立场**:
- 产品的方向是对的（确实需要Hook和结构优化）
- 技术的务实是对的（确实不能过度工程化）
- 但你们都忽略了一个关键问题：**谁来维护这堆代码？**

---

## 1. 对产品经理的吐槽（逐条批判）

### 吐槽1: 12个新字段 - 你是在为难LLM还是为难我？

**产品说**: 新增12个字段让Scene更结构化

**我的问题**:
```python
# 产品期望的输出
{
  "scene_function": "hook",
  "narrative_stage": "opening",
  "carry_over": "承接上文...",
  "emotion": "surprise",
  "energy_level": 4,
  "attention_pattern": "question",
  "surprise_type": "anti-common-sense",
  "shot_type": "title",
  "motion_pattern": "pop",
  "emphasis_words": ["关键词"],
  "must_keep_fact": "事实...",
  "duplicate_risk": 0.1,
  "quality_score": 0.85
}
```

**现实会是什么样**:
- 第1次调用: LLM漏了3个字段
- 第2次调用: `emotion`和`energy_level`自相矛盾（emotion=calm, energy=5）
- 第3次调用: `scene_function`和`narrative_stage`对不上（function=payoff, stage=opening）
- 第4次调用: `emphasis_words`是空数组
- 第5次调用: 我崩溃了

**边界情况**:
1. LLM输出的枚举值不在预定义范围内（`emotion: "excited"` 但我们只定义了surprise/urgency等）
2. 必填字段为null
3. 数值字段超出范围（`energy_level: 10`）
4. JSON格式错误（多了逗号、少了引号）

**潜在bug**:
```python
# 这段代码会在生产环境炸
scene_data = json.loads(llm_output)
energy = scene_data["energy_level"]  # KeyError!
if energy > 5:  # TypeError if energy is None!
    raise ValueError("Invalid energy")
```

**我的建议**: 只加5个核心字段，其他的别想了
- `scene_role`: hook | body | close（3选1，LLM不会搞错）
- `emotion_level`: 1-5（数字简单）
- `has_hook_keywords`: bool（让LLM判断真假比让它生成枚举靠谱）
- `carry_over`: str（自由文本，不约束）
- `quality_score`: 后端计算，不让LLM生成

---

### 吐槽2: AI Critic - 这是递归还是死循环？

**产品说**: 用AI评估生成质量，不通过就重试

**我的问题**:
```python
# 产品期望的流程
scenes = generate_scenes()
critic_result = critique_scenes(scenes)
if not critic_result.passed:
    scenes = generate_scenes()  # 重试
```

**实际会发生什么**:
```python
# 第1次生成
scenes_v1 = generate_scenes()  # Hook强度: 0.65
critic_v1 = critique(scenes_v1)  # 评分: 0.68, 不通过

# 第2次生成（带反馈）
scenes_v2 = generate_scenes(feedback="Hook不够强")  # Hook强度: 0.72
critic_v2 = critique(scenes_v2)  # 评分: 0.69, 还是不通过（Critic今天心情不好）

# 第3次生成
scenes_v3 = generate_scenes(feedback="Hook还是不够强")  # Hook强度: 0.63（更差了！）
critic_v3 = critique(scenes_v3)  # 评分: 0.71, 勉强通过

# 结果: 第3次最差的反而通过了
```

**边界情况**:
1. Critic永远不满意（阈值设太高）→ 无限重试 → 用户等到天荒地老
2. Critic标准不一致（同样内容，两次评分差距大）
3. 重试后质量反而下降（LLM过度调整）
4. Critic崩溃（API超时、返回格式错误）

**潜在bug**:
```python
retry_count = 0
while not critic_result.passed and retry_count < 3:
    scenes = generate_scenes()
    critic_result = critique_scenes(scenes)
    retry_count += 1
    # Bug: 如果critique_scenes抛异常，retry_count不增加，死循环
```

**我的建议**:
- 不要AI Critic，用规则检查（快、稳定、可调试）
- 如果一定要评估，用后置分析（生成后记录分数，不影响流程）

---

### 吐槽3: Hook + Story Director - 这是两次LLM做同一件事

**产品说**: 先生成Hook，再设计Story结构，最后生成Scene

**我的问题**:
```
Step 1: HookGenerator
输入: 文章分析
输出: "为什么90%的人都用错了这个方法？"

Step 2: StoryDirector
输入: 文章分析 + Hook
输出: opening="用Hook提问", build="解释原因", payoff="给出方法"

Step 3: SceneGenerator
输入: 文章分析 + Hook + Story结构
输出: 6个场景，第1个是Hook，后面按Story结构展开
```

**问题**: Step 2和Step 3在做同一件事（把内容分成场景）

**更大的问题**:
- Hook和Story是"内容策略"
- Scene是"内容实现"
- 但LLM不区分"策略"和"实现"，它只会"生成文本"

**类比**:
```python
# 产品的方案
plan = make_plan()  # LLM生成计划
code = write_code(plan)  # LLM根据计划写代码
# 问题: LLM写代码时会忽略计划，自己重新想一遍

# 更好的方案
code = write_code_with_constraints()  # 在Prompt里加约束，一次生成
```

**我的建议**:
- 不要独立的Hook和Story服务
- 在SceneGenerator的Prompt里加强约束：
  ```
  第1个场景必须是Hook（question/reveal/contrast）
  场景必须遵循opening→build→payoff→close结构
  ```

---

## 2. 对技术经理的吐槽（你也别太理想化）

### 吐槽1: "Prompt优化2小时搞定" - 你是没调过Prompt吧？

**技术说**: 在SceneGenerator的Prompt中加入Hook约束，2小时搞定

**我的现实**:
```
第1小时: 加了约束，LLM输出变短了（从8个场景变成4个）
第2小时: 调整约束，LLM开始胡说八道（Hook变成了广告）
第3小时: 再调整，LLM又回到原来的样子（没有Hook）
第4小时: 我开始怀疑人生
第5小时: 发现是temperature设置的问题
第6小时: 调整temperature，其他场景质量下降了
第7小时: 回滚所有改动，从头再来
第8小时: 终于有点效果了，但还不稳定
第9-20小时: 反复调试、测试、再调试...
```

**边界情况**:
1. Prompt太长（超过token限制）
2. Prompt约束冲突（"要简洁"vs"要详细"）
3. 不同文章类型需要不同Prompt（科技文 vs 情感文）
4. LLM版本更新后Prompt失效

**我的建议**:
- Prompt优化确实可行，但别说2小时
- 预留1周时间调试和测试
- 准备A/B测试对比效果

---

### 吐槽2: "规则检查能解决80%问题" - 剩下20%怎么办？

**技术说**: 用规则检查Hook关键词、重复度、结构完整性

**我的问题**:
```python
# 技术的方案
def validate_hook(scene):
    keywords = ['为什么', '你知道吗', '原来', '竟然']
    if any(kw in scene.voiceover for kw in keywords):
        return True
    return False
```

**问题1**: 关键词检查太死板
```python
# 通过检查，但其实很烂
"为什么我今天要讲这个话题呢？因为..."  # 有"为什么"，但不是Hook

# 不通过检查，但其实很好
"90%的人都不知道这个秘密"  # 没有关键词，但Hook很强
```

**问题2**: 规则会被LLM"钻空子"
```python
# LLM学会了套路
scene_1 = "为什么xxx？"  # 满足关键词要求
scene_2 = "因为xxx"      # 但内容很水
```

**边界情况**:
1. 关键词列表不完整（新的Hook模式出现）
2. 关键词在错误的位置（在场景中间而不是开头）
3. 多个场景都有关键词（无法判断哪个是真Hook）
4. 关键词是英文或其他语言

**我的建议**:
- 规则检查是必要的，但不够
- 需要结合简单的NLP（如句子类型判断、情感分析）
- 或者用轻量级模型做二分类（是Hook / 不是Hook）

---

### 吐槽3: "4天完成" - 不包括我debug到凌晨3点的时间对吧？

**技术说**:
- Day 1: Prompt优化
- Day 2: Validator增强
- Day 3: Schema扩展
- Day 4: 效果验证

**我的现实**:
```
Day 1: Prompt优化（实际8小时变成16小时）
Day 2: 发现Prompt改动影响了其他场景，回滚重来
Day 3: Validator增强，写了200行代码
Day 4: 发现Validator太严格，90%的生成都不通过
Day 5: 调整Validator阈值，写单元测试
Day 6: Schema扩展，数据库迁移
Day 7: 发现迁移脚本有bug，旧数据丢失
Day 8: 修复迁移脚本，重新迁移
Day 9: 集成测试，发现5个新bug
Day 10: 修bug，修bug，修bug
Day 11-14: 效果验证，发现Prompt还需要调整，回到Day 1
```

**边界情况**:
1. 数据库迁移失败（旧数据格式不兼容）
2. Prompt改动影响现有功能（回归bug）
3. Validator误杀（好内容被判定为不合格）
4. 性能问题（Validator太慢）

**我的建议**:
- 预留2周时间（10个工作日）
- 每天留出buffer处理意外情况
- 先在测试环境跑1周，再上生产

---

## 3. 我的方案（程序员版v3-pragmatic）

### 3.1 核心思路

**产品的问题**: 想得太多，要得太多
**技术的问题**: 想得太简单，估得太乐观
**我的方案**: 取中间，加保险

### 3.2 方案对比

| 维度 | 产品方案 | 技术方案 | 我的方案 |
|------|---------|---------|---------|
| 新增服务 | 3个（Hook/Story/Critic） | 0个 | 1个（HookGenerator） |
| 新增字段 | 12个 | 3个 | 5个 |
| LLM调用 | 5次 | 2次 | 3次 |
| 生成延迟 | +50秒 | +5秒 | +15秒 |
| 开发时间 | 20天 | 4天 | 8天 |
| 风险等级 | 高 | 中 | 中低 |
| 效果预期 | 100%? | 85% | 90% |

### 3.3 为什么要加HookGenerator？

**技术说**: Prompt优化就够了
**我说**: 不够，原因如下

1. **Hook是最重要的**（开头3秒决定完播率）
2. **Hook需要多样性**（同一个Prompt生成的Hook会趋同）
3. **Hook需要可控**（独立服务可以单独调优）
4. **成本可接受**（+8秒延迟，+1个LLM调用）

**但我不要Story和Critic**:
- Story: 用Prompt约束替代（技术是对的）
- Critic: 用规则检查替代（技术是对的）

### 3.4 为什么要5个字段而不是3个或12个？

**技术说**: 3个就够（scene_role, emotion_level, quality_score）
**产品说**: 12个才完整
**我说**: 5个刚好

**必须要的3个**（技术是对的）:
- `scene_role`: hook | body | close
- `emotion_level`: 1-5
- `quality_score`: 0.0-1.0

**我要加的2个**:
- `hook_type`: question | reveal | contrast | countdown（记录Hook类型，方便分析）
- `narrative_stage`: opening | build | payoff | close（比scene_role更细，但不要turn）

**为什么不要其他7个**:
- `scene_function`: 和scene_role重复
- `carry_over`: LLM生成不稳定，用处不大
- `attention_pattern`: 和hook_type重复
- `surprise_type`: 太细了，当前用不到
- `shot_type/motion_pattern`: 视觉层的事，别混在内容层
- `emphasis_words`: LLM经常输出空数组
- `must_keep_fact`: 理想很美好，现实很骨感
- `duplicate_risk`: 后端计算，不让LLM生成

---

## 4. 功能实现拆解

### 4.1 核心改动点

**改动1: 新增HookGenerateService**

职责: 生成3个Hook方案，选择最优

```python
# /backend/app/services/hook_generate_service.py

class HookGenerateService:
    def generate_hooks(self, analysis: dict) -> HookResult:
        """生成3个Hook方案"""
        prompt = self._build_prompt(analysis)
        response = self.llm.invoke(prompt)
        hooks = self._parse_response(response)
        selected = self._select_best(hooks)
        return HookResult(hooks=hooks, selected=selected)

    def _select_best(self, hooks: List[Hook]) -> int:
        """选择最优Hook（简单规则）"""
        # 规则1: 优先选question类型（疑问句完播率高）
        # 规则2: 其次选contrast类型（反差吸引人）
        # 规则3: 最后选reveal类型
        for i, hook in enumerate(hooks):
            if hook.type == "question":
                return i
        for i, hook in enumerate(hooks):
            if hook.type == "contrast":
                return i
        return 0
```

**改动2: 增强SceneGenerateService的Prompt**

```python
# /backend/app/services/scene_generate_service.py

ENHANCED_PROMPT = """
你是短视频脚本专家。基于文章分析和Hook，生成6-10个场景。

【强制约束】
1. 第1个场景必须使用提供的Hook作为开场
2. 叙事结构必须遵循：
   - 场景1-2: opening（抛出Hook，建立好奇）
   - 场景3-5: build（展开问题，铺垫信息）
   - 场景6-7: payoff（给出答案，交付价值）
   - 场景8: close（总结收束）
3. 情绪控制：
   - opening: 高能量（4-5）
   - build: 中能量（2-3）
   - payoff: 高能量（4-5）
   - close: 中能量（3）
4. 禁止：
   - 场景间内容重复
   - 平铺直叙无起伏

【输出格式】
每个场景必须包含：
- goal, voiceover, screen_text, duration_sec, pace, transition（已有字段）
- scene_role: hook | body | close
- narrative_stage: opening | build | payoff | close
- emotion_level: 1-5
- hook_type: question | reveal | contrast | countdown（仅第1个场景）
"""
```

**改动3: 增强Validator（规则检查）**

```python
# /backend/app/services/validator.py

class EnhancedValidator:
    def validate_scenes(self, scenes: List[Scene]) -> ValidationResult:
        """增强的场景验证"""
        errors = []

        # 检查1: Hook验证
        if not self._validate_hook(scenes[0]):
            errors.append("第1个场景缺少有效Hook")

        # 检查2: 重复度检查
        if self._check_duplicate(scenes):
            errors.append("场景间内容重复")

        # 检查3: 结构完整性
        if not self._check_structure(scenes):
            errors.append("缺少必要的叙事阶段")

        # 检查4: 节奏检查
        if not self._check_rhythm(scenes):
            errors.append("节奏过于平淡")

        return ValidationResult(
            passed=(len(errors) == 0),
            errors=errors
        )

    def _validate_hook(self, first_scene: Scene) -> bool:
        """Hook验证（规则+简单NLP）"""
        text = first_scene.voiceover

        # 规则1: 检查Hook关键词
        hook_keywords = [
            '为什么', '你知道吗', '原来', '竟然', '没想到',
            '真相', '秘密', '误区', '方法', '技巧'
        ]
        has_keyword = any(kw in text for kw in hook_keywords)

        # 规则2: 检查句子类型（疑问句或感叹句）
        has_question = '?' in text or '？' in text
        has_exclamation = '!' in text or '！' in text

        # 规则3: 检查数字（"90%的人"、"3个方法"）
        import re
        has_number = bool(re.search(r'\d+', text))

        # 满足任意2个条件即可
        score = sum([has_keyword, has_question or has_exclamation, has_number])
        return score >= 2

    def _check_duplicate(self, scenes: List[Scene]) -> bool:
        """重复度检查"""
        from difflib import SequenceMatcher

        for i in range(len(scenes)):
            for j in range(i+1, len(scenes)):
                similarity = SequenceMatcher(
                    None,
                    scenes[i].voiceover,
                    scenes[j].voiceover
                ).ratio()

                if similarity > 0.6:  # 相似度阈值
                    return True
        return False

    def _check_structure(self, scenes: List[Scene]) -> bool:
        """结构完整性检查"""
        stages = [s.narrative_stage for s in scenes]
        required = ['opening', 'build', 'payoff', 'close']
        return all(stage in stages for stage in required)

    def _check_rhythm(self, scenes: List[Scene]) -> bool:
        """节奏检查"""
        energy_levels = [s.emotion_level for s in scenes]

        # 检查1: 不能全是3（平淡）
        if all(e == 3 for e in energy_levels):
            return False

        # 检查2: 必须有至少1个高峰（≥4）
        if not any(e >= 4 for e in energy_levels):
            return False

        return True
```

**改动4: 最小化Schema扩展**

```python
# /backend/app/models/scene.py

# 新增字段（5个）
scene_role = Column(String(20), nullable=False, default='body')
# 枚举: hook | body | close

narrative_stage = Column(String(20), nullable=False, default='build')
# 枚举: opening | build | payoff | close

emotion_level = Column(Integer, nullable=False, default=3)
# 范围: 1-5

hook_type = Column(String(20), nullable=True)
# 枚举: question | reveal | contrast | countdown
# 仅第1个场景有值

quality_score = Column(Float, nullable=True)
# 范围: 0.0-1.0
# 由Validator计算
```

---

## 5. API设计（示例）

### 5.1 内部API（服务间调用）

**HookGenerateService.generate_hooks()**

```python
# 输入
{
    "theme": "如何提高工作效率",
    "key_points": ["时间管理", "工具使用", "习惯养成"],
    "target_audience": "职场人士",
    "tone": "实用"
}

# 输出
{
    "hooks": [
        {
            "type": "question",
            "content": "为什么你每天忙到飞起，却总觉得没做什么？",
            "score": 0.85
        },
        {
            "type": "contrast",
            "content": "你以为多任务能提高效率？其实是在浪费时间",
            "score": 0.78
        },
        {
            "type": "reveal",
            "content": "90%的人不知道的3个时间管理秘密",
            "score": 0.72
        }
    ],
    "selected_index": 0,
    "selected_hook": {
        "type": "question",
        "content": "为什么你每天忙到飞起，却总觉得没做什么？"
    }
}
```

**EnhancedValidator.validate_scenes()**

```python
# 输入
[
    {
        "voiceover": "为什么你每天忙到飞起...",
        "scene_role": "hook",
        "narrative_stage": "opening",
        "emotion_level": 4,
        "hook_type": "question"
    },
    # ... 其他场景
]

# 输出
{
    "passed": True,
    "errors": [],
    "warnings": ["场景3和场景5的情绪等级相同，可能缺少变化"],
    "quality_score": 0.82,
    "details": {
        "hook_valid": True,
        "no_duplicate": True,
        "structure_complete": True,
        "rhythm_ok": True
    }
}
```

### 5.2 数据库Schema变更

**迁移脚本**

```python
# /backend/alembic/versions/xxx_add_scene_v3_fields.py

def upgrade():
    # 新增5个字段
    op.add_column('scenes', sa.Column('scene_role', sa.String(20),
                  nullable=False, server_default='body'))
    op.add_column('scenes', sa.Column('narrative_stage', sa.String(20),
                  nullable=False, server_default='build'))
    op.add_column('scenes', sa.Column('emotion_level', sa.Integer(),
                  nullable=False, server_default='3'))
    op.add_column('scenes', sa.Column('hook_type', sa.String(20),
                  nullable=True))
    op.add_column('scenes', sa.Column('quality_score', sa.Float(),
                  nullable=True))

def downgrade():
    # 回滚
    op.drop_column('scenes', 'quality_score')
    op.drop_column('scenes', 'hook_type')
    op.drop_column('scenes', 'emotion_level')
    op.drop_column('scenes', 'narrative_stage')
    op.drop_column('scenes', 'scene_role')
```

---

## 6. 核心流程（时序图）

### 6.1 新流程（8步）

```
1. load_project
   ↓
2. parse_article (已有)
   ↓
3. generate_hook (新增) ← +8秒
   ↓
4. generate_scenes (增强) ← Prompt包含Hook和结构约束
   ↓
5. validate_scenes (增强) ← 新增4项检查
   ↓ 不通过？
   ↓ 重试1次（回到步骤4）
   ↓ 还不通过？降低标准，强制通过
   ↓
6. generate_tts (已有)
   ↓
7. generate_subtitles (已有)
   ↓
8. prepare_render (已有)
```

### 6.2 时序图（详细）

```
User → API: POST /projects/{id}/jobs/generate

API → LangGraph: 启动生成流程

LangGraph → ArticleParser: 分析文章
ArticleParser → LangGraph: 返回analysis

LangGraph → HookGenerator: 生成Hook (新增)
HookGenerator → LLM: 调用LLM
LLM → HookGenerator: 返回3个Hook
HookGenerator → LangGraph: 返回selected_hook

LangGraph → SceneGenerator: 生成场景 (增强)
SceneGenerator → LLM: 调用LLM (带Hook约束)
LLM → SceneGenerator: 返回scenes
SceneGenerator → LangGraph: 返回scenes

LangGraph → Validator: 验证场景 (增强)
Validator → Validator: Hook检查
Validator → Validator: 重复度检查
Validator → Validator: 结构检查
Validator → Validator: 节奏检查

alt 验证通过
    Validator → LangGraph: passed=True
    LangGraph → TTSService: 生成语音
else 验证不通过 (第1次)
    Validator → LangGraph: passed=False, errors=[...]
    LangGraph → SceneGenerator: 重新生成 (带错误反馈)
    SceneGenerator → LangGraph: 返回新scenes
    LangGraph → Validator: 再次验证
    alt 第2次通过
        Validator → LangGraph: passed=True
    else 第2次不通过
        Validator → LangGraph: passed=False
        LangGraph → LangGraph: 降低标准，强制通过
    end
end

LangGraph → API: 返回结果
API → User: 返回job_id
```

### 6.3 错误处理流程

```python
# /backend/app/graph/generation_graph.py

def generate_scenes_node(state: GenerationState) -> GenerationState:
    """生成场景节点（带重试）"""
    try:
        # 第1次生成
        scenes = scene_service.generate(
            analysis=state["analysis"],
            hook=state["hook_data"]
        )
        state["scenes_data"] = scenes
        state["retry_count"] = 0
        return state

    except Exception as e:
        logger.error(f"场景生成失败: {e}")
        # 重试3次
        if state.get("retry_count", 0) < 3:
            state["retry_count"] = state.get("retry_count", 0) + 1
            return generate_scenes_node(state)  # 递归重试
        else:
            # 3次都失败，抛出异常
            raise GenerationError("场景生成失败，已重试3次")

def validate_scenes_node(state: GenerationState) -> GenerationState:
    """验证场景节点（带降级）"""
    scenes = state["scenes_data"]
    result = validator.validate_scenes(scenes)

    if result.passed:
        # 验证通过
        state["validation_passed"] = True
        return state
    else:
        # 验证不通过
        if state.get("validation_retry_count", 0) < 1:
            # 第1次不通过，重新生成
            logger.warning(f"验证不通过: {result.errors}")
            state["validation_retry_count"] = 1
            state["validation_feedback"] = result.errors
            # 回到generate_scenes节点
            return {"__next__": "generate_scenes"}
        else:
            # 第2次还不通过，降低标准
            logger.warning("验证第2次不通过，降低标准强制通过")
            state["validation_passed"] = True
            state["validation_degraded"] = True
            return state
```

---

## 7. 边界情况（必须处理）

### 7.1 LLM输出异常

**情况1: JSON格式错误**
```python
# LLM输出
{
  "hooks": [
    {"type": "question", "content": "为什么...",}  # 多了逗号
  ]
}

# 处理
try:
    data = json.loads(llm_output)
except json.JSONDecodeError:
    # 尝试修复（去除多余逗号）
    fixed = llm_output.replace(',}', '}').replace(',]', ']')
    data = json.loads(fixed)
```

**情况2: 必填字段缺失**
```python
# LLM输出
{
  "scene_role": "hook",
  # 缺少narrative_stage
}

# 处理
scene_data = {
    "scene_role": data.get("scene_role", "body"),  # 默认值
    "narrative_stage": data.get("narrative_stage", "build"),
    "emotion_level": data.get("emotion_level", 3),
}
```

**情况3: 枚举值不合法**
```python
# LLM输出
{"scene_role": "introduction"}  # 不在枚举范围内

# 处理
VALID_ROLES = ["hook", "body", "close"]
role = data.get("scene_role", "body")
if role not in VALID_ROLES:
    logger.warning(f"无效的scene_role: {role}, 使用默认值")
    role = "body"
```

### 7.2 数据库迁移问题

**情况1: 旧数据没有新字段**
```python
# 迁移脚本中设置默认值
op.add_column('scenes', sa.Column('scene_role', sa.String(20),
              nullable=False, server_default='body'))

# 迁移后，旧数据自动填充默认值
```

**情况2: 迁移失败回滚**
```python
# 测试迁移
alembic upgrade head --sql > migration.sql  # 先生成SQL
# 检查SQL无误后再执行

# 如果失败，回滚
alembic downgrade -1
```

### 7.3 Validator误判

**情况1: Hook检查过严**
```python
# 好的Hook，但没有关键词
"想象一下，如果你每天能多出2小时..."

# 解决: 降低阈值（满足2个条件即可，而不是3个）
score = sum([has_keyword, has_question, has_number])
return score >= 2  # 而不是 >= 3
```

**情况2: 重复度检查误杀**
```python
# 两个场景相似度高，但不是重复
scene_1 = "第一个方法是时间管理"
scene_2 = "第二个方法是任务管理"

# 解决: 提高阈值
if similarity > 0.7:  # 而不是0.6
    return True
```

### 7.4 性能问题

**情况1: Validator太慢**
```python
# 问题: 重复度检查是O(n²)
for i in range(len(scenes)):
    for j in range(i+1, len(scenes)):
        similarity = calculate_similarity(scenes[i], scenes[j])

# 解决: 只检查相邻场景
for i in range(len(scenes) - 1):
    similarity = calculate_similarity(scenes[i], scenes[i+1])
```

**情况2: LLM调用超时**
```python
# 设置超时
response = self.llm.invoke(prompt, timeout=30)

# 超时重试
for attempt in range(3):
    try:
        response = self.llm.invoke(prompt, timeout=30)
        break
    except TimeoutError:
        if attempt == 2:
            raise
        time.sleep(2 ** attempt)  # 指数退避
```

---

## 8. 潜在bug点（重点关注）

### 8.1 LLM相关bug

**Bug 1: LLM输出字段顺序不一致**
```python
# 有时输出
{"scene_role": "hook", "narrative_stage": "opening"}

# 有时输出
{"narrative_stage": "opening", "scene_role": "hook"}

# 解决: 用dict而不是依赖顺序
data = json.loads(response)
scene_role = data["scene_role"]  # 而不是data[0]
```

**Bug 2: LLM输出字段名大小写不一致**
```python
# 有时输出
{"scene_role": "hook"}

# 有时输出
{"Scene_Role": "hook"}

# 解决: 统一转小写
data = {k.lower(): v for k, v in json.loads(response).items()}
```

**Bug 3: LLM输出数组长度不符合预期**
```python
# 期望3个Hook，但LLM只输出了2个
{"hooks": [hook1, hook2]}

# 解决: 检查长度
hooks = data.get("hooks", [])
if len(hooks) < 3:
    logger.warning(f"Hook数量不足: {len(hooks)}, 期望3个")
    # 用默认Hook补齐
    while len(hooks) < 3:
        hooks.append(default_hook)
```

### 8.2 数据库相关bug

**Bug 4: 迁移脚本执行顺序错误**
```python
# 错误: 先删除旧字段，再添加新字段
def upgrade():
    op.drop_column('scenes', 'old_field')
    op.add_column('scenes', 'new_field')
    # 如果中间失败，数据丢失

# 正确: 先添加新字段，再删除旧字段
def upgrade():
    op.add_column('scenes', 'new_field')
    # 迁移数据
    op.execute("UPDATE scenes SET new_field = old_field")
    # 确认无误后再删除
    op.drop_column('scenes', 'old_field')
```

**Bug 5: 并发写入冲突**
```python
# 问题: 两个请求同时更新同一个scene
request_1: UPDATE scenes SET quality_score = 0.8 WHERE id = 'sc_123'
request_2: UPDATE scenes SET quality_score = 0.9 WHERE id = 'sc_123'

# 解决: 使用乐观锁
class Scene(Base):
    version = Column(Integer, default=0)

# 更新时检查版本
UPDATE scenes SET quality_score = 0.8, version = version + 1
WHERE id = 'sc_123' AND version = 5
```

### 8.3 Validator相关bug

**Bug 6: 正则表达式性能问题**
```python
# 问题: 复杂正则导致ReDoS攻击
pattern = r'(a+)+b'
re.search(pattern, 'a' * 1000)  # 卡死

# 解决: 使用简单正则，设置超时
import re
import signal

def timeout_handler(signum, frame):
    raise TimeoutError()

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(1)  # 1秒超时
try:
    result = re.search(pattern, text)
finally:
    signal.alarm(0)
```

**Bug 7: 相似度计算内存溢出**
```python
# 问题: 场景太多，O(n²)内存爆炸
scenes = [...]  # 100个场景
for i in range(len(scenes)):
    for j in range(i+1, len(scenes)):
        similarity_matrix[i][j] = calculate(scenes[i], scenes[j])
# 100*100 = 10000次计算

# 解决: 只检查相邻场景
for i in range(len(scenes) - 1):
    if calculate(scenes[i], scenes[i+1]) > 0.7:
        return False
```

### 8.4 流程控制bug

**Bug 8: 重试计数器未重置**
```python
# 问题: 第2个项目生成时，retry_count还是上一个项目的值
state["retry_count"] = 3  # 上一个项目的值
# 导致第2个项目直接失败

# 解决: 每次生成前重置
def generate_scenes_node(state):
    if "retry_count" not in state:
        state["retry_count"] = 0
    # ...
```

**Bug 9: 循环引用导致内存泄漏**
```python
# 问题: state中保存了大量中间数据
state["analysis"] = {...}  # 10KB
state["hook_data"] = {...}  # 5KB
state["scenes_data"] = [...]  # 50KB
state["validation_result"] = {...}  # 10KB
# 每个请求75KB，1000个请求 = 75MB

# 解决: 及时清理不需要的数据
def cleanup_state(state):
    # 只保留必要的数据
    keep_keys = ["job_id", "project_id", "scenes_data"]
    for key in list(state.keys()):
        if key not in keep_keys:
            del state[key]
```

### 8.5 并发相关bug

**Bug 10: 全局变量竞态条件**
```python
# 问题: 多个请求共享全局变量
hook_cache = {}  # 全局缓存

def generate_hook(analysis):
    key = hash(analysis)
    if key in hook_cache:
        return hook_cache[key]
    result = llm.invoke(...)
    hook_cache[key] = result  # 竞态条件
    return result

# 解决: 使用线程安全的缓存
from threading import Lock
cache_lock = Lock()

def generate_hook(analysis):
    key = hash(analysis)
    with cache_lock:
        if key in hook_cache:
            return hook_cache[key]
    result = llm.invoke(...)
    with cache_lock:
        hook_cache[key] = result
    return result
```

---

## 9. 最终建议（给产品和技术）

### 9.1 给产品经理

**你对的地方**:
- ✅ Hook确实是最重要的（开头3秒决定完播率）
- ✅ 需要叙事结构（opening→build→payoff→close）
- ✅ 需要情绪控制（不能平铺直叙）

**你错的地方**:
- ❌ 12个字段太多了（LLM输不出来）
- ❌ AI Critic不靠谱（AI评估AI是循环论证）
- ❌ Story Director是多余的（和SceneGenerator做同一件事）

**我的建议**:
1. 接受我的方案（1个服务 + 5个字段）
2. 先上线验证效果，再决定是否加功能
3. 不要一次性大改，渐进式迭代
4. 用数据说话，不要拍脑袋定KPI

---

### 9.2 给技术经理

**你对的地方**:
- ✅ 不要过度工程化
- ✅ 用Prompt优化替代部分服务
- ✅ 用规则检查替代AI Critic
- ✅ 渐进式迭代

**你错的地方**:
- ❌ "2小时搞定Prompt" - 太乐观了
- ❌ "4天完成" - 没考虑debug时间
- ❌ "规则检查能解决80%问题" - 剩下20%怎么办？

**我的建议**:
1. 加一个HookGenerator（Hook太重要了，值得独立服务）
2. 预留2周时间（不是4天）
3. 规则检查要结合简单NLP（不能只靠关键词）
4. 准备Plan B（如果效果不够，怎么办？）

---

### 9.3 我的最终方案（v3-pragmatic）

**核心改动**:
1. 新增HookGenerateService（生成3个Hook，选最优）
2. 增强SceneGenerator的Prompt（加入Hook和结构约束）
3. 增强Validator（4项检查：Hook/重复/结构/节奏）
4. 新增5个字段（scene_role, narrative_stage, emotion_level, hook_type, quality_score）

**成本**:
- 开发时间: 8天（vs 产品的20天，技术的4天）
- LLM调用: 3次（vs 产品的5次，技术的2次）
- 生成延迟: +15秒（vs 产品的+50秒，技术的+5秒）
- 新增代码: ~500行（vs 产品的~2000行，技术的~300行）

**效果预期**:
- Hook质量提升: 60-70%（vs 产品的100%?，技术的50%）
- 用户修改率降低: 40%（vs 产品的50%，技术的30%）
- 生成成功率: 95%+（vs 产品的<50%，技术的90%）

**风险**:
- 低（vs 产品的高，技术的中）
- 有回滚方案（数据库迁移可回滚）
- 有降级策略（Validator不通过可降低标准）

**实施计划**:
- Week 1: HookGenerator + Prompt优化 + 单元测试
- Week 2: Validator增强 + Schema扩展 + 集成测试
- Week 3: 测试环境验证 + 效果评估
- Week 4: 生产环境上线 + 监控调优

---

## 10. 开发任务清单（可直接执行）

### Phase 1: 数据层（2天）

- [ ] 创建数据库迁移脚本（新增5个字段）
- [ ] 更新Scene模型定义
- [ ] 编写迁移测试脚本
- [ ] 在测试环境执行迁移

### Phase 2: 服务层（3天）

- [ ] 实现HookGenerateService
  - [ ] 编写Prompt模板
  - [ ] 实现Hook选择逻辑
  - [ ] 处理LLM输出异常
  - [ ] 编写单元测试
- [ ] 增强SceneGenerateService
  - [ ] 更新Prompt模板（加入Hook和结构约束）
  - [ ] 适配新字段输出
  - [ ] 处理字段验证
  - [ ] 编写单元测试
- [ ] 增强Validator
  - [ ] 实现Hook检查
  - [ ] 实现重复度检查
  - [ ] 实现结构检查
  - [ ] 实现节奏检查
  - [ ] 编写单元测试

### Phase 3: 流程层（2天）

- [ ] 新增generate_hook节点
- [ ] 更新generate_scenes节点（接收hook_data）
- [ ] 更新validate_scenes节点（新增4项检查）
- [ ] 实现重试逻辑（验证不通过重试1次）
- [ ] 实现降级逻辑（第2次不通过降低标准）
- [ ] 更新GenerationState（新增hook_data等字段）
- [ ] 编写集成测试

### Phase 4: 测试与优化（3天）

- [ ] 单元测试（覆盖率>80%）
- [ ] 集成测试（端到端测试）
- [ ] 性能测试（生成时长、成功率）
- [ ] 边界情况测试（LLM输出异常、数据库异常等）
- [ ] Prompt调优（测试不同文章类型）
- [ ] Validator阈值调优（避免误杀）

### Phase 5: 上线与监控（2天）

- [ ] 在测试环境验证1周
- [ ] 准备回滚方案
- [ ] 生产环境数据库迁移
- [ ] 灰度发布（10% → 50% → 100%）
- [ ] 监控关键指标（生成时长、成功率、Hook质量）
- [ ] 收集用户反馈
- [ ] 根据数据调整Prompt和阈值

**总计**: 12天（vs 产品的20天，技术的4天）

---

## 11. 成功标准（可量化）

### 11.1 技术指标

- ✅ 生成成功率 ≥ 95%（含重试）
- ✅ 平均生成时长 ≤ 70秒（vs 当前55秒）
- ✅ Hook生成成功率 ≥ 98%
- ✅ Validator首次通过率 ≥ 85%
- ✅ 系统稳定性：无崩溃，无数据丢失

### 11.2 质量指标

- ✅ Hook优秀率 ≥ 65%（人工评估100个样本）
- ✅ 内容重复率 < 10%（自动检测）
- ✅ 结构完整率 ≥ 95%（自动检测）
- ✅ 节奏单调率 < 25%（人工评估）

### 11.3 用户指标

- ✅ 用户修改率降低 ≥ 35%（对比v2）
- ✅ 盲测胜率 ≥ 65%（v3 vs v2，100个样本）
- ✅ 用户满意度 ≥ 3.8/5.0
- ✅ 用户投诉率 < 5%

### 11.4 如果达不到怎么办？

**如果Hook质量不达标**:
- Plan B: 增加Hook候选数量（3个→5个）
- Plan C: 引入轻量级Hook评分模型

**如果Validator误杀率高**:
- Plan B: 降低阈值（从2个条件降到1个）
- Plan C: 增加人工审核环节

**如果生成时长过长**:
- Plan B: 优化Prompt（减少token数量）
- Plan C: 使用更快的LLM模型

---

**文档结束**

**下一步**:
1. 产品、技术、程序员三方会议，确定最终方案
2. 如果采用我的方案，开始Phase 1开发
3. 如果不采用，说明理由，我再调整方案
