# AI短视频生成系统 v3 - 开发任务列表（单人执行版）

**文档版本**: v3.0
**创建日期**: 2026-04-20
**角色**: 全栈工程师（单人开发）
**目标**: 从0到MVP，顺序执行，不返工

---

## 0. 开发策略（必读）

### 核心思路
👉 **先打通主链路（端到端），再填充细节**

### 验证原则
每一步都要能：
- 跑起来（能执行）
- 看到结果（有输出）
- 确认正确（符合预期）

### 开发顺序
```
数据结构 → Mock主链路 → 替换真实AI → 增强功能 → 异常处理
```

---

# 1. 开发主链路（核心，按时间顺序）

## Step 1: 定义数据结构（Day 1 上午，2小时）

**做什么**: 定义Scene的新字段和Hook数据结构

**产出**:
```python
# /backend/app/models/scene.py
class Scene(Base):
    # ... 原有字段 ...

    # 新增字段（先不加到数据库，用内存对象验证）
    scene_role: str = "body"  # hook | body | close
    narrative_stage: str = "build"  # opening | build | payoff | close
    emotion_level: int = 3  # 1-5
    hook_type: Optional[str] = None  # question | reveal | contrast
    quality_score: Optional[float] = None  # 0.0-1.0
```

```python
# /backend/app/schemas/hook.py (新建)
from pydantic import BaseModel
from typing import List

class Hook(BaseModel):
    type: str  # question | reveal | contrast
    content: str
    score: float

class HookResult(BaseModel):
    hooks: List[Hook]
    selected_index: int
```

**验证方式**:
```python
# 写一个测试脚本
hook = Hook(type="question", content="测试", score=0.8)
print(hook.dict())  # 能打印出来就OK
```

---

## Step 2: 实现HookGenerateService（Mock版）（Day 1 下午，3小时）

**做什么**: 先用硬编码返回3个Hook，不调用真实LLM

**产出**:
```python
# /backend/app/services/hook_generate_service.py (新建)
class HookGenerateService:
    def generate_hooks(self, analysis: dict) -> HookResult:
        """Mock版本：返回固定的3个Hook"""
        theme = analysis.get("theme", "未知主题")

        hooks = [
            Hook(
                type="question",
                content=f"为什么{theme}这么重要？",
                score=0.85
            ),
            Hook(
                type="contrast",
                content=f"你以为{theme}很简单？其实大部分人都错了",
                score=0.78
            ),
            Hook(
                type="reveal",
                content=f"90%的人不知道的{theme}秘密",
                score=0.72
            )
        ]

        selected_index = 0  # 优先选question
        return HookResult(hooks=hooks, selected_index=selected_index)
```

**验证方式**:
```python
# 写一个测试脚本 test_hook_service.py
service = HookGenerateService()
result = service.generate_hooks({"theme": "时间管理"})
print(result.hooks[0].content)  # 应该输出: "为什么时间管理这么重要？"
assert len(result.hooks) == 3
assert result.selected_index == 0
```

---

## Step 3: 实现EnhancedValidator（Day 1 下午，2小时）

**做什么**: 实现4项检查，先用简单逻辑

**产出**:
```python
# /backend/app/services/enhanced_validator.py (新建)
import re
from difflib import SequenceMatcher
from typing import List

class ValidationResult:
    def __init__(self, passed: bool, errors: List[str], forced: bool = False):
        self.passed = passed
        self.errors = errors
        self.forced = forced

class EnhancedValidator:
    def validate_scenes(self, scenes: List[Scene]) -> ValidationResult:
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

        return ValidationResult(passed=(len(errors) == 0), errors=errors)

    def _validate_hook(self, scene: Scene) -> bool:
        text = scene.voiceover
        hook_keywords = ['为什么', '你知道吗', '原来', '竟然', '没想到',
                         '真相', '秘密', '误区', '方法', '技巧']
        has_keyword = any(kw in text for kw in hook_keywords)
        has_question = '?' in text or '？' in text
        has_number = bool(re.search(r'\d+', text))

        score = sum([has_keyword, has_question, has_number])
        return score >= 2

    def _check_duplicate(self, scenes: List[Scene]) -> bool:
        for i in range(len(scenes) - 1):
            similarity = SequenceMatcher(
                None,
                scenes[i].voiceover,
                scenes[i+1].voiceover
            ).ratio()
            if similarity > 0.7:
                return True
        return False

    def _check_structure(self, scenes: List[Scene]) -> bool:
        stages = [s.narrative_stage for s in scenes]
        required = ['opening', 'build', 'payoff', 'close']
        return all(stage in stages for stage in required)

    def _check_rhythm(self, scenes: List[Scene]) -> bool:
        energy_levels = [s.emotion_level for s in scenes]
        return not all(e == 3 for e in energy_levels) and any(e >= 4 for e in energy_levels)
```

