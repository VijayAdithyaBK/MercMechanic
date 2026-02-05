import os
import pickle
import chromadb
from chromadb.utils import embedding_functions
import networkx as nx

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
GRAPH_PATH = os.path.join(BASE_DIR, "data", "knowledge_graph.gpickle")

class HybridRetriever:
    def __init__(self):
        print("Initializing Retriever...")
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=DB_DIR)
        self.collection = self.client.get_collection(name="manual_docs", embedding_function=self.embedding_func)
        
        with open(GRAPH_PATH, "rb") as f:
            self.graph = pickle.load(f)
            
    def get_related_nodes(self, text, depth=1):
        """
        Simple heuristic: Find graph nodes mentioned in the text strings.
        In a real app, this would use NER (Named Entity Recognition).
        """
        found_nodes = []
        text_lower = text.lower()
        
        for node in self.graph.nodes():
            if str(node).lower() in text_lower:
                found_nodes.append(node)
        
        # Traverse graph
        subgraph_nodes = set(found_nodes)
        for node in found_nodes:
            # Add neighbors
            neighbors = list(self.graph.neighbors(node))
            subgraph_nodes.update(neighbors)
            if depth > 1:
                for n in neighbors:
                    subgraph_nodes.update(list(self.graph.neighbors(n)))
                    
        return list(subgraph_nodes)

    def retrieve(self, query):
        # 1. Vector Search
        results = self.collection.query(
            query_texts=[query],
            n_results=3
        )
        
        docs = results['documents'][0]
        
        # 2. Graph Search
        # We look for entities in the Query AND in the retrieved Docs
        combined_text_for_extraction = query + " " + " ".join(docs)
        related_nodes = self.get_related_nodes(combined_text_for_extraction)
        
        # 3. Format Context
        context_str = "--- Retrieved Documentation ---\n"
        for i, doc in enumerate(docs):
            context_str += f"{i+1}. {doc}\n"
            
        context_str += "\n--- Knowledge Graph Relationships ---\n"
        if not related_nodes:
            context_str += "No specific graph relationships found.\n"
        else:
            subgraph = self.graph.subgraph(related_nodes)
            for u, v, data in subgraph.edges(data=True):
                context_str += f"- {u} --[{data.get('relation', 'related_to')}]--> {v}\n"
                
        return context_str
