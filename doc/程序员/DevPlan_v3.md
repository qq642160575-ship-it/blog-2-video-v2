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

## Step 3: 实现EnhancedValidator（Mock版）（Day 1 下午，2小时）

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

## Step 5: 增强SceneGenerateService的Prompt（Day 2 下午，3小时）

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

// __CONTINUE_HERE__