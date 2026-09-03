from langchain_core.prompts import PromptTemplate, PipelinePromptTemplate

full_template = PromptTemplate.from_template(
    """
    {instruction}
    {example}
    {start}
    """
)
# 描述模板
Instruction_prompt = PromptTemplate.from_template("你正在模拟{person}")

# 示例模板
example_prompt = PromptTemplate.from_template(
    """
    下面是一个交互例子：
    Q: {example_q}
    A: {example_a}
    """
)

# 开始模板
start_prompt = PromptTemplate.from_template(
    """
    现在，你是一个真实的人，请回答用户问题：
    Q: {input}
    A: 
    """
    )
pipeline_prompts = [
    ("instruction", Instruction_prompt),
    ("example", example_prompt),
    ("start", start_prompt)
]

pipeline_prompt = PipelinePromptTemplate(
    final_prompt=full_template,
    pipeline_prompts=pipeline_prompts,
)

print(pipeline_prompt.invoke({
    "person": "乔布斯",
    "example_q": "你最喜欢的手机是什么？",
    "example_a": "苹果手机",
    "input": "你最喜欢的汽车是什么？"
}).to_string())