**验证方式**:
```python
# 创建测试场景
scenes = [
    Scene(voiceover="为什么时间管理这么重要？", narrative_stage="opening", emotion_level=5),
    Scene(voiceover="首先要了解时间的本质", narrative_stage="build", emotion_level=3),
    Scene(voiceover="答案是使用番茄工作法", narrative_stage="payoff", emotion_level=4),
    Scene(voiceover="总结一下", narrative_stage="close", emotion_level=3)
]

validator = EnhancedValidator()
result = validator.validate_scenes(scenes)
print(f"验证通过: {result.passed}")  # 应该是True
```

---

## Step 4: 在LangGraph中集成新节点（Mock版）（Day 2 上午，3小时）

**做什么**: 在现有LangGraph流程中插入generate_hook和validate_scenes节点

**产出**:
```python
# /backend/app/graph/generation_graph.py (修改)

from app.services.hook_generate_service import HookGenerateService
from app.services.enhanced_validator import EnhancedValidator

# 新增节点函数
def generate_hook_node(state: dict) -> dict:
    """生成Hook节点"""
    hook_service = HookGenerateService()
    analysis = state["article_analysis"]
    hook_result = hook_service.generate_hooks(analysis)

    state["hook_result"] = hook_result
    state["selected_hook"] = hook_result.hooks[hook_result.selected_index]
    return state

def validate_scenes_node(state: dict) -> dict:
    """验证场景节点"""
    validator = EnhancedValidator()
    scenes = state["scenes"]
    validation_result = validator.validate_scenes(scenes)

    state["validation_result"] = validation_result
    state["validation_passed"] = validation_result.passed
    return state

# 更新图结构
graph = StateGraph(GenerationState)

# 添加节点
graph.add_node("parse_article", parse_article_node)
graph.add_node("generate_hook", generate_hook_node)  # 新增
graph.add_node("generate_scenes", generate_scenes_node)
graph.add_node("validate_scenes", validate_scenes_node)  # 新增
graph.add_node("generate_tts", generate_tts_node)

# 添加边
graph.add_edge("parse_article", "generate_hook")  # 新增
graph.add_edge("generate_hook", "generate_scenes")  # 新增
graph.add_edge("generate_scenes", "validate_scenes")  # 新增

# 添加条件边（重试逻辑）
def should_retry(state: dict) -> str:
    if not state["validation_passed"] and state.get("retry_count", 0) < 1:
        return "generate_scenes"  # 重试
    return "generate_tts"  # 继续

graph.add_conditional_edges(
    "validate_scenes",
    should_retry,
    {
        "generate_scenes": "generate_scenes",
        "generate_tts": "generate_tts"
    }
)

graph.add_edge("generate_tts", "generate_subtitles")
```

**验证方式**:
```python
# 运行一个端到端测试（仍然用Mock数据）
state = {
    "article_analysis": {"theme": "时间管理", "key_points": ["番茄工作法"]},
    "scenes": [...]  # Mock场景数据
}

result = graph.invoke(state)
print(result["selected_hook"].content)  # 应该输出Hook
print(result["validation_passed"])  # 应该是True或False
```

---

## Step 5: 增强SceneGenerateService（Mock版）（Day 2 下午，3小时）

**做什么**: 修改SceneGenerateService，让它接收Hook并生成带新字段的场景

**产出**:
```python
# /backend/app/services/scene_generate_service.py (修改)

class SceneGenerateService:
    def generate_scenes(self, analysis: dict, selected_hook: Hook) -> List[Scene]:
        """增强版：接收Hook，生成带新字段的场景"""

        # 先用Mock返回（不调用真实LLM）
        scenes = [
            Scene(
                goal="抛出问题，建立好奇",
                voiceover=selected_hook.content,  # 使用传入的Hook
                screen_text=selected_hook.content[:15] + "...",
                duration_sec=3,
                pace="fast",
                transition="cut",
                scene_role="hook",  # 新增
                narrative_stage="opening",  # 新增
                emotion_level=5,  # 新增
                hook_type=selected_hook.type,  # 新增
                quality_score=selected_hook.score  # 新增
            ),
            Scene(
                goal="展开问题",
                voiceover="首先要了解时间的本质",
                screen_text="时间的本质",
                duration_sec=4,
                pace="medium",
                transition="fade",
                scene_role="body",
                narrative_stage="build",
                emotion_level=3,
                hook_type=None,
                quality_score=None
            ),
            # ... 更多场景
        ]

        return scenes
```

