# MercMechanic 🛠️🏎️

**The Intelligent, Privacy-First Diagnostic Assistant for Mercedes-Benz Vehicles.**

> *MercMechanic uses advanced Generative AI and Graph Theory to transform thousands of pages of technical manuals into instant, expert-level diagnostic advice—running entirely locally on your device.*

---

## 🧐 What is MercMechanic?

**MercMechanic** is a specialized AI agent designed to act as a **Senior Diagnostic Technician**. It is not just a search engine; it is a reasoning engine.

It ingests the massive, complex C-Class Owner's Manual (1000+ pages) and combines it with a structured **Knowledge Graph** of vehicle components. When you report a problem, MercMechanic doesn't just keywords; it understands the *cause and effect* of vehicle systems to provide a structured, actionable diagnosis.

---

## 💡 Why did we build it?

Modern vehicles are incredibly complex software-defined machines. The **Mercedes-Benz C-Class (W206)** manual alone is over **1,000 pages** long.

### The Problem
*   **Information Overload:** Finding the root cause of a specific vibration or warning light involves cross-referencing hundreds of pages.
*   **Lack of Context:** Standard search ("Ctrl+F") finds keywords but misses relationships (e.g., that a "Red Battery Icon" is caused by the *Alternator*).
*   **Privacy Concerns:** Diagnostics often require sensitive vehicle data that owners and workshops prefer not to send to the cloud.

### The Solution
MercMechanic solves this by bringing **Senior-Level Expertise** to your fingertips:
*   **Instant Recall:** It has "read" every page of the manual and never forgets.
*   **Causal Reasoning:** It knows that *A connects to B*, allowing it to trace faults logically.
*   **Privacy-First:** It runs 100% offline using local Small Language Models (SLMs), guaranteeing data privacy.

---

## ⚙️ How does it work?

MercMechanic uses a novel **Hybrid RAG (Retrieval-Augmented Generation)** architecture. Here is the step-by-step process of how it "thinks":

### 1. 📂 Ingestion (The "Learning" Phase)
*   **Vector Construction:** We process the 1041-page PDF manual, chunking it into small, meaningful segments. These are stored in **ChromaDB**, which allows the AI to find relevant text based on *meaning*, not just keywords.
*   **Graph Construction:** We build a **Knowledge Graph** using `NetworkX`. This maps physical components (e.g., *Radar Sensors*) to their functions (*Active Brake Assist*) and failure modes (*Dirty Bumper*).

### 2. 🔍 Hybrid Retrieval (The "Thinking" Phase)
When you ask: *"My Eco Start/Stop isn't working"*
*   **Vector Search:** Finds text in the manual about "Eco Start/Stop operating conditions" (e.g., "engine must be warm", "battery must be charged").
*   **Graph Traversal:** The Graph Explorer sees the node `Eco Start/Stop` and follows the edges:
    *   `Eco Start/Stop` --(disabled_by)--> `Sport Mode`
    *   `Eco Start/Stop` --(requires)--> `12V Battery`
*   **Synthesis:** The system combines the *manual's text* with the *graph's logic* into a single context.

### 3. 🧠 Generation (The "Expert" Phase)
This rich context is fed into a **Local LLM (`tinyllama`)**. The LLM is prompted with a specialized "Technician Persona" to:
*   Analyze the user's vague complaint.
*   Cross-reference the Graph rules with the Manual's text.
*   Output a professional **Diagnostic Report** with Analysis, Interaction, Diagnosis, and Prevention steps.

---

## 🏗️ Technical Architecture

```mermaid
graph TD
    User[Driver/Technician] -->|Query: 'Vibration'| CLI[CLI Interface]
    
    subgraph "Hybrid Retrieval Engine"
        CLI --> Router[Query Router]
        Router -->|Semantic Search| VectorDB[(ChromaDB\n1041 Pages)]
        Router -->|Causal Search| Graph[(Knowledge Graph\nRules)]
    end
    
    subgraph "Local Inference"
        VectorDB & Graph --> Context[Fused Context]
        Context --> Prompt[Expert Prompt]
        Prompt --> LLM[Ollama (TinyLlama)]
    end
    
    LLM -->|Diagnostic Report| User
```

## 📦 Tech Stack

*   **Core:** Python 3.13
*   **AI Orchestration:** LangChain
*   **Vector Database:** ChromaDB (Local, Embedded)
*   **Graph Database:** NetworkX
*   **LLM Runtime:** Ollama (Zero-Latency Local Inference)
*   **Data Processing:** `pypdf`, `sentence-transformers`

---

## 🧗 Challenges & Solutions

Building a local, privacy-first diagnostic agent came with significant hurdles. Here is how we overcame them:

### 1. The "1000-Page" PDF Problem
*   **Challenge:** Ingesting a 500MB+ PDF (1041 pages) caused memory overflows and "Stream Ended Unexpectedly" errors with standard libraries.
*   **Solution:** We architected a **Batch Ingestion Pipeline** using `pypdf`. Instead of loading the whole file, we process it in 50-page chunks, ensuring stable memory usage and reliable commit checkpoints to the Vector DB.

### 2. Local Inference Latency
*   **Challenge:** Running a standard 8-Billion parameter model (Llama 3) locally on a CPU resulted in slow responses (30s+), making the tool feel unresponsive.
*   **Solution:** We pivoted to **Small Language Models (SLMs)**. By optimizing the system prompt for `tinyllama` (1.1B parameters), we achieved near-instant responses while maintaining high diagnostic accuracy for this specific domain.

### 3. The "Sparse Graph" Dilemma
*   **Challenge:** A Knowledge Graph is only as good as its nodes. Initially, our graph was too small, leading to limited causal reasoning.
*   **Solution:** We implemented a **Hybrid Architecture**. Even if the graph misses a connection (e.g., *AdBlue -> Tank*), the Vector Search covers the gap by retrieving the raw text. We effectively use the Graph for "Precision" and Vector Search for "Recall."

## 🔮 Future Roadmap

## 🚀 Setup & Usage

### Prerequisites
*   Python 3.10+
*   [Ollama](https://ollama.com/) (Free, Open-Source)

### Installation
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-repo/mercmechanic.git
    cd mercmechanic
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Prepare the Brain:**
    *   Install Ollama and pull the model: `ollama pull tinyllama`
    *   Start the server: `ollama serve`

### Running It
1.  **Ingest Data:** (One-time setup to read the manual and build the graph)
    ```bash
    python src/main.py --rebuild
    ```
2.  **Diagnose:**
    ```bash
    python src/main.py "My car shakes when I brake"
    ```
