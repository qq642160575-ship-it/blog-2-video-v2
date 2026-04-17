# AI 自动生成视频系统系统级分析与优化方案

## 1. 系统总体评分

系统总分：`5.9 / 10`

### 分维度评分

- 内容生成质量：`5.5/10`
- 结构设计合理性：`7.0/10`
- 可控性：`5.0/10`
- 传播潜力：`4.8/10`
- 工程合理性：`7.2/10`

### 评分结论

当前系统可以稳定产出“结构化、能播、可编辑”的短视频草稿，但还不能稳定产出“高传播、高记忆点、高完成度”的短视频。

它最大的问题不是工程失控，而是：

> 系统把“文章转视频”做出来了，但还没有把“短视频内容设计”建成一个独立层。

所以当前产物更像：

- 正确的视频讲解稿

而不是：

- 具备强 Hook、节奏递进、情绪设计和平台传播潜力的短视频脚本

---

## 2. 系统级问题定位

以下问题按层分类，并且都是会直接影响系统稳定产出高质量短视频的关键问题。

### A. Prompt 层问题

#### 问题 1：缺少“传播设计层 Prompt”

当前 Prompt 体系主要是：

- 文章解析 Prompt
- Scene 生成 Prompt

中间缺了一层非常关键的：

- Hook 设计
- 叙事曲线设计
- 注意力设计
- 短视频表达改写

这意味着系统直接从“文章理解”跳到“分镜生成”，模型必须自己临场决定：

- 开头怎么抓人
- 中段怎么推进
- 结尾怎么收束

这会导致质量不稳定。

#### 问题 2：过度依赖模型自由生成

当前 Scene Prompt 给了原则，但没有强制结构，例如：

- 第 1 个 Scene 必须承担什么功能
- 中段必须完成什么认知推进
- 结尾必须完成什么收束动作

所以模型虽然输出了 JSON，但输出的仍然可能只是“格式正确的普通讲解稿”。

#### 问题 3：缺少“质量变量”的约束式输出

当前约束主要是字段齐全，而不是质量受控。

缺失的关键变量包括：

- 情绪强度
- 认知冲突类型
- Hook 类型
- 节奏峰值位置
- 场景功能唯一性
- 叙事阶段

---

### B. Scene Schema 问题

#### 问题 4：Schema 过于轻量，只能支撑“文本讲解视频”

当前 Scene Schema 核心字段主要是：

- `goal`
- `voiceover`
- `screen_text`
- `duration_sec`
- `pace`
- `transition`
- `visual_params`

这套结构可以支撑 MVP，但不足以稳定表达高质量短视频的内容控制和视觉控制。

#### 问题 5：缺少情绪与注意力控制字段

当前 Schema 无法显式表达：

- 这段想制造什么情绪
- 这段用什么方式抓住注意力
- 这段是拉高紧张感还是做认知释压

这会让 scene 之间只剩“信息顺序”，没有“情绪顺序”。

#### 问题 6：缺少镜头语法字段

当前 Schema 没有定义：

- shot_type
- motion_pattern
- emphasis_words
- reveal_style
- beat_points

结果是模板层只能吃一段文本，再做固定动画，无法真正消费“视觉意图”。

#### 问题 7：无法支持内容递进

当前 Schema 没有 scene 间关系字段，例如：

- 前一个 scene 做了什么
- 当前 scene 要承接什么
- 当前 scene 在叙事上属于 opening/build/turn/payoff 哪一段

所以 Scene 很容易变成“信息平铺”。

---

### C. 内容结构问题

#### 问题 8：Hook 被当成模板类型，而不是内容设计层

系统现在的 Hook 更像是：

- `template_type = hook_title`

而不是：

- 通过独立策略层先选择 Hook 方式，再决定用什么模板表现

这会让 Hook 退化成“第一屏标题大字”，而不是传播上的强钩子。

#### 问题 9：没有真正的叙事曲线

虽然系统中出现了 `narrative_flow`，但它只是输出字段，不是强控制变量，也没有后续校验约束。

所以它更像“事后描述”，不是“前置结构控制”。

#### 问题 10：文章适合讲解，不等于适合短视频

现在系统做的是：

- 从文章提取摘要
- 从摘要生成 scenes

但短视频真正需要的是：

- 从文章中提炼适合短视频传播的表达角度

这两者不是一回事。

---

### D. 视觉表达问题

#### 问题 11：当前视觉层仍然偏“文本转视频”

现有模板主要能力是：

- 标题渐显
- 卡片浮现
- 双栏对比
- 字幕浮层

这足够做“信息可视化”，但不足以形成“短视频视觉语法”。

#### 问题 12：视觉系统没有独立语法层

当前 `visual_params` 更像自由扩展字段，不是稳定协议。

这导致：

- Prompt 无法稳定输出视觉控制指令
- 模板无法稳定消费视觉意图
- 视觉表现难以复用和扩展

#### 问题 13：模板少不是核心问题，模板表达弱才是

3 个模板不是问题。

真正的问题是：每个模板内部缺少多种可控视觉行为模式，例如：

