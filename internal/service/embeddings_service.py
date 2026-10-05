import os
from dataclasses import dataclass

import tiktoken
from injector import inject
from langchain.embeddings import CacheBackedEmbeddings
from langchain_community.storage import RedisStore
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from redis import Redis


@inject
@dataclass
class EmbeddingsService:
    """文本嵌入模型服务"""
    _store: RedisStore
    _embeddings: Embeddings
    _cache_backed_embeddings: CacheBackedEmbeddings

    def __init__(self, redis: Redis):
        """构造函数，初始化文本嵌入模型客户端、存储器、缓存客户端"""
        self._store = RedisStore(client=redis)
        # 老师原版用的是本地 HuggingFace 模型（nomic-embed-text-v1.5）。
        # 这里改用 OpenAI 的嵌入接口，原因：
        #   1) langchain-huggingface 会把 langchain-core 升到 1.x，和本项目锁定的
        #      0.2.x 不兼容（0.2 的 langchain_core.pydantic_v1 在 1.x 里被删了）
        #   2) 本地模型要下载约 2GB 权重
        # 将来要上本地模型（数据不能出内网的场景），需要把整套 LangChain 一起升级。
        self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        # self._embeddings = HuggingFaceEmbeddings(
        #     model_name="nomic-ai/nomic-embed-text-v1.5",
        #     cache_folder=os.path.join(os.getcwd(), "internal", "core", "embeddings"),
        #     model_kwargs={"trust_remote_code": True},
        # )
        self._cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
            self._embeddings,
            self._store,
            namespace="embeddings",
        )

    @classmethod
    def calculate_token_count(cls, query: str) -> int:
        """计算传入文本的token数"""
        # 注意：encoding_name_for_model() 返回的是编码「名字」（字符串），
        # 要拿编码器对象必须用 encoding_for_model()，否则这里调的是 str.encode()，
        # 会把 query 当成编码名传进去，运行时报 LookupError。
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(query))

    @property
    def store(self) -> RedisStore:
        return self._store

    @property
    def embeddings(self) -> Embeddings:
        return self._embeddings

    @property
    def cache_backed_embeddings(self) -> CacheBackedEmbeddings:
        return self._cache_backed_embeddings
