# DAOCouncil Frontend

DAOCouncil 是一个用于 DAO 治理讨论的虚拟法庭平台。

## 快速开始

```bash
npm install  # 安装依赖
npm run dev  # 启动开发服务器
```

## 项目结构

```
src/
├── components/         # 组件目录
│   ├── Header.jsx     # 头部组件：导航栏和钱包连接
│   ├── CourtRoom.jsx  # 法庭组件：法庭界面和投票倾向指示器
│   ├── UserAvatar.jsx # 用户头像组件：处理用户和 AI 评委的头像显示
│   ├── Messages.jsx   # 消息组件：聊天界面和消息输入
│   └── JurorOpinions.jsx # 评委意见组件：显示 AI 评委的意见
├── hooks/             # 自定义 Hook 目录
│   ├── useMessages.js    # 消息相关逻辑：处理消息状态和操作
│   └── useJurorOpinions.js # 评委意见相关逻辑：处理评委意见状态
├── utils/             # 工具函数目录
│   └── avatarUtils.js    # 头像相关工具函数：处理头像显示逻辑
└── constants/         # 常量目录
    └── avatarColors.js   # 头像颜色常量：定义头像背景色
```

## 主要功能

1. **讨论系统**
   - 多人实时讨论
   - 支持立场表达（支持/反对/中立）
   - 消息历史记录
   - 轮次管理

2. **AI 评委系统**
   - AI 评委意见展示
   - 评分和投票机制
   - 可展开/收起的详细意见视图

3. **钱包集成**
   - 钱包连接功能
   - 地址显示
   - 连接状态管理

4. **用户界面**
   - 虚拟法庭场景
   - 动态投票倾向指示器
   - 用户头像系统
   - 响应式设计

## 技术栈

- React 18
- Vite
- Tailwind CSS
- ESLint

## 组件说明

### Header
- 显示应用标题
- 处理钱包连接
- 显示钱包状态

### CourtRoom
- 显示虚拟法庭场景
- 展示投票倾向指示器
- 处理动画效果

### UserAvatar
- 生成用户头像
- 支持 AI 评委特殊显示
- 提供多种尺寸选项

### Messages
- 显示聊天消息
- 处理消息输入
- 管理用户立场选择

### JurorOpinions
- 显示 AI 评委意见
- 支持展开/收起视图
- 展示评分和投票倾向

## 开发指南

1. **添加新组件**
   - 在 `components` 目录创建新文件
   - 遵循现有的组件结构
   - 更新 README.md

2. **修改样式**
   - 使用 Tailwind CSS 类
   - 保持与现有设计一致
   - 注意响应式设计

3. **状态管理**
   - 使用自定义 Hooks 管理复杂状态
   - 保持组件职责单一
   - 适当拆分逻辑

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request