- zoom
- shake
- flash
- stagger reveal
- contrast reveal
- countdown reveal

---

### E. 工程流程问题

#### 问题 14：设计里有 Validator，主流程里没有真正形成强闭环

技术方案中定义了 Scene Rule Validator，但当前主链路更像是：

- Prompt 输出
- Pydantic 校验
- 继续执行

这能保证“结构合法”，但不能保证“内容有效”。

#### 问题 15：没有“生成后评估层”

当前系统缺少：

- Hook 质量评估
- Scene 重复度评估
- 节奏失衡评估
- 叙事完整性评估

没有评估层，就没有自动闭环。

#### 问题 16：Fallback 逻辑会稀释质量判断

当前有 mock/fallback 逻辑，这对流程联调有帮助，但如果长期混在主链路，会让团队对“真实生成质量”判断失真。

#### 问题 17：有日志，但没有质量反馈闭环

现在已经能记录 AI 输入输出和任务日志，这很好。

但系统还没有做到：

- 自动归类失败模式
- 回流用户修改点
- 用修改数据反向修 Prompt / Schema / 模板

---

## 3. 最大系统瓶颈

只选一个：

> 缺少“短视频内容设计中间层”

### 为什么它是最大瓶颈

当前系统基本是：

`文章解析 -> 直接分镜生成`

这跳过了最关键的一层：

- 把文章信息改写成适合短视频传播的结构

没有这一层，模型就必须一边理解文章，一边决定：

- 什么最适合做 Hook
- 什么该删
- 什么该放前面
- 什么应该做反差
- 什么适合结尾收束

这会导致输出质量高度依赖模型瞬时发挥，而不是系统控制。

### 不解决会导致什么

- Hook 不稳定
- 中段容易平铺
- 结尾缺少收束
- 视觉层只能包装普通内容
- 模板再优化，最终也只是把“普通脚本”做得更精致

也就是说：

> 不解决这个问题，整个系统上限会被锁死。

---

## 4. 系统重构建议

### ① Prompt 系统如何重构

建议把 Prompt 系统拆成四层，而不是继续用单一 Scene Prompt 扛全部职责。

#### 第一层：Article Analyst

职责：

- 提取文章事实
- 提取核心观点
- 提取关键论点
- 提取应丢弃的部分
- 标出最适合视频化的部分

输出应包含：

- facts
- key_points
- visualizable_points
- discarded_parts
- target_audience
- content_risk

#### 第二层：Hook Strategist

职责：

- 生成多个 Hook 方案
- 为 Hook 排序
- 选择最适合当前文章和受众的开头方式

控制变量：

- hook_type
- tension_level
- curiosity_gap
- promise_type
- target_emotion

#### 第三层：Short Video Director

职责：

- 把文章理解结果改写成短视频叙事骨架

输出内容：

- opening
- problem
- misconception
- reveal
- payoff
- close

控制变量：

- 节奏强弱
- 信息密度分布
- 情绪曲线
- 认知转折点

#### 第四层：Scene Writer

职责：

- 把导演层输出展开成可渲染的 Scene

强约束：

- 每个 Scene 只能承担一个主要功能
- Scene 间必须有推进关系
- 前中后段必须承担不同任务

#### 第五层：Visual Mapper

职责：

- 根据 scene 的功能与情绪，选择模板和视觉行为

它不再只吃 `template_type`，而要吃：

- scene_function
- emotion
- attention_pattern
- visual_intent

---

### ② Scene Schema 如何升级

建议把当前轻量 Scene Schema 升级为“可控短视频协议”。

至少新增以下字段：

#### 内容控制字段

- `scene_function`
  - hook / problem / explanation / misconception / comparison / payoff / cta
- `narrative_stage`
  - opening / build / turn / payoff / close
- `carry_over`
  - 本 scene 如何承接上一段

#### 情绪与传播字段

- `emotion`
  - surprise / urgency / clarity / tension / confidence / relief
- `energy_level`
  - 1-5
- `attention_pattern`
  - question / reveal / contrast / countdown / escalation
- `surprise_type`
  - anti-common-sense / mistaken-belief / hidden-cost / hidden-benefit

#### 视觉控制字段

- `shot_type`
  - title / list / compare / quote / timeline / focus
- `motion_pattern`
  - fade / pop / slide / zoom / shake / flash / stagger
- `emphasis_words`
  - 用于视觉重点高亮
- `beat_points`
  - 配合字幕与动画节奏
- `visual_intent`
  - 结构化视觉意图，不再是自由 dict

#### 质量辅助字段

- `must_keep_fact`
- `duplicate_risk`
- `editor_note`

---

### ③ Pipeline 如何调整

建议从当前链路：

`文章解析 -> Scene 生成 -> TTS -> 字幕 -> 渲染`

升级为：

1. Article Parse  
2. Content Distill  
3. Hook Generate  
4. Story Director  
5. Scene Generate  
6. Scene Critic  
7. Visual Mapping  
8. TTS  
9. Subtitle Alignment  
10. Render  
11. Post-render QA

### 调整原因

