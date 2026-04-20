# AI短视频生成系统 PRD v3（最终冻结版）

**文档版本**: v3.0-FINAL
**创建日期**: 2026-04-20
**文档状态**: 已冻结，可进入开发
**决策人**: 高级产品经理

---

## 0. 决策说明（必读）

本PRD经过产品、技术、程序员三方评审，最终决策如下：

### 决策结果

**采用方案**: 程序员折中方案（v3-pragmatic）

**理由**:
1. 产品方案过度工程化，风险高（成功率<50%，成本+150%）
2. 技术方案过于保守，效果可能不足（Hook质量提升仅50%）
3. 程序员方案平衡了成本与效果（成本+30%，效果提升60-70%）

### 被砍掉的功能

❌ **Story Director服务** - 用Prompt约束替代
❌ **Scene Critic服务** - 用规则检查替代
❌ **12个新字段中的7个** - 只保留5个核心字段

### 保留的功能

✅ **Hook Generator服务** - Hook太重要，值得独立服务
✅ **增强的Validator** - 规则检查+简单NLP
✅ **5个核心字段** - 最小化Schema扩展

---

## 1. 项目背景

### 1.1 解决什么问题

当前系统生成的视频开头不够吸引人，导致：
- 前3秒流失率高（用户直接划走）
- 内容平铺直叙，缺少节奏
- 用户需要大量手动修改

### 1.2 为什么现在做

系统已完成MVP验证，技术架构稳定。现在是提升内容质量的最佳时机。

---

## 2. 用户场景

### 2.1 目标用户

知识博主、自媒体作者，需要把文章转成短视频。

### 2.2 关键使用路径

**路径1**: 上传文章 → 一键生成 → 直接发布（无需修改）
- 当前：70%用户需要修改开头
- 目标：修改率降低到30%

---

## 3. MVP范围

### 3.1 本版本包含（P0功能）

**功能1: Hook自动生成**
- 生成3个Hook方案（question/reveal/contrast）
- 自动选择最优方案
- 作为第1个场景的开场

**功能2: 增强的内容验证**
- Hook关键词检查
- 内容重复度检查
- 结构完整性检查
- 节奏平衡检查

**功能3: 最小化Schema扩展**
- 新增5个字段：scene_role, narrative_stage, emotion_level, hook_type, quality_score
- 支持结构化分析和质量追踪

### 3.2 本版本不包含

❌ **Story Director** - 原因：与SceneGenerator功能重复，用Prompt约束替代
❌ **AI Critic** - 原因：AI评估AI不可靠，用规则检查替代
❌ **7个额外字段** - 原因：当前用不到，等需要时再加
❌ **视觉层升级** - 原因：本次聚焦内容层
❌ **并行优化** - 原因：先验证效果，再优化性能

---

## 4. 功能定义

### 4.1 Hook Generator（核心功能）

**输入**:
```json
{
  "theme": "如何提高工作效率",
  "key_points": ["时间管理", "工具使用"],
  "target_audience": "职场人士",
  "tone": "实用"
}
```

**输出**:
```json
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
  "selected_index": 0
}
```

**行为规则**:
1. 必须生成3个不同类型的Hook
2. 每个Hook必须在3秒内制造好奇缺口
3. 不能夸大或偏离文章事实
4. 优先选择question类型（完播率最高）

---

### 4.2 Enhanced Validator（增强验证）

**检查项1: Hook验证**
```python
# 规则
hook_keywords = ['为什么', '你知道吗', '原来', '竟然', '没想到',
                 '真相', '秘密', '误区', '方法', '技巧']
has_keyword = any(kw in text for kw in hook_keywords)
has_question = '?' in text or '？' in text
has_number = bool(re.search(r'\d+', text))

# 满足任意2个条件即通过
score = sum([has_keyword, has_question, has_number])
passed = score >= 2
```

**检查项2: 重复度检查**
```python
# 相邻场景相似度不能超过70%
for i in range(len(scenes) - 1):
    similarity = SequenceMatcher(None, scenes[i].voiceover,
                                 scenes[i+1].voiceover).ratio()
    if similarity > 0.7:
        return False
```

**检查项3: 结构完整性**
```python
# 必须包含opening/build/payoff/close
stages = [s.narrative_stage for s in scenes]
required = ['opening', 'build', 'payoff', 'close']
passed = all(stage in stages for stage in required)
```

**检查项4: 节奏检查**
```python
# 不能全是3（平淡），必须有至少1个高峰（≥4）
energy_levels = [s.emotion_level for s in scenes]
passed = not all(e == 3 for e in energy_levels) and any(e >= 4 for e in energy_levels)
```

---

### 4.3 Scene Schema扩展

**新增字段（5个）**:

