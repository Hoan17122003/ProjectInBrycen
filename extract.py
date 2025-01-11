import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.graphs.graph_document import Node, Relationship
from config import CONFIG
import time 
import pandas as pd
import pickle
import shutil
import json 
from prompt import CYPHER_GENERATION_PROMPT
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain, construct_schema


def extract_graph_and_chunk(path):
    '''
    Trích xuất thông tin từ file pdf và lưu vào file csv và pkl
    1. Chia file pdf thành các chunk
    2. Embed các chunk (tùy chọn, không cần cũng được)
    3. Trích xuất các entity và relationship từ các chunk bằng LLM (convert_to_graph_documents)
    4. Lưu các node và relationship vào file pkl, chunks vào file csv
    5. Trả về True nếu thành công, False nếu không thành công
    '''
    try :
        docs = PyPDFLoader(file_path=path).load() # đọc file pdf
        chunks = CONFIG.text_splitter.split_documents(docs) # chia file pdf thành các chunk
        data_chunk = []
        data_node = []
        for chunk in chunks:
            filename = os.path.basename(chunk.metadata["source"])
            chunk_id = f"{filename}.{chunk.metadata['page']}"
            print("Processing -", chunk_id)
            # Embed the chunk
            chunk_embedding = CONFIG.embedding_provider.embed_query(chunk.page_content) # embed các chunk
            # Add the Document and Chunk nodes to the graph
            properties = {
                "filename": filename,
                "chunk_id": chunk_id,
                "text": chunk.page_content,
                "embedding": chunk_embedding
            }

            data_chunk.append(properties) # lưu thông tin chunk vào list

            graph_docs = CONFIG.doc_transformer.convert_to_graph_documents([chunk]) # trích xuất entity và relationship từ chunk
            for graph_doc in graph_docs:
                chunk_node = Node(
                    id=chunk_id,
                    type="Chunk"
                )
                for node in graph_doc.nodes:

                    graph_doc.relationships.append(
                        Relationship(
                            source=chunk_node,
                            target=node, 
                            type="HAS_ENTITY"
                            )
                        ) # thêm relationship giữa chunk và entity ( đây là thêm để giàu thông tin, thực tế đã có relationship khác)
            data_node += graph_docs # lưu các node và relationship vào list
        # Lưu list vào file
        filename =  os.path.basename(path)
        path = Path(path)
        filename = path.stem
        print(filename)
        outdir = os.path.join(CONFIG.output_db, filename)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        with open(os.path.join(outdir, "graph.pkl"), "wb") as f: # lưu graph vào file
            pickle.dump(data_node, f)

        df = pd.DataFrame(data_chunk)
        df.to_csv(os.path.join(outdir,"chunks.csv" ), index=False) # lưu thông tin chunk vào file csv
        return True

    except Exception as e:  
        print(e)
        return False
    

def read_file(name):
    '''
    Đọc thông tin từ file csv và pkl'''

    path = os.path.join(CONFIG.output_db,name)

    chunks = pd.read_csv(os.path.join(path,"chunks.csv")) # đọc thông tin chunk từ file csv
    with open(os.path.join(path,'graph.pkl'), "rb") as f: # đọc thông tin graph từ file pkl
        graph_db = pickle.load(f)

    return chunks, graph_db


def reload_neo4j(name):

    '''
    Load thông tin từ file csv và pkl vào neo4j
    1. Xóa thông tin cũ
    2. Load thông tin mới
    3. Thêm thông tin vào neo4j
    
    '''
    CONFIG.graph.query("MATCH (n) DETACH DELETE n") # xóa thông tin cũ
    chunks, graph_db = read_file(name) # đọc thông tin từ file csv và pkl
    for index, row in chunks.iterrows():

        filename = row['filename']
        chunk_id = row['chunk_id']
        text = row['text']
        # embedding = row['embedding']

        properties = {
            "filename": filename,
            "chunk_id": chunk_id,
            "text": text,
            "embedding":None# json.loads(embedding)
        }
        # print(properties)
        CONFIG.graph.query("""
            MERGE (d:Document {id: $filename})
            MERGE (c:Chunk {id: $chunk_id})
            SET c.text = $text
            MERGE (d)<-[:PART_OF]-(c)
            """, 
            properties
        ) # dùng cypher để thêm thông tin chunks vào neo4j, vì không dùng embedding để tìm nên anh không đưa thêm thông tin embedding
            # WITH c
            # CALL db.create.setNodeVectorProperty(c, 'textEmbedding', $embedding)
            # """, 
        #     properties
        # )

    CONFIG.graph.add_graph_documents(graph_db) # thêm thông tin graph vào neo4j ,  đọc kỹ bên trong thì nó cũng cùng cypher thôi
 
    CONFIG.graph.refresh_schema() # refresh lại schema cho chắc ăn, đảm bảo thông tin đã update s


def bot_response(user_input):
    '''
    Truy vấn Neo4j và trả lời câu hỏi của người dùng
    Lưu ý: a có đổi prompt, nếu dùng propmt mặc định thì để cypher_prompt = None
    '''

    chain = GraphCypherQAChain.from_llm(graph=CONFIG.graph, llm=CONFIG.llm, verbose=True, allow_dangerous_requests = True, enhanced_schema=True, cypher_prompt=CYPHER_GENERATION_PROMPT)
    response = chain.invoke({"query": user_input})

    return response['result']

def del_db(name):
    '''
    Xóa thông tin của file đã tải
    '''
    path = os.path.join(CONFIG.output_db,name)
    if os.path.exists(path):
        shutil.rmtree(path)
        return True
    