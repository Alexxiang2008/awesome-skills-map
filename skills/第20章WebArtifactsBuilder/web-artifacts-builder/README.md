【案例】Web Artifacts Builder Skill —— 一键生成可分享的 React Artifact 🚀
输入：你想做的网页应用描述
输出：一个可以直接分享的 HTML 文件

web-artifacts-builder 能帮你把复杂的 React 项目打包成一个 HTML 文件，直接丢给别人就能用。不用再发一堆文件夹了。

---

### 举个例子

假设你想做一个任务管理小应用，有添加任务、勾选完成、删除这些功能。

**以前怎么做？**
1. 先装 Node.js
2. 跑一堆命令创建项目
3. 一个个装 UI 组件库
4. 配置一大堆东西
5. 写完代码后，发给别人还得教他们怎么跑起来

**现在怎么做？**
1. 跑一行命令，项目就建好了
2. 40 多个漂亮的组件直接用
3. 写完后再跑一行命令
4. 得到一个 HTML 文件，发给谁都能直接打开

---

### 传统方式 vs Web Artifacts Builder

| 传统方式 | 用这个 Skill |
|---------|-------------|
| 手动配置一堆东西 | 一行命令搞定 |
| 一个个装组件 | 40+ 组件开箱即用 |
| 发项目文件夹给别人 | 发一个 HTML 文件 |
| 别人还得装环境才能跑 | 浏览器打开就能用 |

---

### 怎么用？

就四步：

```
第 1 步：创建项目
跑这个命令 → bash scripts/init-artifact.sh my-app

第 2 步：写代码
在 src/ 文件夹里写你的页面和组件

第 3 步：打包
跑这个命令 → bash scripts/bundle-artifact.sh

第 4 步：分享
把生成的 bundle.html 发给任何人
```

---

### 用了哪些技术？

不用全记住，知道大概就行：

| 干嘛用的 | 技术名字 |
|---------|---------|
| 写页面逻辑 | React + TypeScript |
| 开发时预览 | Vite |
| 打包成一个文件 | Parcel |
| 写样式 | Tailwind CSS |
| 漂亮的组件 | shadcn/ui |

---

### 有哪些现成的组件？

装完就能用的组件，不用自己写：

**布局类的**
- 折叠面板、卡片、标签页、可调整大小的面板...

**表单类的**
- 按钮、输入框、下拉选择、开关、滑块、复选框...

**提示类的**
- 弹窗、提示条、加载骨架屏、进度条...

**导航类的**
- 菜单、面包屑、右键菜单、下拉菜单...

**展示类的**
- 头像、日历、轮播图、表格、对话框...

一共 40 多个，够用了。

---

### 代码长什么样？

导入组件很简单：

```tsx
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
```

写一个任务卡片：

```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'

export function TaskCard({ task }) {
  return (
    <Card>
      <CardHeader>
        <Checkbox checked={task.completed} />
        <CardTitle>{task.title}</CardTitle>
        <Badge>{task.priority}</Badge>
      </CardHeader>
      <CardContent>
        <p>{task.description}</p>
        <Button>编辑</Button>
        <Button>删除</Button>
      </CardContent>
    </Card>
  )
}
```

看起来像写 HTML，但是有逻辑、能交互。

---

### 什么时候该用这个？

**适合用的场景：**
- 想做一个小工具分享给朋友
- 需要按钮、表单、弹窗这些交互
- 想要好看的 UI 但不想自己设计
- 需要打包成一个文件方便传播

**不太需要用的场景：**
- 就写个静态页面，没啥交互
- 代码很简单，几十行就搞定了

---

### 电脑要装什么？

- Node.js 18 或更高版本（去官网下就行）
- pnpm（脚本会自动帮你装）

---

### 怎么安装这个 Skill？

把 `web-artifacts-builder/` 这个文件夹复制到：

- 所有项目都能用：`~/.claude/skills/web-artifacts-builder/`
- 只在当前项目用：`你的项目/.claude/skills/web-artifacts-builder/`

---

### 从头到尾走一遍

```bash
# 1. 创建一个叫 my-dashboard 的项目
bash ~/.claude/skills/web-artifacts-builder/scripts/init-artifact.sh my-dashboard

# 2. 进去
cd my-dashboard

# 3. 开发时实时预览
pnpm dev

# 4. 写完了，打包
bash ~/.claude/skills/web-artifacts-builder/scripts/bundle-artifact.sh

# 5. 完事了，bundle.html 就是最终文件
```

---

### 想了解更多？

- [shadcn/ui 组件文档](https://ui.shadcn.com/docs/components) - 看看有哪些组件
- [Tailwind CSS 文档](https://tailwindcss.com/docs) - 学学怎么写样式
