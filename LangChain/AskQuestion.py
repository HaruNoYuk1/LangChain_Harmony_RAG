import base64
import os
import sys

from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from OCR.RapidOCR_api import OcrAPI

imgPath = os.getcwd() + r"\image\test10.jpg"
ocrPath = os.getcwd() + r"\OCR\RapidOCR-json\RapidOCR-json.exe"

if not os.path.exists(ocrPath):
    print(f"未在以下路径找到引擎！\n{ocrPath}")
    sys.exit()
ocr = OcrAPI(ocrPath)

# 路径识图
print("OCR初始化完毕，开始路径识图。")
imageOCR = ocr.run(imgPath)
print(imageOCR)
ocr.printResult(imageOCR)


def extract_ocr_text(ocr_json):
    text_lines = [item['text'] for item in ocr_json['data']]  # 提取每个识别项的文本
    full_text = '\n'.join(text_lines)  # 将所有文本行合并为一个字符串，每个条目之间用换行符分隔
    return "OCR:\n" + full_text


# 使用这个函数来转换你的 OCR 数据
ocr_text = extract_ocr_text(imageOCR)


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


base64_image = encode_image(imgPath)
# 创建嵌入引擎
embeddings = OpenAIEmbeddings(api_key="key",
                              base_url='https://api.gptniux.com/v1')

persist_directory = 'docs/chroma/'

vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# 使用数据库进行文档检索
retriever = vectordb.as_retriever()

from langchain.prompts import ChatPromptTemplate

template = """你是问答任务助手。使用以下检索到的上下文片段来回答问题。
我的需求是首要的，代码仅供参考，并且你在生成答案时应该去掉代码首部的Copyright声明，并给代码附上必要的注释。
context中是参考代码，OCR是对于传入图像（如果有）识别得到的图像内模块的文字。
Question: {question}
Context: {context}
Answer:
"""
prompt = ChatPromptTemplate.from_template(template)
# # 创建模型请求的负载
# messages = [
#     {
#         "role": "user",
#         "content": [
#             {
#                 "type": "text",
#                 "text": ocr_text
#             },
#             {
#                 "type": "image_url",
#                 "image_url": f"data:image/jpeg;base64,{base64_image}"
#             }
#         ]
#     }
# ]
llm = ChatOpenAI(model_name="gpt-4-vision-preview",
                 temperature=0,
                 api_key="key",
                 base_url='https://api.gptniux.com/v1'
                 )

rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

query = "生成鸿蒙系统付款界面代码"

# 提问并获取检索内容
context = retriever.invoke(query)
print(f"Question: {query}\n"
      f"Retrieved Context Size: {len(context)}\n"
      f"Retrieved Context: {context}\n"
      f"Retrieved Context【0,1】: {context[:2]}"
      )

# 生成内容

answer = rag_chain.invoke(query)

print(f"Generated Content: {answer}")

# 保存生成的内容到文件
with open(f"response/{query}.txt", "w", encoding="utf-8") as file:
    file.write(answer)
