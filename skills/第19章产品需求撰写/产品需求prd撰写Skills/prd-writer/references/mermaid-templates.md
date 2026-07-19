# Mermaid 图表模板

## 1. 序列图 (Sequence Diagram)

适用于：展示系统各组件之间的交互流程

### 基础模板

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant B as 后端
    participant D as 数据库

    U->>F: 1. 用户操作
    F->>B: 2. API 请求
    B->>D: 3. 数据查询
    D-->>B: 4. 返回数据
    B-->>F: 5. 响应结果
    F-->>U: 6. 展示界面
```

### 带条件分支的模板

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant B as 后端
    participant D as 数据库

    U->>F: 提交表单
    F->>B: POST /api/submit
    B->>B: 数据验证

    alt 验证通过
        B->>D: 保存数据
        D-->>B: 成功
        B-->>F: 200 OK
        F-->>U: 显示成功
    else 验证失败
        B-->>F: 400 错误信息
        F-->>U: 显示错误
    end
```

### 带循环的模板

```mermaid
sequenceDiagram
    participant U as 用户
    participant S as 系统

    U->>S: 开始任务

    loop 每隔5秒
        S->>S: 检查任务状态
        S-->>U: 更新进度
    end

    S-->>U: 任务完成
```

---

## 2. 流程图 (Flowchart)

适用于：展示业务逻辑、决策流程

### 基础模板（从上到下）

```mermaid
flowchart TD
    A[开始] --> B{条件判断}
    B -->|是| C[处理1]
    B -->|否| D[处理2]
    C --> E[结束]
    D --> E
```

### 基础模板（从左到右）

```mermaid
flowchart LR
    A[输入] --> B[处理] --> C[输出]
```

### 复杂业务流程

```mermaid
flowchart TD
    A[用户请求] --> B{是否登录?}
    B -->|否| C[跳转登录页]
    C --> D[登录]
    D --> B
    B -->|是| E{权限检查}
    E -->|无权限| F[显示无权限]
    E -->|有权限| G[执行操作]
    G --> H{操作成功?}
    H -->|是| I[返回成功]
    H -->|否| J[返回错误]
```

### 带子流程的模板

```mermaid
flowchart TD
    A[主流程开始] --> B[步骤1]
    B --> C[步骤2]

    subgraph 子流程
        D[子步骤1] --> E[子步骤2]
        E --> F[子步骤3]
    end

    C --> D
    F --> G[主流程结束]
```

---

## 3. 状态图 (State Diagram)

适用于：展示对象的状态变化

```mermaid
stateDiagram-v2
    [*] --> 待处理
    待处理 --> 处理中: 开始处理
    处理中 --> 已完成: 处理成功
    处理中 --> 失败: 处理失败
    失败 --> 待处理: 重试
    已完成 --> [*]
```

---

## 4. 实体关系图 (ER Diagram)

适用于：展示数据库表结构

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string name
        string email
        datetime created_at
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int user_id FK
        decimal total
        string status
        datetime created_at
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }
    PRODUCT ||--o{ ORDER_ITEM : "included in"
    PRODUCT {
        int id PK
        string name
        decimal price
        int stock
    }
```

---

## 5. 类图 (Class Diagram)

适用于：展示系统架构、模块关系

```mermaid
classDiagram
    class Controller {
        +handleRequest()
        +validateInput()
    }
    class Service {
        +businessLogic()
        +processData()
    }
    class Repository {
        +findById()
        +save()
        +delete()
    }
    class Database {
        +query()
        +execute()
    }

    Controller --> Service: 调用
    Service --> Repository: 调用
    Repository --> Database: 调用
```

---

## 6. 甘特图 (Gantt Chart)

适用于：展示项目计划、开发进度

```mermaid
gantt
    title MVP 开发计划
    dateFormat  YYYY-MM-DD
    section 阶段1
    需求分析           :a1, 2024-01-01, 3d
    技术设计           :a2, after a1, 2d
    section 阶段2
    核心功能开发       :b1, after a2, 7d
    单元测试           :b2, after b1, 2d
    section 阶段3
    集成测试           :c1, after b2, 3d
    上线部署           :c2, after c1, 1d
```

---

## 使用建议

### 选择正确的图表类型

| 场景 | 推荐图表 |
|------|----------|
| API 调用流程 | 序列图 |
| 业务决策逻辑 | 流程图 |
| 订单/任务状态 | 状态图 |
| 数据库设计 | ER 图 |
| 模块依赖关系 | 类图 |
| 开发计划 | 甘特图 |

### 图表简化原则

1. **一图一主题**：每个图只表达一个核心流程
2. **控制节点数**：单个图不超过 15 个节点
3. **命名清晰**：使用中文标注，便于理解
4. **突出重点**：核心流程放在显眼位置

### 样式建议

```mermaid
flowchart TD
    classDef primary fill:#4CAF50,stroke:#333,color:#fff
    classDef secondary fill:#2196F3,stroke:#333,color:#fff
    classDef danger fill:#f44336,stroke:#333,color:#fff

    A[开始]:::primary --> B{判断}
    B -->|成功| C[处理]:::secondary
    B -->|失败| D[错误]:::danger
```
