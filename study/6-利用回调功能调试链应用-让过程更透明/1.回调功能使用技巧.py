import time
from typing import Any

import dotenv
from langchain_core.callbacks import BaseCallbackHandler, StdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class LLMOpsCallbackHandler(BaseCallbackHandler):
    """自定义 LLMOps 回调处理器

    回调 = 在链执行的关键节点上「插眼」，看清中间发生了什么。
    继承 BaseCallbackHandler 后，想监控哪个环节就重写哪个 on_xxx 方法。
    """

    def __init__(self):
        self.start_at: float = 0.0

    def on_chat_model_start(self, serialized, messages, **kwargs: Any) -> None:
        """聊天模型开始执行时触发 —— 能看到真正发给模型的消息"""
        print("=" * 50)
        print("聊天模型开始执行了")
        print("真正发给模型的消息：")
        for msg in messages[0]:
            print(f"  [{msg.type}] {msg.content}")
        self.start_at = time.time()
    
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """模型返回后触发 —— 能看到耗时和 token 消耗"""
        print("-" * 50)
        print(f"模型执行完毕，耗时 {time.time() - self.start_at:.2f} 秒")
        usage = (response.llm_output or {}).get("token_usage")
        if usage:
            print(f"token 消耗：{usage}")
        print("=" * 50)


# 1.编排 prompt
prompt = ChatPromptTemplate.from_template("""请根据用户的问题回答，可以参考对应的上下文进行生成

<context>
{context}
</context>
用户的提问是：{query}""")

# 2.构建大语言模型
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

# 3.创建输出解析器
parser = StrOutputParser()

# 4.构建链 —— prompt 需要 context 和 query 两个变量，两个都得给
chain = {
    "context": RunnablePassthrough(),
    "query": RunnablePassthrough(),
} | prompt | llm | parser

# 5.调用链，把回调处理器挂上去
resp = chain.stream(
    "你好，你是？",
    config={"callbacks": [StdOutCallbackHandler(), LLMOpsCallbackHandler()]},
)

for chunk in resp:
    pass