**验证方式**:
```python
# 测试场景生成
service = SceneGenerateService()
hook = Hook(type="question", content="为什么时间管理这么重要？", score=0.85)
scenes = service.generate_scenes({"theme": "时间管理"}, hook)

print(scenes[0].voiceover)  # 应该是Hook的内容
print(scenes[0].scene_role)  # 应该是"hook"
print(scenes[0].narrative_stage)  # 应该是"opening"
```

---

## Step 6: 端到端测试（Mock版完整链路）（Day 2 下午，2小时）

**做什么**: 跑通整个流程，确保所有节点能串起来

**产出**:
```python
# /backend/tests/test_e2e_mock.py (新建)

def test_full_pipeline_mock():
    """端到端测试：从文章输入到场景输出"""

    # 输入
    article = "如何提高工作效率？时间管理是关键..."

    # 执行流程
    state = {
        "article_content": article,
        "retry_count": 0
    }

    result = graph.invoke(state)

    # 验证
    assert "selected_hook" in result
    assert result["selected_hook"].type in ["question", "reveal", "contrast"]

    assert "scenes" in result
    assert len(result["scenes"]) >= 4

    assert result["scenes"][0].scene_role == "hook"
    assert result["scenes"][0].voiceover == result["selected_hook"].content

    assert "validation_passed" in result

    print("✅ Mock版端到端测试通过")
```

**验证方式**:
```bash
pytest tests/test_e2e_mock.py -v
```

---

## Step 7: 数据库迁移（Day 3 上午，2小时）

**做什么**: 在数据库中添加5个新字段

**产出**:
```python
# /backend/alembic/versions/xxx_add_scene_v3_fields.py (新建)

def upgrade():
    op.add_column('scenes',
        sa.Column('scene_role', sa.String(20), nullable=False, server_default='body')
    )
    op.add_column('scenes',
        sa.Column('narrative_stage', sa.String(20), nullable=False, server_default='build')
    )
    op.add_column('scenes',
        sa.Column('emotion_level', sa.Integer(), nullable=False, server_default='3')
    )
    op.add_column('scenes',
        sa.Column('hook_type', sa.String(20), nullable=True)
    )
    op.add_column('scenes',
        sa.Column('quality_score', sa.Float(), nullable=True)
    )

def downgrade():
    op.drop_column('scenes', 'quality_score')
    op.drop_column('scenes', 'hook_type')
    op.drop_column('scenes', 'emotion_level')
    op.drop_column('scenes', 'narrative_stage')
    op.drop_column('scenes', 'scene_role')
```

**验证方式**:
```bash
# 在测试环境执行迁移
alembic upgrade head

# 检查表结构
psql -d test_db -c "\d scenes"

# 应该看到5个新字段
```

---

## Step 8: 更新Scene模型（Day 3 上午，1小时）

**做什么**: 在ORM模型中添加新字段

**产出**:
```python
# /backend/app/models/scene.py (修改)

class Scene(Base):
    __tablename__ = "scenes"

    # ... 原有字段 ...

    # 新增字段
    scene_role = Column(String(20), nullable=False, default='body')
    narrative_stage = Column(String(20), nullable=False, default='build')
    emotion_level = Column(Integer, nullable=False, default=3)
    hook_type = Column(String(20), nullable=True)
    quality_score = Column(Float, nullable=True)
```

**验证方式**:
```python
# 测试创建和保存
scene = Scene(
    voiceover="测试",
    scene_role="hook",
    narrative_stage="opening",
    emotion_level=5
)
db.add(scene)
db.commit()

# 查询验证
saved_scene = db.query(Scene).filter_by(voiceover="测试").first()
assert saved_scene.scene_role == "hook"
print("✅ 数据库字段验证通过")
```

---

## Step 9: 替换真实LLM - HookGenerateService（Day 3 下午，3小时）

**做什么**: 将Mock版本替换为真实LLM调用

