import os
import json
import pickle
import networkx as nx
import chromadb
from chromadb.utils import embedding_functions

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
GRAPH_PATH = os.path.join(DATA_DIR, "knowledge_graph.gpickle")

def build_vector_index(reset=False):
    print("Building Vector Index...")
    client = chromadb.PersistentClient(path=DB_DIR)
    
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    if reset:
        try:
            client.delete_collection("manual_docs")
            print("Deleted existing collection.")
        except ValueError:
            pass # Collection didn't exist

    collection = client.get_or_create_collection(
        name="manual_docs",
        embedding_function=embedding_func
    )
    
    # Check if empty to avoid re-adding unless reset
    if collection.count() > 0 and not reset:
        print("Vector DB already populated.")
        return

    # Target C-Class Manual specifically
    target_pdf = "mercedes-c-class-saloon-2025-october-w206-mbux-owners-manual-1.pdf"
    pdf_path = os.path.join(DATA_DIR, target_pdf)
    
    if os.path.exists(pdf_path):
        import pypdf
        print(f"Targeting PDF: {target_pdf}")
        try:
            reader = pypdf.PdfReader(pdf_path)
            total_pages = len(reader.pages)
            print(f"Total Pages: {total_pages}")
            
            batch_size = 50
            current_batch = []
            current_ids = []
            current_metadatas = []
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    current_batch.append(text)
                    current_ids.append(f"doc_{i}")
                    current_metadatas.append({"source": target_pdf, "page": i})
                
                # Process batch
                if len(current_batch) >= batch_size or i == total_pages - 1:
                    print(f"Ingesting batch: Pages {i - len(current_batch) + 1} to {i}...")
                    collection.add(
                        documents=current_batch,
                        ids=current_ids,
                        metadatas=current_metadatas
                    )
                    # Clear memory
                    current_batch = []
                    current_ids = []
                    current_metadatas = []
            
            print(f"Successfully ingested C-Class Manual.")
            return

        except Exception as e:
            print(f"[Error] Failed to process {target_pdf}: {e}")
    else:
        print(f"[Error] Target PDF not found: {target_pdf}")

    # Fallback logic removed as we are strictly following user request for C-Class
    if collection.count() == 0:
         print("[Warning] No documents in Vector DB.")

def build_graph_index():
    print("Building Knowledge Graph...")
    with open(os.path.join(DATA_DIR, "knowledge_graph.json"), "r") as f:
        data = json.load(f)
    
    G = nx.DiGraph()
    
    for rel in data["relationships"]:
        source = rel["source"]
        target = rel["target"]
        relation = rel["relation"]
        G.add_edge(source, target, relation=relation)
    
    # Save graph
    with open(GRAPH_PATH, "wb") as f:
        pickle.dump(G, f)
    
    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    print(f"Graph saved to {GRAPH_PATH}")

if __name__ == "__main__":
    build_vector_index()
    build_graph_index()
