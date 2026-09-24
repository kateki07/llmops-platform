import os

import weaviate
from injector import inject
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate import WeaviateClient


@inject
class VectorDatabaseService:
    """向量数据库服务

    这个类把「连 Weaviate」+「包成 LangChain 的向量存储」这两件事封装起来，
    上层（handler）只管拿检索器，不用关心底层用的是哪个向量库。
    """

    client: WeaviateClient
    vector_store: WeaviateVectorStore

    def __init__(self):
        """构造函数：建立向量数据库客户端 + LangChain 向量存储实例"""
        # 1.连接本地 Weaviate（Docker 起的那个）
        self.client = weaviate.connect_to_local(
            host=os.getenv("WEAVIATE_HOST"),
            port=int(os.getenv("WEAVIATE_PORT")),
        )

        # 2.包一层 LangChain 的向量存储
        #   index_name  = Weaviate 里的类名（相当于表名），首字母必须大写
        #   text_key    = 原文存在哪个字段里
        #   embedding   = 用哪个模型把文字转成向量
        self.vector_store = WeaviateVectorStore(
            client=self.client,
            index_name="Dataset",
            text_key="text",
            embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        )

    def get_retriever(self) -> VectorStoreRetriever:
        """获取检索器（把向量存储变成一个可以放进 LCEL 链里的 Runnable）"""
        return self.vector_store.as_retriever()

    @classmethod
    def combine_documents(cls, documents: list[Document]) -> str:
        """把检索回来的文档列表合并成一段纯文本，好塞进提示词的 {context}"""
        return "\n\n".join([document.page_content for document in documents])