**产出**:
```python
# /backend/app/services/hook_generate_service.py (修改)

class HookGenerateService:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_hooks(self, analysis: dict) -> HookResult:
        """真实版本：调用LLM生成Hook"""
        prompt = self._build_prompt(analysis)

        try:
            response = self.llm.invoke(prompt, timeout=30)
            hooks = self._parse_response(response)
            selected_index = self._select_best(hooks)
            return HookResult(hooks=hooks, selected_index=selected_index)
        except Exception as e:
            logger.error(f"Hook生成失败: {e}")
            return self._get_default_hook(analysis)

    def _build_prompt(self, analysis: dict) -> str:
        theme = analysis.get("theme", "")
        key_points = analysis.get("key_points", [])
        audience = analysis.get("target_audience", "")

        return f"""
你是短视频Hook专家。基于以下信息，生成3个不同类型的开场Hook。

主题: {theme}
关键点: {', '.join(key_points)}
目标受众: {audience}

要求：
1. 生成3个Hook，类型分别为：question（疑问）、contrast（对比）、reveal（揭秘）
2. 每个Hook必须在3秒内制造好奇缺口
3. 不能夸大或偏离主题
4. 每个Hook给出质量评分（0.0-1.0）

输出JSON格式：
{{
  "hooks": [
    {{"type": "question", "content": "为什么...", "score": 0.85}},
    {{"type": "contrast", "content": "你以为...其实...", "score": 0.78}},
    {{"type": "reveal", "content": "90%的人不知道...", "score": 0.72}}
  ]
}}
"""

    def _parse_response(self, response: str) -> List[Hook]:
        """解析LLM响应"""
        try:
            data = json.loads(response)
            return [Hook(**h) for h in data["hooks"]]
        except Exception as e:
            logger.error(f"解析Hook失败: {e}")
            # 尝试修复JSON
            fixed = self._fix_json(response)
            data = json.loads(fixed)
            return [Hook(**h) for h in data["hooks"]]

    def _select_best(self, hooks: List[Hook]) -> int:
        """选择最优Hook"""
        # 优先选question类型
        for i, hook in enumerate(hooks):
            if hook.type == "question":
                return i
        # 其次选contrast
        for i, hook in enumerate(hooks):
            if hook.type == "contrast":
                return i
        return 0

    def _get_default_hook(self, analysis: dict) -> HookResult:
        """默认Hook（兜底）"""
        theme = analysis.get("theme", "这个话题")
        hook = Hook(
            type="reveal",
            content=f"接下来我要分享{theme}的关键方法",
            score=0.5
        )
        return HookResult(hooks=[hook], selected_index=0)
```

**验证方式**:
```python
# 测试真实LLM调用
service = HookGenerateService(llm_client)
result = service.generate_hooks({"theme": "时间管理", "key_points": ["番茄工作法"]})

print(result.hooks[0].content)  # 应该是LLM生成的内容
assert len(result.hooks) == 3
assert result.hooks[0].type in ["question", "reveal", "contrast"]
```

---

## Step 10: 替换真实LLM - SceneGenerateService（Day 4 上午，4小时）

**做什么**: 增强Prompt，让LLM生成带新字段的场景

**产出**:
```python
# /backend/app/services/scene_generate_service.py (修改)

class SceneGenerateService:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_scenes(self, analysis: dict, selected_hook: Hook) -> List[Scene]:
        """真实版本：调用LLM生成场景"""
        prompt = self._build_enhanced_prompt(analysis, selected_hook)

        try:
            response = self.llm.invoke(prompt, timeout=30)
            scenes = self._parse_response(response, selected_hook)
            return scenes
        except Exception as e:
            logger.error(f"场景生成失败: {e}")
            raise

    def _build_enhanced_prompt(self, analysis: dict, selected_hook: Hook) -> str:
        theme = analysis.get("theme", "")
        key_points = analysis.get("key_points", [])

        return f"""
你是短视频脚本专家。基于文章分析和Hook，生成6-10个场景。

主题: {theme}
关键点: {', '.join(key_points)}
Hook: {selected_hook.content} (类型: {selected_hook.type})

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
4. 禁止：场景间内容重复、平铺直叙无起伏

【输出格式】
每个场景必须包含：
- goal: 场景目标
- voiceover: 旁白文本
- screen_text: 屏幕文字
- duration_sec: 时长（秒）
- pace: 节奏（slow/medium/fast）
- transition: 转场（cut/fade/slide）
- scene_role: hook | body | close
- narrative_stage: opening | build | payoff | close
- emotion_level: 1-5

输出JSON格式：
{{
  "scenes": [
    {{
      "goal": "抛出问题，建立好奇",
      "voiceover": "{selected_hook.content}",
      "screen_text": "...",
      "duration_sec": 3,
      "pace": "fast",
      "transition": "cut",
      "scene_role": "hook",
      "narrative_stage": "opening",
      "emotion_level": 5
    }},
    ...
  ]
}}
"""

    def _parse_response(self, response: str, selected_hook: Hook) -> List[Scene]:
        """解析LLM响应"""
        try:
            data = json.loads(response)
            scenes = []
            for i, s in enumerate(data["scenes"]):
                scene = Scene(
                    goal=s.get("goal", ""),
                    voiceover=s.get("voiceover", ""),
                    screen_text=s.get("screen_text", ""),
                    duration_sec=s.get("duration_sec", 3),
                    pace=s.get("pace", "medium"),
                    transition=s.get("transition", "cut"),
                    scene_role=s.get("scene_role", "body"),
                    narrative_stage=s.get("narrative_stage", "build"),
                    emotion_level=s.get("emotion_level", 3),
                    hook_type=selected_hook.type if i == 0 else None,
                    quality_score=selected_hook.score if i == 0 else None
                )
                scenes.append(scene)
            return scenes
        except Exception as e:
            logger.error(f"解析场景失败: {e}")
            # 尝试修复JSON
            fixed = self._fix_json(response)
            return self._parse_response(fixed, selected_hook)
```

