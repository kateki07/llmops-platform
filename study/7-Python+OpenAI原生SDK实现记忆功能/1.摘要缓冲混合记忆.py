import os

import dotenv
import tiktoken
from openai import OpenAI

dotenv.load_dotenv()

# 1.创建openai客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ConversationSummaryBufferMemory:
    """摘要缓冲混合记忆类"""
 
    def __init__(self, summary: str = "", chat_histories: list = None, max_tokens: int = 300):
        # 1.max_tokens用于判断是否需要生成新的摘要
        self.max_tokens = max_tokens
        # 2.summary用于存储摘要的信息
        self.summary = summary
        # 3.chat_histories用于存储历史对话
        self.chat_histories = [] if chat_histories is None else chat_histories

    @classmethod
    def get_num_tokens(cls, query: str) -> int:
        """4.计算传入文本的token数"""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(query))

    def save_context(self, human_query: str, ai_content: str) -> None:
        """5.存储新的交流对话"""
        self.chat_histories.append({"human": human_query, "ai": ai_content})

        # 历史对话没超过上限就不用动
        buffer_string = self.get_buffer_string()
        tokens = self.get_num_tokens(buffer_string)
        if tokens <= self.max_tokens:
            return

        # 超了：把最老的一轮对话压缩进摘要，然后从历史里删掉
        first_chat = self.chat_histories[0]
        print("\n[生成新摘要中……]")
        self.summary = self.summary_text(
            self.summary,
            f"Human:{first_chat.get('human')}\nAI:{first_chat.get('ai')}",
        )
        print(f"[新摘要] {self.summary}\n")
        del self.chat_histories[0]

    def get_buffer_string(self) -> str:
        """6.将历史对话转换成字符串"""
        buffer: str = ""
        for chat in self.chat_histories:
            buffer += f"Human:{chat.get('human')}\nAI:{chat.get('ai')}\n\n"
        return buffer.strip()

    def load_memory_variables(self) -> dict:
        """7.加载记忆变量信息"""
        buffer_string = self.get_buffer_string()
        return {
            "chat_history": f"{self.summary}\n\n{buffer_string}",
        }

    def summary_text(self, origin_summary: str, new_line: str) -> str:
        """8.将旧的摘要和传入的对话生成新摘要"""
        prompt = f"""你是一个强大的聊天机器人，请根据用户提供的谈话内容，总结内容，并将其添加到先前提供的摘要中，返回一个新的摘要，除了新摘要意外，不要返回任何内容。

<example>
当前摘要: 人类会问人工智能对人工智能的看法。人工智能认为人工智能是一股向善的力量。

新的谈话内容:
Human: 为什么你认为人工智能是一股向善的力量?
AI: 因为人工智能将帮助人类充分发挥潜力。

新摘要: 人类会问人工智能对人工智能的看法。人工智能认为人工智能是一股向善的力量，因为它将帮助人类充分发挥潜力。
</example>

=====================以下是一次实际的操作案例=====================

当前摘要: {origin_summary}

新的谈话内容:
{new_line}

请帮我生成新摘要："""
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content


# 2.创建记忆实例
memory = ConversationSummaryBufferMemory("", [], 300)

# 3.创建一个死循环用于人机对话
while True:
    # 4.获取人类的输入
    query = input('Human: ')

    # 5.判断下输入是否为q，如果是则退出
    if query == 'q':
        break

    # 6.把记忆（摘要 + 最近的对话）拼进提示词
    memory_variables = memory.load_memory_variables()
    answer_prompt = (
        "以下是一段AI与人类的对话，其中<histories>标签里是历史对话，"
        "请根据历史对话回答用户的问题。\n\n"
        f"<histories>\n{memory_variables.get('chat_history')}\n</histories>\n\n"
        f"用户的提问是：{query}"
    )

    # 7.向openai的接口发起请求获取ai生成的内容
    response = client.chat.completions.create(
        model='gpt-4-turbo',
        messages=[
            {"role": "user", "content": answer_prompt},
        ],
        stream=True,
    )

    # 8.循环读取流式响应的内容
    print("AI: ", flush=True, end="")
    ai_content = ""
    for chunk in response:
        content = chunk.choices[0].delta.content or ""
        ai_content += content
        print(content, flush=True, end="")
    print("")

    # 9.把这一轮对话存进记忆
    memory.save_context(query, ai_content)
