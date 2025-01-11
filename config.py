import os
from langchain_google_genai import GoogleGenerativeAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.graphs import Neo4jGraph

class CONFIG:

    '''
    Cấu hình LLM chat và LLM Embedding
    Google API Key thì em đổi thành key của e cho khỏi xung đột bên a'''
    GOOGLE_API_KEY = "AIzaSyApkMLVWNXnM-fr9EjbTUCqpGRo27TfrMY"
    llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
    embedding_provider =GoogleGenerativeAIEmbeddings(google_api_key=GOOGLE_API_KEY, model="models/text-embedding-004")

    doc_transformer = LLMGraphTransformer(
        llm=llm,
        ) # transformer để chuyển đổi text thành graph của lang chain

    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1500,
        chunk_overlap=200,
    ) # trình chia text để chia file pdf thành các chunk

    graph = Neo4jGraph(
        url="bolt://localhost:7687",
        username="neo4j",
        password="123456789"
    ) # cấu hình neo4j

    output_db = "./DB" # thư mục lưu trữ các file pdf, chunk và graph đã được xử lý

    pdfs= {}

    for pdf_dir in os.listdir(output_db):
        if os.path.exists(os.path.join(output_db,pdf_dir ,pdf_dir+".pdf")) \
        and os.path.exists(os.path.join(output_db,pdf_dir ,"chunks.csv")) \
        and os.path.exists(os.path.join(output_db,pdf_dir ,"graph.pkl")):
            pdfs[pdf_dir+".pdf"] = True