**验证方式**:
```python
# 测试真实LLM调用
service = SceneGenerateService(llm_client)
hook = Hook(type="question", content="为什么时间管理这么重要？", score=0.85)
scenes = service.generate_scenes({"theme": "时间管理"}, hook)

print(f"生成了{len(scenes)}个场景")
print(scenes[0].voiceover)  # 应该是Hook的内容
print(scenes[0].scene_role)  # 应该是"hook"
print(scenes[0].narrative_stage)  # 应该是"opening"
```

---

## Step 11: 添加重试逻辑（Day 4 下午，2小时）

**做什么**: 在验证失败时重新生成场景

**产出**:
```python
# /backend/app/graph/generation_graph.py (修改)

def generate_scenes_node(state: dict) -> dict:
    """生成场景节点（带重试逻辑）"""
    service = SceneGenerateService(llm_client)
    analysis = state["article_analysis"]
    selected_hook = state["selected_hook"]

    # 如果是重试，带上错误反馈
    feedback = None
    if state.get("retry_count", 0) > 0:
        errors = state.get("validation_result", {}).get("errors", [])
        feedback = f"上次生成的场景存在以下问题：{', '.join(errors)}，请修正"

    scenes = service.generate_scenes(analysis, selected_hook, feedback)
    state["scenes"] = scenes
    return state

def validate_scenes_node(state: dict) -> dict:
    """验证场景节点（带降级逻辑）"""
    validator = EnhancedValidator()
    scenes = state["scenes"]
    retry_count = state.get("retry_count", 0)

    validation_result = validator.validate_scenes(scenes)

    # 如果重试次数>=1，降低标准强制通过
    if not validation_result.passed and retry_count >= 1:
        logger.warning(f"验证不通过（重试{retry_count}次），降低标准强制通过")
        validation_result.passed = True
        validation_result.forced = True

    state["validation_result"] = validation_result
    state["validation_passed"] = validation_result.passed

    # 如果不通过，增加重试计数
    if not validation_result.passed:
        state["retry_count"] = retry_count + 1

    return state
```

**验证方式**:
```python
# 测试重试逻辑
state = {
    "article_analysis": {"theme": "时间管理"},
    "selected_hook": hook,
    "retry_count": 0
}

# 第一次生成
state = generate_scenes_node(state)
state = validate_scenes_node(state)

if not state["validation_passed"]:
    print("第一次验证失败，开始重试")
    state = generate_scenes_node(state)  # 重试
    state = validate_scenes_node(state)  # 再次验证

print(f"最终验证结果: {state['validation_passed']}")
```

---

## Step 12: 端到端测试（真实LLM版）（Day 4 下午，2小时）

**做什么**: 用真实LLM跑通整个流程

**产出**:
```python
# /backend/tests/test_e2e_real.py (新建)

def test_full_pipeline_real():
    """端到端测试：真实LLM调用"""

    # 输入真实文章
    article = """
如何提高工作效率？

时间管理是关键。很多人每天忙到飞起，却总觉得没做什么。
问题在于没有掌握正确的方法。

番茄工作法是一个简单有效的技巧...
"""

    # 执行流程
    state = {
        "article_content": article,
        "retry_count": 0
    }

    result = graph.invoke(state)

    # 验证
    assert "selected_hook" in result
    assert result["selected_hook"].type in ["question", "reveal", "contrast"]
    print(f"生成的Hook: {result['selected_hook'].content}")

    assert "scenes" in result
    assert len(result["scenes"]) >= 4
    print(f"生成了{len(result['scenes'])}个场景")

    assert result["scenes"][0].scene_role == "hook"
    assert result["scenes"][0].voiceover == result["selected_hook"].content

    assert "validation_passed" in result
    print(f"验证通过: {result['validation_passed']}")

    # 检查叙事结构
    stages = [s.narrative_stage for s in result["scenes"]]
    assert "opening" in stages
    assert "build" in stages
    assert "payoff" in stages
    assert "close" in stages

    print("✅ 真实LLM端到端测试通过")
```

