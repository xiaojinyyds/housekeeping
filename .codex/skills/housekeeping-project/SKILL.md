---
name: housekeeping-project
description: 帮助 Codex 快速理解家政服务项目的后台管理端与微信小程序结构、核心业务模块和默认开发路径。
---

# Housekeeping Project Skill

## Purpose
帮助 Codex 快速进入这个家政服务项目的上下文，减少每次重新摸索目录、业务模块和改动边界的成本。

## Trigger Words
当用户请求中出现以下词语或近似表达时，应优先使用本 skill：
- 家政服务项目
- housekeeping project
- geeker-admin
- wxfront
- 家政后台
- 家政小程序
- adminOps
- 线索管理
- 家政工管理
- 员工管理
- 合同管理
- 工人申请

当用户提出以下类型任务时使用本 skill：
- 修改或排查 `geeker-admin` 后台管理端功能
- 修改或排查 `wxfront` 微信小程序功能
- 新增家政业务页面、接口对接、列表/详情/创建/编辑页
- 调整路由、状态管理、公共组件、权限、国际化、主题样式
- 需要先理解本项目结构再执行开发、修复、重构、评审

## Best For
本 skill 特别适合这些场景：
- 进入仓库后的首次项目理解
- 根据业务名称快速定位代码目录
- 在后台管理端新增或修改业务页面
- 排查接口、路由、store、权限之间的联动问题
- 判断一个需求应该改后台端、微信小程序端，还是两端一起改
- 代码评审前快速建立项目上下文

## Suggested Commands
如果终端可用，优先使用这些命令快速建立上下文：

```powershell
Get-ChildItem
rg --files
rg "adminOps|lead|worker|staff|contract" geeker-admin/src
rg "createWorker|workerList|leadList|contractList" geeker-admin/src/views
rg "login|user|business|upload" geeker-admin/src/api
rg --files wxfront
rg "Page\\(|request|wx.request" wxfront
```

如果要进一步聚焦后台管理端，优先执行：

```powershell
rg --files geeker-admin/src/views/adminOps
rg --files geeker-admin/src/api/modules
rg --files geeker-admin/src/stores/modules
rg --files geeker-admin/src/routers
```

如果要进一步聚焦小程序端，优先执行：

```powershell
rg --files wxfront/pages
rg --files wxfront/utils
```

## Read First
进入项目后，优先阅读这些位置：

### 仓库级别
- `geeker-admin/package.json`
- `wxfront/app.json`
- `wxfront/project.config.json`

### 后台管理端入口
- `geeker-admin/src/main.ts`
- `geeker-admin/src/App.vue`
- `geeker-admin/src/routers/index.ts`
- `geeker-admin/src/stores/index.ts`
- `geeker-admin/src/api/index.ts`
- `geeker-admin/src/config/index.ts`

### 后台核心业务
- `geeker-admin/src/views/adminOps/**`
- `geeker-admin/src/views/home/**`
- `geeker-admin/src/api/modules/business.ts`
- `geeker-admin/src/api/modules/user.ts`
- `geeker-admin/src/api/modules/upload.ts`

### 后台公共能力
- `geeker-admin/src/components/ProTable/index.vue`
- `geeker-admin/src/components/SearchForm/index.vue`
- `geeker-admin/src/components/Upload/Img.vue`
- `geeker-admin/src/components/Upload/Imgs.vue`
- `geeker-admin/src/layouts/**`
- `geeker-admin/src/hooks/**`
- `geeker-admin/src/utils/**`

### 后台状态与权限
- `geeker-admin/src/stores/modules/auth.ts`
- `geeker-admin/src/stores/modules/user.ts`
- `geeker-admin/src/stores/modules/global.ts`
- `geeker-admin/src/routers/modules/dynamicRouter.ts`
- `geeker-admin/src/routers/modules/staticRouter.ts`

### 微信小程序端
- `wxfront/app.js`
- `wxfront/app.json`
- `wxfront/utils/api.js`
- `wxfront/pages/index/**`
- `wxfront/pages/detail/**`
- `wxfront/pages/agreement/**`
- `wxfront/pages/privacy/**`

## Project Snapshot
这是一个“家政服务”项目，当前仓库里至少包含两个主要前端：

1. `geeker-admin`
这是后台管理端，技术栈从目录判断为：
- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- 多个可复用后台组件与布局系统

2. `wxfront`
这是微信小程序端，使用原生小程序目录结构：
- `app.js / app.json / app.wxss`
- `pages/*`
- `utils/api.js`

## Repo Map
优先关注以下目录：

### `geeker-admin/src`
- `api/`
  接口封装层，含登录、用户、上传、业务接口模块
- `components/`
  后台通用组件，如 `ProTable`、`SearchForm`、`Grid`、`Upload`、`ECharts`
- `config/`
  全局配置与进度条等
- `directives/`
  自定义指令，如权限、复制、节流、防抖、拖拽、水印
- `hooks/`
  通用组合式逻辑，如表格、主题、权限、下载、时间处理
- `languages/`
  国际化中英文资源
- `layouts/`
  后台布局骨架、头部、标签页、主题抽屉、菜单等
- `routers/`
  静态/动态路由
- `stores/`
  Pinia 状态管理，重点关注用户、权限、全局配置、tabs、keepAlive
