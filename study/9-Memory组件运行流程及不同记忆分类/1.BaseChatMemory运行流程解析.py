from langchain.memory.chat_memory import BaseChatMemory

# BaseChatMemory 是所有「对话型记忆」的基类，运行流程固定为三步：
#   ① load_memory_variables()  取出记忆，塞进 prompt
#   ② chain.invoke(...)        调用链得到回复
#   ③ save_context(输入, 输出)  把这一轮存回记忆
memory = BaseChatMemory(
    input_key="query",
    output_key="output",
    return_messages=True,
)

# ① 第一次取记忆：还是空的
memory_variable = memory.load_memory_variables({})
print("第一次:", memory_variable)

# ② 假设这里调用了链，得到了回复
# content = chain.invoke({"query": "你好，我是慕小课你是谁", "chat_history": memory_variable.get("history")})

# ③ 把这一轮对话存回记忆
memory.save_context(
    {"query": "你好，我是慕小课你是谁"},
    {"output": "你好，我是ChatGPT，有什么可以帮到您的"},
)

# 再取一次：已经有内容了
memory_variable = memory.load_memory_variables({})
print("第二次:", memory_variable)
