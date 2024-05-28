from openai import OpenAI

client = OpenAI(
    api_key="key",
    base_url='https://api.gptniux.com/v1'
)

completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": "你帮我写一下"},
        {"role": "user", "content": "中文：借问酒家何处有？牧童遥指杏花村。 英文："}
    ]
)

# 获取生成的文本内容
txt_content = str(completion.choices[0].message.content)
print(txt_content)
# 将内容写入.txt文件
with open("../generated_code_gpt-4-1106-preview.txt", "w", encoding="utf-8") as f:
    f.write(txt_content)

print("gpt-4-1106-preview文本文件已保存在当前目录下的 generated_code_gpt-4-1106-preview.txt 文件中")
