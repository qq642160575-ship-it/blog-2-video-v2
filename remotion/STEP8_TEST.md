# Step 8 测试指南 - Remotion 模板

## ✅ Step 8 已完成

已创建最简单的 Remotion 模板 `HookTitle`，可以渲染标题和副标题的视频。

## 📁 项目结构

```
remotion/
├── src/
│   ├── index.tsx              # 入口文件，注册 Composition
│   └── compositions/
│       └── HookTitle.tsx      # HookTitle 模板组件
├── out/
│   └── test.mp4              # 渲染输出（297KB，6秒视频）
├── package.json
├── tsconfig.json
└── remotion.config.ts
```

## 🎨 HookTitle 模板特性

- **尺寸**: 1080x1920 (9:16 竖屏)
- **时长**: 6秒 (180帧 @ 30fps)
- **动画**:
  - 标题淡入 (0-0.5秒)
  - 副标题淡入 (0.3-0.8秒)
- **样式**: 深色背景 (#1a1a2e)，白色标题，浅蓝色副标题

## 🧪 如何测试

### 方式 1: 手动渲染

```bash
cd remotion
npm run test
```

输出: `remotion/out/test.mp4`

### 方式 2: 启动 Remotion Studio（可视化编辑）

```bash
cd remotion
npm start
```

然后在浏览器中打开 http://localhost:3000

### 方式 3: 自定义参数渲染

```bash
cd remotion
npx remotion render src/index.tsx HookTitle out/custom.mp4 \
  --props='{"title":"自定义标题","subtitle":"自定义副标题"}'
```

## ✅ 验证结果

已成功渲染测试视频:
- 文件: `remotion/out/test.mp4`
- 大小: 297KB
- 时长: 6秒
- 分辨率: 1080x1920

## 📊 模板参数

```typescript
interface HookTitleProps {
  title: string;      // 主标题
  subtitle: string;   // 副标题
}
```

默认参数:
```json
{
  "title": "什么是 RAG？",
  "subtitle": "检索增强生成技术解析"
}
```

## 🎯 下一步：Step 9

创建 Render Worker，从渲染队列消费任务并调用 Remotion 渲染视频。
