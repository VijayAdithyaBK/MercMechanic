import argparse
import sys
import os
import io

# Add src to path if needed (though running as python src/main.py usually requires explicit package handling or path adjustment)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force UTF-8 for Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.ingestion import build_vector_index, build_graph_index
from src.retrieval import HybridRetriever
from src.llm_client import LLMClient

def main():
    parser = argparse.ArgumentParser(description="MercMechanic: Intelligent Diagnostics Assistant")
    parser.add_argument("query", nargs="?", type=str, help="The diagnostic question (e.g., 'ABS light is on')")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of indices")
    
    args = parser.parse_args()
    
    # Check if indices exist
    db_exists = os.path.exists(os.path.join("chroma_db"))
    
    if args.rebuild or not db_exists:
        print("[System] Building Indices...")
        try:
            build_vector_index(reset=True)
            build_graph_index()
        except Exception as e:
            print(f"[Error] Failed to build indices: {e}")
            print("Ensure you have 'owners_manual_mock.txt' and 'knowledge_graph.json' in /data")
            return

    if not args.query:
        print("\nWelcome to MercMechanic CLI")
        print("Usage: python src/main.py \"<your query>\"")
        print("Example: python src/main.py \"Why is the ABS light on?\"")
        return

    # Retrieval
    try:
        retriever = HybridRetriever()
        context = retriever.retrieve(args.query)
    except Exception as e:
        print(f"[Error] Retrieval failed: {e}")
        return

    print("\n" + "="*40)
    print("CONTEXT RETRIEVED")
    print("="*40)
    print(context)
    print("="*40 + "\n")

    # Generation
    print("[System] Consulting Expert Agent...\n")
    llm = LLMClient() # 2. Generate Diagnosis
    system_prompt = (
        "You are an Expert Mercedes-Benz Technician & Diagnostic Assistant. "
        "Your role is to diagnose vehicle issues based strictly on the provided context (Owner's Manual + Knowledge Graph). "
        "Strictly follow these rules:\n"
        "1. ANALYSIS: Use the provided Context to find relevant info.\n"
        "2. INTERACTION: If the user's description is vague (e.g. 'vibration'), ASK clarifying questions (speed, road condition, location) to narrow it down.\n"
        "3. DIAGNOSIS: List potential causes with probabilities if possible (e.g. 'Most likely: Wheel Balance').\n"
        "4. PREVENTION: Cite specific pages or sections from the manual if mentioned.\n"
        "5. TONE: Professional, technical, yet accessible.\n"
        "6. FALLBACK: If the context has no answer, say 'I cannot find this in the manual, please contact a service center'."
    )
    
    final_prompt = f"{system_prompt}\n\nCONTEXT:\n{context}\n\nUSER QUERY: {args.query}\n\n>> DIAGNOSIS REPORT:"
    
    response = llm.generate(final_prompt)
    
    print(">> DIAGNOSIS REPORT:")
    print(response)

if __name__ == "__main__":
    main()
