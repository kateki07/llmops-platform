from datetime import datetime

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.编排 prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请回答用户的问题，现在的时间是{now}"),
    ("human", "{query}"),
]).partial(now=datetime.now())

# 2.创建大语言模型
llm = ChatOpenAI(model="gpt-3.5-turbo")

ai_message = llm.batch([
    prompt.invoke({"query": "你好，你是？"}),
    prompt.invoke({"query": "请讲一个关于程序员的冷笑话"})
])

for ai_message in ai_message: 
    print(ai_message.content)
    print("===============================")
