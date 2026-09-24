# study/ — 课程随堂练习

> **这里不是平台功能代码。**
> 本目录是跟随《AI Agent 全栈开发 (LLMOps)》课程逐讲敲写的 LangChain 组件示例，
> 用于理解各组件的行为和边界。平台本身的代码在 [`../internal/`](../internal/)。

每个子目录对应课程的一讲，文件可独立运行，相互之间没有依赖。

## 目录索引

| 讲次 | 主题 |
|---|---|
| 1–6 | Prompt / Model / OutputParser / LCEL / Runnable 核心类 / 回调调试 |
| 7–14 | 记忆：原生 SDK 实现、ChatMessageHistory、四种记忆策略、内置 Chain、RunnableWithMessageHistory |
| 15–19 | Runnable 进阶：`bind` / `configurable_fields` / `configurable_alternatives` / 重试与回退 / 生命周期监听器 |
| 20–22 | 嵌入模型：OpenAI、缓存包装、HuggingFace 与百度千帆 |
| 23–27 | 向量数据库：Faiss / Pinecone / TCVectorDB / Weaviate / 自定义对接 |
| 28–31 | 文档加载：Document 结构、内置与自定义加载器、Blob 解析器 |
| 32–36 | 文档分割：字符 / 递归字符 / 语义分割、自定义分割器、非分割型转换器 |
| 37–39 | 检索：VectorStore 检索方法、Retriever 组件、自定义检索器 |
| 40–52 | RAG 优化：多查询融合、问题分解、Step-Back、HyDE、混合检索、路由、自查询、MultiVector、父文档、RAPTOR、ReRank |

## 运行方式

依赖已在项目根的 `requirements.txt` 中声明，先激活虚拟环境：

```bash
# 脚本内使用了 "./xxx" 相对路径时，需要先切到该讲的目录
cd "study/28-Document 组件与文档加载器组件的使用"
python "1.Document与TextLoader.py"
```

配置项（OpenAI / Weaviate / LangSmith）统一从项目根的 `.env` 读取，
`dotenv.load_dotenv()` 会自上而下查找，因此在任意子目录执行都能读到。

## 关于第三方凭据

原课程代码中存在硬编码的密钥与主机地址，本仓库已全部改为从环境变量读取
（`WEAVIATE_CLUSTER_URL` / `WEAVIATE_API_KEY` / `WEAVIATE_HOST` 等）。
部分示例需要自行申请账号（Pinecone、腾讯云向量库、百度千帆、Cohere），
未配置时该讲的脚本无法运行，但不影响平台主体和其他讲次。
