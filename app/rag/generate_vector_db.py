import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

file_path = "data_source/bus_booking_policy.pdf"
loader = PyMuPDFLoader(file_path,mode="page")

docs = loader.load()
#print(len(docs)) #prints total number of documents of PDF
#print(docs[3].page_content) #prints content of particular page

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,  # chunk size (characters)
    chunk_overlap=100,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)
#print(all_splits)

embeddings = OpenAIEmbeddings()

# SAVE VECTOR DATA TO LOCAL DISK - ONE TIME
# vector_data = FAISS.from_documents(all_splits,embeddings)
# file_path = "vector_db/bus_booking_policy"
# vector_data.save_local(file_path)

# LOAD VECTOR DATA FROM SAVED DATA ON DISK
vector_data = FAISS.load_local("vector_db/bus_booking_policy",embeddings,allow_dangerous_deserialization=True)
retriever = vector_data.as_retriever(search_type="similarity",search_kwargs={"k": 2},)
query = "what is refund policy"
docs = vector_data.similarity_search(query)
print(docs[0].page_content)