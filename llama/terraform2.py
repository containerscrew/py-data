import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain import hub
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# terrafolder_dir = os.path.join(os.getcwd(), "terraform")
# loader = DirectoryLoader(terrafolder_dir, glob="**/*.tf")
# configs = loader.load()
# print(len(configs))

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0, length_function = len)
# all_splits = text_splitter.split_documents(configs)

# vectorstore = Chroma.from_documents(
#     documents=all_splits,
#     embedding=OllamaEmbeddings(model="llama3.1", show_progress=True),
#     persist_directory="./chroma_db",
# )

# loading the vectorstore
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=OllamaEmbeddings(model="llama3.1"))

# loading the Llama3 model
llm = Ollama(model="llama3.1")

# using the vectorstore as the retriever
retriever = vectorstore.as_retriever()

# formating the docs
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# loading the QA chain from langchain hub
rag_prompt = hub.pull("rlm/rag-prompt")

# creating the QA chain
qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

# running the QA chain in a loop until the user types "exit"
while True:
    question = input("Question: ")
    if question.lower() == "exit":
        break
    answer = qa_chain.invoke(question)

    print(f"\nAnswer: {answer}\n")