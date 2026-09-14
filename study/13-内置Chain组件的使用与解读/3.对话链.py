import dotenv
from langchain.chains.conversation.base import ConversationChain
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

# ConversationChain 自带记忆，不用自己管 history
chain = ConversationChain(llm=llm)

content = chain.invoke({"input": "你好，我是慕小课，我喜欢打篮球还有游泳，你喜欢什么运动呢？"})
print(content)

content = chain.invoke({"input": "根据上下文信息，请统计一下我的运动爱好有什么?"})
print(content)
