import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_core.runnables import RunnablePassthrough

dotenv.load_dotenv()

def retrieval(query: str) -> str:
    """一个模拟的检索器函数"""
    print("正在检索：", query)
    return "我是穆小可"

# 1.编排prompt
prompt = ChatPromptTemplate.from_template("""请根据用户的问题回答，可以参考对用的上下文进行生成

<context>
{context}
</context>
用户的提问是：{query}""")

# 2.构建大语言模型
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

# 3.创建输出解析器
parser = StrOutputParser()

# 4.构建链
chain = RunnableParallel({
    "context": lambda x: retrieval(x["query"]),
    "query": RunnablePassthrough(),
}) | prompt | llm | parser

# 5.调用链
content = chain.invoke({"query":"你好，我是谁？"})