**验证方式**:
```bash
pytest tests/test_e2e_real.py -v -s
```

---

## Step 13: 添加异常处理和日志（Day 5 上午，3小时）

**做什么**: 完善错误处理、重试机制、日志记录

**产出**:
```python
# /backend/app/services/hook_generate_service.py (增强)

class HookGenerateService:
    def generate_hooks_with_retry(self, analysis: dict, max_retries: int = 3) -> HookResult:
        """带重试的Hook生成"""
        for attempt in range(max_retries):
            try:
                logger.info(f"开始生成Hook (尝试 {attempt+1}/{max_retries})")
                result = self.generate_hooks(analysis)
                logger.info(f"Hook生成成功: {result.hooks[result.selected_index].content}")
                return result
            except Exception as e:
                logger.warning(f"Hook生成失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒后重试
                else:
                    logger.error("Hook生成失败，使用默认Hook")
                    return self._get_default_hook(analysis)

    def _fix_json(self, text: str) -> str:
        """修复常见的JSON格式错误"""
        # 去除多余逗号
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        # 去除注释
        text = re.sub(r'//.*?\n', '\n', text)
        return text
```

**验证方式**:
```python
# 测试异常处理
service = HookGenerateService(llm_client)

# 模拟LLM失败
with patch.object(service.llm, 'invoke', side_effect=Exception("LLM超时")):
    result = service.generate_hooks_with_retry({"theme": "测试"})
    assert result.hooks[0].content == "接下来我要分享测试的关键方法"  # 默认Hook
```

---

## Step 14: Prompt调优（Day 5 下午，3小时）

**做什么**: 用真实文章测试，调整Prompt

**产出**:
```python
# 准备10个真实文章样本
test_articles = [
    "如何提高工作效率...",
    "Python编程技巧...",
    "健康饮食指南...",
    # ... 更多
]

# 批量测试
results = []
for article in test_articles:
    result = graph.invoke({"article_content": article})
    results.append({
        "hook": result["selected_hook"].content,
        "hook_type": result["selected_hook"].type,
        "scenes_count": len(result["scenes"]),
        "validation_passed": result["validation_passed"]
    })

# 分析结果
print(f"Hook生成成功率: {sum(1 for r in results if r['hook']) / len(results) * 100}%")
print(f"验证通过率: {sum(1 for r in results if r['validation_passed']) / len(results) * 100}%")
```

**调优方向**:
1. 如果Hook质量不高 → 增加Few-shot示例
2. 如果验证通过率低 → 放宽验证阈值
3. 如果结构不完整 → 强化Prompt约束

---

## Step 15: 单元测试（Day 6 上午，3小时）

**做什么**: 为核心服务编写单元测试

**产出**:
```python
# /backend/tests/test_hook_service.py

def test_hook_generation():
    """测试Hook生成"""
    service = HookGenerateService(mock_llm)
    result = service.generate_hooks({"theme": "时间管理"})

    assert len(result.hooks) == 3
    assert result.selected_index >= 0

def test_hook_selection():
    """测试Hook选择逻辑"""
    hooks = [
        Hook(type="reveal", content="...", score=0.9),
        Hook(type="question", content="...", score=0.8)
    ]
    service = HookGenerateService(mock_llm)
    selected = service._select_best(hooks)

    assert selected == 1  # 应该选question类型

def test_validator():
    """测试验证器"""
    validator = EnhancedValidator()

    scenes = [
        Scene(voiceover="为什么时间管理这么重要？", narrative_stage="opening", emotion_level=5),
        Scene(voiceover="首先要了解时间的本质", narrative_stage="build", emotion_level=3),
        Scene(voiceover="答案是使用番茄工作法", narrative_stage="payoff", emotion_level=4),
        Scene(voiceover="总结一下", narrative_stage="close", emotion_level=3)
    ]

    result = validator.validate_scenes(scenes)
    assert result.passed == True
```

**验证方式**:
```bash
pytest tests/ -v --cov=app/services
```

---

## Step 16: 生产环境准备（Day 6 下午，2小时）

**做什么**: 准备上线检查清单和回滚方案

