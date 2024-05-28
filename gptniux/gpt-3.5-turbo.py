from openai import OpenAI

client = OpenAI(
    api_key="key",
    base_url='https://api.gptniux.com/v1'
)

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "你是一个中译英助手，我输入中文，你返回其对应的英文"},
        {"role": "user", "content": "中文：两个黄鹂鸣翠柳 英文："}
    ]
)

# 获取生成的文本内容
txt_content = str(completion.choices[0].message.content)
print(txt_content)
