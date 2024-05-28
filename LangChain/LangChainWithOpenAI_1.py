import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# 预先声明splitter和embedding engine
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
embeddings = OpenAIEmbeddings(api_key="key",
                              base_url='https://api.gptniux.com/v1')


# 获取../data目录中的所有.txt文件
txt_files = [f for f in os.listdir('../HarmonyOS/GuidePolymerize') if f.endswith('.txt')]
print(len(txt_files))
count = 0
# 将每个.txt文件加载到数据库中
for txt_file in txt_files:
    count += 1

    loader = TextLoader(os.path.join('../HarmonyOS/GuidePolymerize', txt_file), encoding='utf-8')
    documents = loader.load()
    print('加载了第', count, '个文件')

    texts = text_splitter.split_documents(documents)
    print('分割了第', count, '个文件')

    db = Chroma.from_documents(texts, embeddings)
    print('嵌入了第', count, '个文件')

    print('完成了', count, '个文件')

print("所有在../dataPolymerize目录中的.txt文件已成功加载到数据库中。")

retriever = db.as_retriever()

docs = retriever.get_relevant_documents("监听麦克风状态变化")

print("\n\n".join([x.page_content[:300] for x in docs[:3]]))