**产出**:
```bash
# /backend/scripts/deploy_v3.sh (新建)

#!/bin/bash
set -e

echo "=== AI短视频生成系统 v3 部署脚本 ==="

# 1. 备份数据库
echo "1. 备份数据库..."
pg_dump -U postgres -d prod_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 执行数据库迁移
echo "2. 执行数据库迁移..."
alembic upgrade head

# 3. 检查迁移结果
echo "3. 检查迁移结果..."
psql -U postgres -d prod_db -c "\d scenes" | grep -E "scene_role|narrative_stage|emotion_level|hook_type|quality_score"

# 4. 运行测试
echo "4. 运行测试..."
pytest tests/test_e2e_real.py -v

# 5. 重启服务
echo "5. 重启服务..."
systemctl restart video-generation-service

echo "✅ 部署完成"
```

```bash
# /backend/scripts/rollback_v3.sh (新建)

#!/bin/bash
set -e

echo "=== AI短视频生成系统 v3 回滚脚本 ==="

# 1. 回滚数据库
echo "1. 回滚数据库迁移..."
alembic downgrade -1

# 2. 恢复代码
echo "2. 恢复代码到v2版本..."
git checkout v2.0

# 3. 重启服务
echo "3. 重启服务..."
systemctl restart video-generation-service

echo "✅ 回滚完成"
```

**上线检查清单**:
```markdown
## 上线前检查

### 代码检查
- [ ] 所有单元测试通过
- [ ] 端到端测试通过（至少10个真实文章）
- [ ] 代码Review完成
- [ ] 无明显性能问题

### 数据库检查
- [ ] 迁移脚本在测试环境验证
- [ ] 生产环境数据库已备份
- [ ] 回滚脚本已准备并测试

### 监控检查
- [ ] 日志记录完整（耗时、成功率）
- [ ] 错误告警配置完成
- [ ] 性能指标监控配置完成

### 回滚准备
- [ ] 回滚脚本已测试
- [ ] 回滚流程已文档化
- [ ] 团队成员知晓回滚步骤
```

---

## Step 17: 灰度发布（Day 7，全天）

**做什么**: 逐步放量，监控指标

**产出**:
```python
# /backend/app/config.py (新增)

class Config:
    # v3功能开关
    V3_ENABLED = os.getenv("V3_ENABLED", "false").lower() == "true"
    V3_TRAFFIC_PERCENTAGE = int(os.getenv("V3_TRAFFIC_PERCENTAGE", "0"))

# /backend/app/graph/generation_graph.py (修改)

def should_use_v3(user_id: str) -> bool:
    """判断是否使用v3版本"""
    if not Config.V3_ENABLED:
        return False

    # 基于user_id的哈希值决定是否使用v3
    hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    return (hash_value % 100) < Config.V3_TRAFFIC_PERCENTAGE

def generate_video(user_id: str, article: str):
    """生成视频（支持灰度）"""
    if should_use_v3(user_id):
        logger.info(f"用户{user_id}使用v3版本")
        return generate_video_v3(article)
    else:
        logger.info(f"用户{user_id}使用v2版本")
        return generate_video_v2(article)
```

**灰度计划**:
```
Day 7 上午: 10%流量
- 监控指标：生成成功率、Hook质量、验证通过率
- 如果正常，继续

Day 7 下午: 50%流量
- 持续监控
- 收集用户反馈

Day 7 晚上: 100%流量
- 全量上线
- 关闭v2代码
```

**监控指标**:
```python
# 关键指标
metrics = {
    "hook_generation_success_rate": 0.98,  # 目标 ≥ 98%
    "validation_pass_rate": 0.85,          # 目标 ≥ 85%
    "generation_success_rate": 0.95,       # 目标 ≥ 95%
    "avg_generation_time": 70,             # 目标 ≤ 70秒
}
```

---

# 2. 数据结构定义（核心）

## Hook数据结构
```python
class Hook(BaseModel):
    type: str  # question | reveal | contrast
    content: str  # Hook文本
    score: float  # 0.0-1.0

class HookResult(BaseModel):
    hooks: List[Hook]  # 3个Hook
    selected_index: int  # 选中的索引
```

## Scene数据结构（新增字段）
```python
class Scene(Base):
    # 原有字段
    goal: str
    voiceover: str
    screen_text: str
    duration_sec: int
    pace: str
    transition: str

    # 新增字段
    scene_role: str  # hook | body | close
    narrative_stage: str  # opening | build | payoff | close
    emotion_level: int  # 1-5
    hook_type: Optional[str]  # question | reveal | contrast (仅第1个场景)
    quality_score: Optional[float]  # 0.0-1.0
```

## ValidationResult数据结构
```python
class ValidationResult:
    passed: bool  # 是否通过
    errors: List[str]  # 错误列表
    forced: bool  # 是否强制通过
```

---

# 3. 接口开发顺序

## 第一个接口（核心入口）
```
POST /api/v3/generate
- 输入: article_content
- 输出: video_url + scenes + hook
```

