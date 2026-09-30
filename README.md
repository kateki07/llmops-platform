# llmops-platform

基于 **Flask + LangChain** 构建的 LLM 应用平台后端，支持多轮对话记忆与知识库检索（RAG）。

前端仓库：[kateki07/llmops-ui](https://github.com/kateki07/llmops-ui)（Vue 3 + TypeScript）

<!-- 截图放到 docs/screenshot.png 之后，取消下面这行的注释
![调试界面](docs/screenshot.png)
-->

---

## 已实现的能力

| 能力 | 说明 |
|---|---|
| **对话记忆** | 滑动窗口记忆（保留最近 N 轮），历史持久化到文件，会话重启后不丢失 |
| **知识库检索** | 文档向量化后存入 Weaviate，提问时检索相关片段注入提示词，支持元数据过滤 |
| **链式编排** | 基于 LCEL 组装提示词、记忆、检索与模型，记忆读取与向量检索并行执行 |
| **统一响应协议** | 全部接口返回 `code` / `message` / `data` 三字段，业务状态码与 HTTP 状态码分离 |
| **参数校验** | 基于 WTForms 的请求校验，校验失败统一返回 `validate_error` |
| **应用管理** | App 实体的增删改查，UUID 主键，Alembic 管理表结构迁移 |
| **可观测性** | 接入 LangSmith，每次链调用的各步骤耗时、输入输出、Token 消耗可追溯 |
| **跨域支持** | `after_request` 统一注入 CORS 响应头，正确处理预检请求 |

### 主要接口

```
GET   /ping                          健康检查
POST  /apps/<uuid:app_id>/debug      对话调试（记忆 + 知识库检索）
POST  /app/completion                单轮对话
POST  /app                           创建应用
GET   /app/<uuid:id>                 查询应用
POST  /app/<uuid:id>                 更新应用
POST  /app/<uuid:id>/delete          删除应用
```

---

## 架构

```
app/http/app.py          入口：加载环境变量 → 构建配置 → 装配依赖注入容器 → 启动
        │
        ├── config/                  配置对象，值全部来自环境变量，代码内无默认密钥
        │
        └── internal/
              ├── server/            Flask 应用封装，注册扩展、路由、CORS 钩子
              ├── router/            路由表，URL 与 handler 方法的绑定集中在一处
              ├── handler/           接收请求、校验参数、编排链、返回响应
              ├── service/           业务逻辑与外部资源封装（AppService / VectorDatabaseService）
              ├── model/             SQLAlchemy 模型
              ├── schema/            请求参数定义与校验规则
              ├── exception/         业务异常，与响应层的业务状态码对应
              ├── extension/         数据库、迁移等扩展的初始化
              └── migration/         Alembic 迁移脚本

pkg/                     与业务无关的通用能力
    ├── response/        统一响应结构与业务状态码
    └── sqlalchemy/      SQLAlchemy 封装，提供 auto_commit 上下文管理器

study/                   课程随堂练习，非平台代码（见 study/README.md）
```

分层规则：**`handler` 不直接碰数据库，`service` 不感知 HTTP**。依赖关系由 `injector` 在启动时装配，各层之间通过构造注入连接，不使用全局单例。

---

## 技术选型与设计取舍

这一节记录的是**为什么这么做**，而不是用了什么。

### 向量数据库封装在 service 之后

`VectorDatabaseService` 对外只暴露 `get_retriever()` 和 `combine_documents()`，Weaviate 的客户端、索引名、嵌入模型都封在里面。

上层的 handler 拿到的是一个 LangChain `Runnable`，不知道底层是 Weaviate 还是别的。**换成 Faiss 只需要改这一个文件，链的代码一行不动。**

这不是过度设计——向量库选型在项目早期通常定不下来：本地开发用嵌入式的 Faiss 更轻，生产要元数据过滤和并发就得换独立服务。把这个决策隔离在一层之后，迁移成本从"改遍全项目"降到"改一个类"。

### 记忆在调用时传入，而不是写进链里

早期实现把 `memory` 对象直接捕获进链：

```python
chain = RunnablePassthrough.assign(
    history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
) | prompt | llm
```

这样一条链就绑死了一个用户的记忆，多用户场景下必须为每个请求重建整条链。

改为从 `RunnableConfig` 运行时读取：

```python
chain.invoke(chain_input, config={"configurable": {"memory": memory}})
```

链本身变成**无状态、可复用**的对象，记忆由调用方在调用时提供。写回记忆交给 `with_listeners(on_end=...)`，调用方不需要记得手动调 `save_context`，少一处可能遗漏的地方。

> 这与 Spring 中「Service 保持单例、用户态通过方法参数传递」是同一个原则。区别在于 LangChain 的示例代码大多是单用户脚本，这个问题在本地开发时不会暴露。

### 记忆与检索并行

`RunnablePassthrough.assign` 中的多个 key 是并行求值的，因此"读取历史记忆"与"向量检索"同时进行。

LangSmith 的调用链显示整体耗时约等于 `max(记忆, 检索) + 模型`，而非三者相加。在检索耗时约 1.8s 的情况下，这部分被模型调用的 7.8s 完全掩盖。

同时这也说明了**优化方向**：瓶颈在模型响应而非检索，应该优先做流式输出，而不是调优向量库。

### 依赖版本锁定在 LangChain 0.2.x

`langchain-core` 在 0.3 引入了破坏性变更，且 `langchain-weaviate` 等周边包的新版本会连带要求升级核心库。

`requirements.txt` 中核心链路的版本全部写死。执行 `pip install -U` 升级单个包会连锁升级整套依赖并导致大面积不兼容——这类问题排查成本很高，锁版本是更省事的选择。

### 业务状态码与 HTTP 状态码分离

所有接口固定返回 HTTP 200，处理结果由响应体中的 `code` 字段表达：

```json
{ "code": "success", "message": "", "data": { "content": "..." } }
```

前端只需一套解析逻辑，不必区分"网络层失败"与"业务层失败"。HTTP 状态码保留给真正的传输层问题（连接失败、网关错误），语义不会混淆。

---

## 本地运行

### 环境要求

- Python 3.12
- PostgreSQL 16
- Docker（用于运行 Weaviate）
- Node.js 20+（如需同时运行前端）

### 1. 安装依赖

```bash
python -m venv env
env\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入自己的值：

```bash
cp .env.example .env
```

必填项：`SQLALCHEMY_DATABASE_URI`、`OPENAI_API_KEY`、`WEAVIATE_HOST`、`WEAVIATE_PORT`。

### 3. 启动依赖服务

```bash
# PostgreSQL（按各自安装方式启动）

# Weaviate
docker run -d --name weaviate-dev \
  -p 8080:8080 -p 50051:50051 \
  cr.weaviate.io/semitechnologies/weaviate:1.24.20
```

验证 Weaviate 已就绪：

```bash
curl http://localhost:8080/v1/meta
```

### 4. 初始化数据库

```bash
flask --app app.http.app db upgrade
```

### 5. 启动

```bash
python -m app.http.app
```

服务监听 `http://localhost:5000`。

### 服务依赖关系

启动顺序不能颠倒——应用在装配阶段就会连接数据库与向量库：

```
PostgreSQL (5432) ─┐
                   ├─→ Flask (5000) ←─ Vite (5173)
Weaviate   (8080) ─┘
```

---

## 开发记录

排查过程中值得记录的几个问题。

### `.env` 从未被读取

配置全部走了默认值，且**没有任何报错**。两个原因叠加：虚拟环境中未安装 `python-dotenv`；Flask 仅在 `flask run` 下自动加载 `.env`，而当时用的是 `python -m`。

修复方式是在 `Config()` 实例化**之前**显式调用 `load_dotenv()`——顺序颠倒的话同样不报错，只是继续读不到。

### 连接池配置静默失效

`SQLALCHEMY_POOL_SIZE` 在 Flask-SQLAlchemy 3.0 中已被移除，改为 `SQLALCHEMY_ENGINE_OPTIONS`。旧写法不会报错，只是被忽略。

由于默认值恰好与配置值相同，这个问题在监控连接数之前完全不可见。

### `@dataclass` 重写了异常类的构造函数

`FailException("数据未找到")` 的消息被赋给了 `code` 字段。原因是 `@dataclass` 按字段声明顺序 `(code, message, data)` 生成了 `__init__`，覆盖了 `Exception` 原本的行为。

用 `inspect.signature` 打印构造函数签名可以直接确认。修复方式是改用关键字参数调用，不改动类定义。

### CORS 预检请求打到了错误的处理函数

`/app/<uuid:id>` 同时注册了 `GET` 和 `POST`，并额外加了 `OPTIONS`。浏览器发出的预检请求匹配到了 `update_app`，该方法尝试访问不存在的属性而返回 500。

正确做法是不在业务路由上声明 `OPTIONS`，交给 Flask 自动处理，CORS 响应头则统一由 `after_request` 钩子注入。

---

## 关于本项目

本项目基于慕课网《AI Agent 全栈开发（LLMOps）》课程构建。

在课程内容之外做了以下调整：

- 课程示例代码中硬编码的 API 密钥与主机地址，全部改为从环境变量读取
- 配置项补充了 Flask-SQLAlchemy 3.x 的正确写法（课程使用的是已废弃的键名）
- 依赖清单按实际安装版本整理，区分了主线必需与练习按需的依赖
