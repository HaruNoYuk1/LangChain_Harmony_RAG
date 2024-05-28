import base64
import os
import sys

from langchain.chains import TransformChain
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

img_path = "image/test11.jpg"
ocr_img_path = '/' + img_path


# 加载并对图片进行Base64编码的函数
def load_image(inputs: dict) -> dict:
    image_path = inputs["image_path"]
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    return {"image": image_base64}


# 配置用于加载和编码图片的转换链
load_image_chain = TransformChain(
    input_variables=["image_path"],
    output_variables=["image"],
    transform=load_image
)


# 修改generate_harmonyos_code函数，以接受OCR文本作为附加参数
@chain
def generate_harmonyos_module_with_ocr(inputs: dict) -> dict:
    model = ChatOpenAI(temperature=0.2, max_tokens=1024, model="gpt-4o",
                       api_key="key",
                       base_url='https://api.gptniux.com/v1')
    msg = model.invoke([HumanMessage(content=[
        {"type": "text", "text": inputs["prompt"]},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{inputs['image']}"}},
        {"type": "text", "text": inputs["ocr_text"]}
    ])])
    return msg.content


# 使用现有的加载图像链并集成OCR文本的函数
def get_module_with_ocr(image_path: str, ocr_text: str) -> dict:
    code_prompt_with_ocr = """
    以下图片是一个APP页面，并附带OCR识别文本。请你参考OCR识别文本识别的的内容。
    生成在鸿蒙系统中这个界面有哪些模块和功能，不用给出代码。
    """
    code_chain_with_ocr = load_image_chain | generate_harmonyos_module_with_ocr
    return code_chain_with_ocr.invoke({'image_path': image_path, 'prompt': code_prompt_with_ocr, 'ocr_text': ocr_text})


from OCR.RapidOCR_api import OcrAPI

imgPath = os.getcwd() + ocr_img_path
ocrPath = os.getcwd() + r"\OCR\RapidOCR-json\RapidOCR-json.exe"

if not os.path.exists(ocrPath):
    print(f"未在以下路径找到引擎！\n{ocrPath}")
    sys.exit()

ocr = OcrAPI(ocrPath)
# OCR初始化完毕，开始识别图片中的文字
print("OCR初始化完毕，开始路径识图。")
imageOCR = ocr.run(imgPath)
ocr.printResult(imageOCR)


# 从OCR JSON中提取文本的函数
def extract_ocr_text(ocr_json):
    text_lines = [item['text'] for item in ocr_json['data']]
    full_text = '\n'.join(text_lines)
    return "OCR:\n" + full_text


# 使用这个函数来转换你的OCR数据
ocr_text = extract_ocr_text(imageOCR)

result1 = get_module_with_ocr(img_path, ocr_text)
print(result1)

# 创建嵌入引擎
embeddings = OpenAIEmbeddings(api_key="key",
                              base_url='https://api.gptniux.com/v1')
persist_directory = 'docs/chroma/'
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# 使用数据库进行文档检索
retriever = vectordb.as_retriever()

# 分割result1为单独的模块描述
modules = result1.split('\n')

# 使用检索器查找每个模块的相关代码
contexts = []
for module in modules:
    context = retriever.invoke(module)[0]
    if isinstance(context, list):
        context = context[0] if context else ""
    elif isinstance(context, dict):
        context = context.get('some_key', "")
    context = str(context)
    contexts.append(context)

# 将所有检索到的上下文合并成一个字符串
combined_contexts = '\n'.join(contexts)
print("检索器检索完毕")


@chain
def generate_harmonyos_code_final(inputs: dict) -> dict:
    model = ChatOpenAI(temperature=0.3, max_tokens=2048, model="gpt-4o",
                       api_key="key",
                       base_url='https://api.gptniux.com/v1')
    prompt = f"""
    请你使用以下检索到的上下文片段作为参考，对于输入的图片和参考代码，来生成实现这个图片效果的鸿蒙代码。
    生成的内容需要覆盖到实现图片效果的每一个组件，每个组件的布局都需要给出其详细代码实现（不能只给一个框架模板），并给代码附上必要的注释。
    参考代码: {inputs['combined_contexts']}
    这些代码是通过之前的回答对于输入的图片检索得到的模块在代码库中进行匹配得到的，你在实现图片效果的鸿蒙代码时可以参考这些代码。
    注意生成代码时需要去掉首部的CopyRight声明
    """
    msg = model.invoke([
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{inputs['image']}"}}
            ]
        )
    ])
    return msg.content


def get_final_harmonyos_code(image_path: str, combined_contexts: str) -> dict:
    final_code_chain = load_image_chain | generate_harmonyos_code_final
    return final_code_chain.invoke({'image_path': image_path, 'combined_contexts': combined_contexts})


result2 = get_final_harmonyos_code(img_path, combined_contexts)
print('result2:', result2)


# 定义额外的步骤来使用result2和图片生成最终代码result3
@chain
def generate_final_code_with_enhancement(inputs: dict) -> dict:
    model = ChatOpenAI(temperature=0.3, max_tokens=2048, model="gpt-4o",
                       api_key="key",
                       base_url='https://api.gptniux.com/v1')
    prompt = f"""
    请你根据以下代码和图片，完善这段代码内容，使其运行起来效果能够最大程度的还原图片，如果模块内容有缺失的，补充完成没有完成的模块。
    代码: {inputs['result2']}
    """
    msg = model.invoke([
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{inputs['image']}"}}
            ]
        )
    ])
    return msg.content


def get_final_code_enhanced(image_path: str, result2: str) -> dict:
    enhanced_code_chain = load_image_chain | generate_final_code_with_enhancement
    return enhanced_code_chain.invoke({'image_path': image_path, 'result2': result2})


result3 = get_final_code_enhanced(img_path, result2)
print('result3:', result3)

# 保存最终生成的内容到文件
if not os.path.exists('response/image'):
    os.makedirs('response/image')

file_path = os.getcwd() + f"/response/{img_path.split('.')[0]}_v2.txt"

with open(file_path, "w", encoding="utf-8") as file:
    file.write(result3)