- `styles/`
  全局样式、主题变量、Element 样式覆盖
- `utils/`
  工具函数、事件总线、错误处理、字典、校验、svg 处理
- `views/`
  业务页面与示例页面

### `geeker-admin/src/views/adminOps`
这是当前项目最核心的业务域之一，围绕家政后台运营管理：
- 线索：`leadList`、`leadDetail`、`createLead`、`editLead`、`guestLeadList`
- 员工/工作人员：`staffList`、`staffDetail`、`createStaff`、`editStaff`
- 家政工人：`workerList`、`workerDetail`、`createWorker`、`editWorker`
- 合同：`contractList`、`contractDetail`、`createContract`
- 申请/用户：`workerApplications`、`userList`

处理相关需求时，优先从这里建立业务上下文。

### `geeker-admin/src/views/home`
首页工作台，包含：
- `AdminWorkbench.vue`
- `StaffWorkbench.vue`

如果任务涉及角色首页差异、首页数据面板、快捷入口，这里通常是入口。

### `wxfront`
小程序主要页面：
- `pages/index`
- `pages/detail`
- `pages/agreement`
- `pages/privacy`
- `utils/api.js`

如果用户需求涉及 C 端展示、详情页、协议/隐私页、埋点或小程序接口联动，优先从这些位置入手。

## Working Style For This Repo
使用本 skill 时，默认遵循以下策略：

1. 先判断改动属于哪个端
- 后台管理功能：优先看 `geeker-admin`
- 小程序功能：优先看 `wxfront`
- 两端联动：先找接口字段与业务实体，再分别改两端

2. 在后台端优先定位三层
- 页面：`views/**`
- 状态/路由：`stores/**`、`routers/**`
- 接口：`api/modules/**`

3. 修改后台列表页时，优先检查这些公共能力是否已存在
- `ProTable`
- `SearchForm`
- `TreeFilter`
- `SelectFilter`
- `Upload`

4. 新增页面或表单时，优先保持现有后台风格
- 先复用已有页面结构
- 复用同类业务页面的表单字段组织方式
- 不要引入与现有布局割裂的新交互模式

5. 涉及权限、菜单、用户态时，额外检查
- `stores/modules/auth.ts`
- `stores/modules/user.ts`
- `routers/modules/*`
- 相关菜单 JSON 或动态路由来源

6. 涉及国际化文案时，同时检查
- `languages/modules/zh.ts`
- `languages/modules/en.ts`

7. 涉及主题、样式异常时，重点检查
- `styles/var.scss`
- `styles/common.scss`
- `styles/element.scss`
- `layouts/**`

## Domain Understanding
从目录命名判断，这个项目至少覆盖以下业务对象：
- 线索 `lead`
- 员工 `staff`
- 家政工/阿姨 `worker`
- 合同 `contract`
- 用户 `user`
- 工人申请 `workerApplications`

因此在实现需求时，应优先寻找这些实体在以下位置的对应关系：
- 页面目录名
- API 模块名
- 表格列定义
- 表单字段
- 详情页展示结构

如果用户只给出业务名而没指出代码位置，优先搜索这些关键词。

## Default Investigation Flow
收到任务后，按以下顺序工作：

1. 确认任务属于 `geeker-admin` 还是 `wxfront`
2. 找到对应页面入口与相邻模块
3. 再看接口封装与数据结构
4. 如果是后台页面，优先复用已有通用组件
5. 做最小范围改动，避免无关重构
6. 完成后尽量运行该端可执行的校验命令

## Execution Guidance
如果要修改 `geeker-admin`：
- 先读对应 `views` 页面
- 再读 `api/modules` 中相关接口
- 必要时看 `stores/modules` 和 `routers/modules`
- 尽量沿用已有的 `ProTable`、表单、上传、筛选器模式

如果要修改 `wxfront`：
- 先读目标页面目录下的 `.js/.wxml/.wxss/.json`
- 再读 `utils/api.js`
- 保持原生小程序结构与数据流，不要强行引入后台端写法

## Caution Points
- `geeker-admin/src/views` 下既有通用示例页面，也有真实业务页面；处理家政业务需求时，优先聚焦 `adminOps`、`home`、`worker`
- 不要把演示页代码风格直接复制到核心业务页，除非目标页本身就复用了那套模式
- 如果改动列表/详情/创建/编辑四类页面中的某一个，注意同实体的其他页面是否也需要同步调整
- 涉及图片上传时，先检查是否已有 `Upload` 或业务内专用上传组件，例如 `createWorker/components/ImageUploader.vue`
- 涉及角色差异时，关注首页工作台和权限/菜单联动

## Expected Output Style
在这个项目中工作时，Codex 应该：
- 先用简短中文说明自己定位到的端和模块
- 解释将要修改的页面、接口或 store
- 改动尽量收敛，优先复用现有模式
- 最终汇报时说明影响范围、验证情况、是否还有待确认的接口或字段

## When Information Is Missing
如果命令不可用或仓库信息不完整，也应基于当前已知目录先建立上下文，不要停在泛泛建议上。

尤其是：
- 已知后台主工程是 `geeker-admin`
- 已知小程序工程是 `wxfront`
- 已知核心业务域是 `adminOps`

在此基础上先完成分析或初版实现，再指出仍需补充的信息。