```python
# 场景角色
scene_role = Column(String(20), nullable=False, default='body')
# 枚举: hook | body | close

# 叙事阶段
narrative_stage = Column(String(20), nullable=False, default='build')
# 枚举: opening | build | payoff | close

# 情绪等级
emotion_level = Column(Integer, nullable=False, default=3)
# 范围: 1-5

# Hook类型（仅第1个场景）
hook_type = Column(String(20), nullable=True)
# 枚举: question | reveal | contrast | countdown

# 质量分数（由Validator计算）
quality_score = Column(Float, nullable=True)
# 范围: 0.0-1.0
```

**为什么只要这5个**:
- `scene_role`: 用于结构检查
- `narrative_stage`: 比scene_role更细，支持叙事分析
- `emotion_level`: 用于节奏检查
- `hook_type`: 记录Hook类型，方便分析
- `quality_score`: 质量追踪

---

## 5. 用户流程

### 5.1 生成流程（8步）

```
1. 用户上传文章
   ↓
2. 系统分析文章（parse_article）
   ↓
3. 生成3个Hook方案（generate_hook）← 新增，+8秒
   ↓
4. 生成6-10个场景（generate_scenes）← Prompt增强
   ↓
5. 验证场景质量（validate_scenes）← 新增4项检查
   ↓ 不通过？重试1次
   ↓ 还不通过？降低标准，强制通过
   ↓
6. 生成语音（generate_tts）
   ↓
7. 生成字幕（generate_subtitles）
   ↓
8. 准备渲染（prepare_render）
```

### 5.2 错误处理

**场景1: Hook生成失败**
- 重试3次
- 仍失败：使用默认Hook（"接下来我要分享..."）

**场景2: 验证不通过**
- 第1次不通过：重新生成场景（带反馈）
- 第2次不通过：降低标准到0.6，强制通过

**场景3: LLM输出格式错误**
- 尝试修复JSON（去除多余逗号）
- 仍失败：使用默认值填充缺失字段

---

## 6. 关键决策说明

### 6.1 技术妥协

**妥协1: 不做Story Director**
- 原因：与SceneGenerator功能重复，增加复杂度
- 替代：在SceneGenerator的Prompt中加入叙事结构约束
- 节省：12秒延迟，1个服务，~500行代码

**妥协2: 不做AI Critic**
- 原因：AI评估AI不可靠，重试导致延迟爆炸
- 替代：规则检查+简单NLP
- 节省：5-30秒延迟，1个服务，~400行代码

**妥协3: 只加5个字段**
- 原因：12个字段LLM输出不稳定，大部分当前用不到
- 替代：需要时再加
- 节省：降低LLM输出难度，提高成功率

### 6.2 产品坚持

**坚持1: 必须有独立的Hook Generator**
- 理由：Hook是最重要的（前3秒决定完播率）
- 成本：+8秒延迟，+1次LLM调用
- 收益：Hook质量提升60-70%，值得投入

**坚持2: 必须有增强的Validator**
- 理由：当前系统没有质量检查，低质量内容直接渲染
- 成本：+2秒延迟，~200行代码
- 收益：能检测80%的质量问题，避免浪费渲染资源

---

## 7. 风险与边界

### 7.1 已知风险

**风险1: Hook生成可能不够多样**
- 应对：Prompt中加入多样性约束，定期调优

**风险2: 规则检查可能误杀**
- 应对：阈值可配置，初期设宽松（2个条件即可）

**风险3: 生成时长增加15秒**
- 应对：用户可接受（从55秒到70秒），后续可优化

### 7.2 明确不处理的情况

**边界1: 非中文内容**
- 当前只支持中文，英文等其他语言留待v3.1

**边界2: 超长文章（>5000字）**
- 当前不处理，建议用户拆分

**边界3: 专业术语过多的文章**
- Hook可能不够通俗，需要用户手动修改

---

## 8. 技术实现

### 8.1 核心改动点

**改动1: 新增HookGenerateService**
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
```

**改动2: 增强SceneGenerator的Prompt**
```python
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
4. 禁止：场景间内容重复、平铺直叙无起伏

