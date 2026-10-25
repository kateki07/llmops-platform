"""重建辅助 Agent 的 FAISS 本地索引。

首页右下角那个「辅助 Agent」用一个本地 FAISS 向量库来检索项目的 API 文档。
`FaissService` 在应用启动时就会 `FAISS.load_local(...)`，所以
`internal/core/vector_store/` 下的 index.faiss + index.pkl 是跑起来的必需品。

什么时候要跑这个脚本：
  · 改了 storage/vector_store/ 下的源文档
  · 换了嵌入模型（索引的维度会跟着变，旧索引直接用不了）
  · 从零 clone 下来、索引文件丢了

用法（在 llmops-api 目录下，激活虚拟环境后）：

    python scripts/build_assistant_index.py

会调用 OpenAI 的嵌入接口，成本很低（text-embedding-3-small，
一份 200KB 左右的文档大约几分钱人民币以内）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import UnstructuredMarkdownLoader  # noqa: E402
from langchain_community.vectorstores import FAISS  # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter  # noqa: E402

from app.http.app import app  # noqa: E402
from app.http.module import injector  # noqa: E402
from internal.service import EmbeddingsService  # noqa: E402

SOURCE_DIR = os.path.join("storage", "vector_store")
TARGET_DIR = os.path.join("internal", "core", "vector_store")


def main() -> int:
    if not os.path.isdir(SOURCE_DIR):
        print(f"错误：找不到源文档目录 {SOURCE_DIR}")
        return 1

    sources = [
        os.path.join(SOURCE_DIR, f)
        for f in sorted(os.listdir(SOURCE_DIR))
        if f.lower().endswith((".md", ".markdown", ".txt"))
    ]
    if not sources:
        print(f"错误：{SOURCE_DIR} 下没有可用的源文档")
        return 1

    with app.app_context():
        # 1.加载源文档
        documents = []
        for path in sources:
            documents.extend(UnstructuredMarkdownLoader(path).load())
            print(f"  已加载 {path}")

        # 2.切分。参数对齐项目里知识库的默认分段规则（见 internal/entity/dataset_entity.py），
        #   add_start_index 让每个片段记住它在原文里的偏移，便于回溯
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            add_start_index=True,
        )
        chunks = splitter.split_documents(documents)
        print(f"  切分出 {len(chunks)} 个片段")

        # 3.用项目自己的嵌入服务，保证和 FaissService 加载时用的是同一个模型
        #   （模型不一致的话维度对不上，load_local 出来的结果是乱的）
        embeddings_service = injector.get(EmbeddingsService)
        print(f"  正在调用嵌入接口……（{len(chunks)} 个片段）")
        store = FAISS.from_documents(chunks, embeddings_service.embeddings)

        # 4.落盘
        os.makedirs(TARGET_DIR, exist_ok=True)
        store.save_local(TARGET_DIR)
        print(f"\n完成，索引已写入 {TARGET_DIR}")
        print(f"  向量数：{store.index.ntotal} ｜ 维度：{store.index.d}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
