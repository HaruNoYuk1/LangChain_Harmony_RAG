import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# 创建嵌入引擎
embeddings = OpenAIEmbeddings(api_key="",
                              base_url='https://api.gptniux.com/v1')

persist_directory = 'docs/chroma/'

if os.path.exists(persist_directory):
    # 加载现有的ChromaDB
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    print("向量数据库已加载。")
else:
    txt_files = [f for f in os.listdir('../OpenHarmony/CodeGet2') if f.endswith('.txt')]
 #   txt_files = txt_files[:10]  # 获取前十个文件
    print(f"找到 {len(txt_files)} 个文本文件。")

    documents_collection = []
    for count, txt_file in enumerate(txt_files, 1):
        loader = TextLoader(os.path.join('../OpenHarmony/CodeGet2', txt_file), encoding='utf-8')
        documents = loader.load()
        print(f'已加载文件 {count}: {txt_file}')
        documents_collection.extend(documents)

    # 从文档文本集合创建向量数据库
    vectordb = Chroma.from_documents(
        documents=documents_collection,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vectordb.persist()
    print("向量数据库已创建并保存。")

# 使用数据库进行文档检索
retriever = vectordb.as_retriever()

# 举例检索文档
query = "天气"
docs = retriever.get_relevant_documents(query)
print(docs[0].page_content)
# print("\n\n".join([x.page_content[:300] for x in docs[:3]]))
