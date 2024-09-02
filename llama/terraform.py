import os
import logging
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain import hub
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global configuration
MODEL_NAME = "llama3.1"
CHUNK_SIZE = 600
CHROMA_DB_DIR = "./chroma_db"
TERRAFORM_DIR = "terraform"

def get_terraform_files(terrafolder_dir):
    """Load Terraform files from the specified directory."""
    logging.info(f"Loading documents from {terrafolder_dir}...")
    loader = DirectoryLoader(terrafolder_dir, glob="**/*.tf")
    documents = loader.load()
    if not documents:
        raise ValueError("No documents found in the specified folder.")
    logging.info(f"{len(documents)} documents loaded.")
    return documents

def split_documents(documents, chunk_size):
    """Split documents into smaller chunks."""
    logging.info(f"Splitting documents into chunks of {chunk_size} characters...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
    all_splits = text_splitter.split_documents(documents)
    if not all_splits:
        raise ValueError("Failed to split the documents into chunks.")
    logging.info(f"Documents split into {len(all_splits)} chunks.")
    return all_splits

def create_vectorstore(splits, model_name, persist_directory):
    """Create and persist the vector store using the document splits."""
    logging.info(f"Creating vector store and saving it to {persist_directory}...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OllamaEmbeddings(model=model_name, show_progress=True),
        persist_directory=persist_directory,
    )
    if vectorstore._collection.count() == 0:
        raise ValueError("Failed to store the documents in the vector store.")
    logging.info("Vector store created and documents stored successfully.")
    return vectorstore

def load_vectorstore(persist_directory, model_name):
    """Load an existing vector store."""
    logging.info(f"Loading vector store from {persist_directory}...")
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=OllamaEmbeddings(model=model_name))
    return vectorstore

def create_qa_chain(retriever, model_name):
    """Create the QA chain using the retriever and model."""
    logging.info("Creating the question-answering chain...")
    rag_prompt = hub.pull("rlm/rag-prompt")
    llm = Ollama(model=model_name)
    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    logging.info("Question-answering chain created successfully.")
    return qa_chain

def format_docs(docs):
    """Format documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def run_qa_loop(qa_chain):
    """Run the QA loop to interact with the user."""
    while True:
        question = input("Question: ")
        if question.lower() == "exit":
            logging.info("Exiting the program...")
            break
        try:
            answer = qa_chain.invoke(question)  # Ask the QA chain
            print(f"\nAnswer: {answer}\n")
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

def main():
    # Get the absolute path of the 'terraform' folder from the current directory
    terrafolder_dir = os.path.join(os.getcwd(), TERRAFORM_DIR)

    # Load and process documents
    documents = get_terraform_files(terrafolder_dir)
    splits = split_documents(documents, CHUNK_SIZE)
    
    # Create or load the vector store
    if not os.path.exists(CHROMA_DB_DIR):
        vectorstore = create_vectorstore(splits, MODEL_NAME, CHROMA_DB_DIR)
    else:
        vectorstore = load_vectorstore(CHROMA_DB_DIR, MODEL_NAME)
    
    # Create the QA chain
    retriever = vectorstore.as_retriever()
    qa_chain = create_qa_chain(retriever, MODEL_NAME)
    
    # Run the question-answering loop
    run_qa_loop(qa_chain)

if __name__ == "__main__":
    main()