【输出格式】
每个场景必须包含：
- goal, voiceover, screen_text, duration_sec, pace, transition
- scene_role: hook | body | close
- narrative_stage: opening | build | payoff | close
- emotion_level: 1-5
- hook_type: question | reveal | contrast | countdown（仅第1个场景）
"""
```

**改动3: 增强Validator**
```python
# /backend/app/services/validator.py

class EnhancedValidator:
    def validate_scenes(self, scenes: List[Scene]) -> ValidationResult:
        errors = []

        if not self._validate_hook(scenes[0]):
            errors.append("第1个场景缺少有效Hook")

        if self._check_duplicate(scenes):
            errors.append("场景间内容重复")

        if not self._check_structure(scenes):
            errors.append("缺少必要的叙事阶段")

        if not self._check_rhythm(scenes):
            errors.append("节奏过于平淡")

        return ValidationResult(passed=(len(errors) == 0), errors=errors)
```

### 8.2 数据库迁移

```sql
-- /backend/alembic/versions/xxx_add_scene_v3_fields.py

ALTER TABLE scenes ADD COLUMN scene_role VARCHAR(20) NOT NULL DEFAULT 'body';
ALTER TABLE scenes ADD COLUMN narrative_stage VARCHAR(20) NOT NULL DEFAULT 'build';
ALTER TABLE scenes ADD COLUMN emotion_level INT NOT NULL DEFAULT 3;
ALTER TABLE scenes ADD COLUMN hook_type VARCHAR(20) NULL;
ALTER TABLE scenes ADD COLUMN quality_score FLOAT NULL;
```

### 8.3 LangGraph流程

```python
# 新增节点
graph.add_node("generate_hook", generate_hook_node)

# 更新节点
graph.add_node("generate_scenes", generate_scenes_node)  # Prompt增强
graph.add_node("validate_scenes", validate_scenes_node)  # 新增4项检查

# 流程
graph.add_edge("parse_article", "generate_hook")
graph.add_edge("generate_hook", "generate_scenes")
graph.add_edge("generate_scenes", "validate_scenes")
graph.add_conditional_edges(
    "validate_scenes",
    lambda state: "generate_scenes" if not state["validation_passed"]
                  and state.get("retry_count", 0) < 1
                  else "generate_tts"
)
```

---

## 9. 开发计划

### 9.1 任务拆解（8天）

**Day 1-2: 数据层**
- [ ] 创建数据库迁移脚本（5个字段）
- [ ] 更新Scene模型定义
- [ ] 在测试环境执行迁移

**Day 3-4: 服务层**
- [ ] 实现HookGenerateService
- [ ] 增强SceneGenerateService（Prompt）
- [ ] 增强Validator（4项检查）
- [ ] 编写单元测试

**Day 5-6: 流程层**
- [ ] 新增generate_hook节点
- [ ] 更新generate_scenes节点
- [ ] 更新validate_scenes节点
- [ ] 实现重试逻辑
- [ ] 编写集成测试

**Day 7: 测试与调优**
- [ ] 端到端测试
- [ ] Prompt调优
- [ ] Validator阈值调整

**Day 8: 上线准备**
- [ ] 在测试环境验证
- [ ] 准备回滚方案
- [ ] 生产环境迁移

### 9.2 成本预估

**开发成本**:
- 开发时间：8天
- 代码量：~500行
- 新增服务：1个

**运行成本**:
- LLM调用：+1次（从2次到3次）
- 生成延迟：+15秒（从55秒到70秒）
- API成本：+30%

**预期收益**:
- Hook质量提升：60-70%
- 用户修改率降低：35-40%
- 生成成功率：95%+

---

## 10. 成功标准

### 10.1 技术指标（必须达到）

- ✅ 生成成功率 ≥ 95%（含重试）
- ✅ 平均生成时长 ≤ 70秒
- ✅ Hook生成成功率 ≥ 98%
- ✅ Validator首次通过率 ≥ 85%

### 10.2 质量指标（必须达到）

- ✅ Hook优秀率 ≥ 65%（人工评估100个样本）
- ✅ 内容重复率 < 10%（自动检测）
- ✅ 结构完整率 ≥ 95%（自动检测）

### 10.3 用户指标（必须达到）

- ✅ 用户修改率降低 ≥ 35%（对比v2）
- ✅ 盲测胜率 ≥ 65%（v3 vs v2）
- ✅ 用户满意度 ≥ 3.8/5.0

### 10.4 如果达不到

**Plan B: 增加Hook候选数量**
- 从3个增加到5个
- 成本：+3秒延迟

**Plan C: 引入轻量级Hook评分模型**
- 用小模型做二分类（是Hook/不是Hook）
- 成本：+2秒延迟

---

## 11. 附录

### 11.1 关键文件清单

**新增文件**:
```
/backend/app/services/hook_generate_service.py
/backend/app/services/enhanced_validator.py
/backend/alembic/versions/xxx_add_scene_v3_fields.py
```

**修改文件**:
```
/backend/app/models/scene.py
/backend/app/graph/generation_graph.py
/backend/app/services/scene_generate_service.py
```

### 11.2 不做的功能（明确记录）

以下功能经评审后决定不做，原因已记录：

❌ **Story Director服务** - 与SceneGenerator重复
❌ **Scene Critic服务** - AI评估AI不可靠
❌ **12个字段中的7个** - 当前用不到
❌ **并行优化** - 先验证效果
❌ **视觉层升级** - 本次聚焦内容层

---

**文档状态**: 已冻结
**下一步**: 进入开发阶段
**负责人**: 程序员团队
**预计完成**: 8个工作日