- `Scene Generate` 前必须先做内容策略层
- `Scene Generate` 后必须做质量评估层
- `Visual Mapping` 应该作为独立步骤，而不是 Prompt 顺带决定

---

### ④ 是否需要新增中间层

必须新增，至少需要以下 3 层：

#### Story Layer

职责：

- 定义叙事阶段
- 控制信息推进顺序
- 保证前后场景的逻辑关系

#### Emotion Layer

职责：

- 明确每一段希望传达的情绪
- 保证节奏和情绪不是平的

#### Attention Layer

职责：

- 设计开头抓手
- 控制认知冲突和反差点
- 控制视频中段的注意力回收

如果不增加这些中间层，系统就只能继续依赖模型“自己发挥”。

---

## 5. 理想系统架构

下面是一个“可以稳定生成高质量短视频”的理想系统描述。

### 输入层

输入内容：

- 标题
- 正文
- 内容类型
- 目标平台
- 目标受众
- 时长
- 风格偏好

职责：

- 做输入校验
- 做内容预处理
- 保留原文事实边界

控制变量：

- 时长
- 平台风格
- 保守/激进程度
- 信息压缩率

---

### 内容理解层

职责：

- 提取事实
- 提取观点
- 提取关键论点
- 提取可视化点
- 删除不适合短视频的部分

控制变量：

- 事实保真
- 信息压缩率
- 不补充原文之外内容

输出：

- ArticleAnalysisPlus

---

### 传播设计层

职责：

- 设计 Hook
- 设计叙事曲线
- 设计受众进入方式
- 设计情绪推进

控制变量：

- hook_type
- tension_level
- curiosity_gap
- payoff_type
- CTA 风格

输出：

- StoryBlueprint

---

### 脚本生成层

职责：

- 把 StoryBlueprint 变成 Scene 列表

控制变量：

- scene_function
- narrative_stage
- 信息密度
- 节奏强弱
- 情绪曲线

输出：

- Structured SceneSpec[]

---

### 视觉映射层

职责：

- 根据 Scene 意图匹配模板
- 把内容变量转成视觉变量

控制变量：

- shot_type
- motion_pattern
- emphasis_words
- reveal_style

输出：

- Render-ready Scene Payload

---

### 语音字幕层

职责：

- 生成配音
- 控制停顿和语速
- 生成字幕并对齐

控制变量：

- 语速
- 停顿
- 重音词
- 字幕切分粒度

---

### 评估层

职责：

- 检查 Hook 强度
- 检查结构重复
- 检查节奏失衡
- 检查收束是否完整

控制变量：

- 最低质量阈值
- 自动重试策略
- critic 得分门槛

---

### 渲染层

职责：

- 消费稳定协议
- 输出 MP4、字幕、Scene JSON

控制变量：

- 模板选择
- 动效参数
- 时长边界
- 字幕安全区

---

### 反馈层

职责：

- 记录 AI 输入输出
- 记录任务失败点
- 记录用户修改行为
- 反向驱动 Prompt 和 Schema 优化

控制变量：

- 失败模式分类
- 修改点统计
- 模板命中率
- quality score

---

## 6. 快速优化清单

### 3 个“立刻改就会变好”的点

#### 1. 升级 Scene Schema

立刻增加：

- `scene_function`
- `emotion`
- `attention_pattern`
- `narrative_stage`

原因：

- 成本低
- 立刻增强系统可控性
- 后续 Prompt、模板、评估层都能复用

#### 2. 把 Scene Prompt 拆成 Hook + Director + Scene Writer

不要再用一个 Prompt 既做传播设计又做分镜输出。

原因：

- 这样可以显著减少模型自由发挥
- 让质量控制点更清晰

#### 3. 增加 Scene Critic

在进入 TTS 前增加自动评估：

- 开头是否足够强
- 是否有内容重复
- 是否有叙事转折
- 是否存在 payoff

不通过就重试。

---

### 3 个“长期必须重构”的点

#### 1. 重构为内容层 / 传播层 / 分镜层 / 视觉层四层系统

这是系统上限问题，不是小优化。

#### 2. 重构视觉协议

把 `visual_params` 从自由 dict 升级为可控视觉语法协议。

否则模板系统永远只是“文本排版器”。

#### 3. 建立生成后评估闭环

要形成：

- 生成
- 自动评估
- 用户修改回流
- Prompt / Schema / 模板迭代

没有这一步，系统只能靠人工感觉优化。

---

## 7. 优先级结论

建议的优先顺序如下：

1. 先补 `Story / Hook / Attention` 中间层  
2. 再升级 Scene Schema  
3. 再加 Scene Critic  
4. 然后重构 Visual Intent 协议  
5. 最后才值得扩模板数量

---

## 8. 最终结论

这个系统当前最大的问题不是工程，而是：

> 没有把“短视频内容设计”建成独立系统层。

所以它现在可以稳定生成：

- 可运行
- 可渲染
- 可编辑
- 有基本结构

但还不能稳定生成：

- 强 Hook
- 强节奏
- 强情绪递进
- 强传播潜力

如果继续只优化 Prompt 文案、模板视觉细节、日志系统，而不补上内容设计中间层，整体质量提升会非常有限。