## 后续接口顺序
1. `POST /api/v3/generate-hook` - 单独生成Hook（调试用）
2. `POST /api/v3/validate-scenes` - 单独验证场景（调试用）
3. `GET /api/v3/metrics` - 获取质量指标（监控用）

---

# 4. AI集成步骤

## 阶段1: Mock（Day 1-2）
- HookGenerateService返回固定Hook
- SceneGenerateService返回固定场景
- 目的：验证流程能跑通

## 阶段2: 替换真实LLM（Day 3-4）
- HookGenerateService调用真实LLM
- SceneGenerateService调用真实LLM
- 目的：验证Prompt和解析逻辑

## 阶段3: 异常处理（Day 5）
- 添加重试逻辑
- 添加默认兜底
- 添加JSON修复
- 目的：提高稳定性

## 失败处理策略
```
LLM调用失败 → 重试3次 → 使用默认Hook
JSON解析失败 → 修复JSON → 仍失败则使用默认值
验证不通过 → 重试1次 → 降低标准强制通过
```

---

# 5. 延后事项（刻意不做）

## 当前不实现的功能

### 1. 并行优化
**原因**: 先验证效果，再优化性能
**何时做**: v3.1，如果生成时长超过70秒

### 2. AI Critic（LLM评估LLM）
**原因**: 不可靠，且增加5-30秒延迟
**替代**: 使用规则检查

### 3. Story Director服务
**原因**: 与SceneGenerator功能重复
**替代**: 在Prompt中加入叙事约束

### 4. 12个字段中的7个
**原因**: 当前用不到，增加LLM输出难度
**何时做**: 等需要时再加

### 5. 视觉层升级
**原因**: 本次聚焦内容层
**何时做**: v3.2

### 6. 灰度发布机制
**原因**: 可以手动控制流量
**何时做**: 如果需要长期A/B测试

---

# 6. 开发时间表

| 阶段 | 时间 | 任务 | 产出 |
|------|------|------|------|
| Day 1 上午 | 2h | 定义数据结构 | Hook/Scene Schema |
| Day 1 下午 | 5h | 实现Mock服务 | HookService + Validator |
| Day 2 上午 | 3h | 集成LangGraph | 新增2个节点 |
| Day 2 下午 | 5h | 增强SceneService + 端到端测试 | Mock版完整链路 |
| Day 3 上午 | 3h | 数据库迁移 | 5个新字段 |
| Day 3 下午 | 3h | 替换真实LLM - Hook | 真实Hook生成 |
| Day 4 上午 | 4h | 替换真实LLM - Scene | 真实场景生成 |
| Day 4 下午 | 4h | 添加重试逻辑 + 端到端测试 | 真实LLM完整链路 |
| Day 5 上午 | 3h | 异常处理和日志 | 稳定性提升 |
| Day 5 下午 | 3h | Prompt调优 | 质量提升 |
| Day 6 上午 | 3h | 单元测试 | 测试覆盖率≥80% |
| Day 6 下午 | 2h | 生产环境准备 | 部署脚本 + 检查清单 |
| Day 7 | 8h | 灰度发布 | 10% → 50% → 100% |

**总计**: 7个工作日

---

# 7. 成功标准

## 技术指标（必须达到）
- ✅ 生成成功率 ≥ 95%（含重试）
- ✅ 平均生成时长 ≤ 70秒
- ✅ Hook生成成功率 ≥ 98%
- ✅ Validator首次通过率 ≥ 85%

## 质量指标（必须达到）
- ✅ Hook优秀率 ≥ 65%（人工评估100个样本）
- ✅ 内容重复率 < 10%（自动检测）
- ✅ 结构完整率 ≥ 95%（自动检测）

## 如果达不到
- 执行风险降级方案（见Tech Spec第8章）
- 考虑回滚到v2

---

# 8. 关键文件清单

## 新增文件
```
/backend/app/schemas/hook.py
/backend/app/services/hook_generate_service.py
/backend/app/services/enhanced_validator.py
/backend/alembic/versions/xxx_add_scene_v3_fields.py
/backend/tests/test_e2e_mock.py
/backend/tests/test_e2e_real.py
/backend/tests/test_hook_service.py
/backend/tests/test_validator.py
/backend/scripts/deploy_v3.sh
/backend/scripts/rollback_v3.sh
```

## 修改文件
```
/backend/app/models/scene.py
/backend/app/services/scene_generate_service.py
/backend/app/graph/generation_graph.py
/backend/app/config.py
```

---

**文档状态**: 已完成
**下一步**: 开始执行Step 1
**预计完成**: 7个工作日