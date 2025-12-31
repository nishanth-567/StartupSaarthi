# StartupSaarthi: System Architecture & Data Flow

## 1. System Overview
StartupSaarthi is a **Retrieval-Augmented Generation (RAG)** system designed to answer complex queries about Indian Startup policies, funding, and investors. It combines semantic search with a Large Language Model (LLM) to provide accurate, context-aware responses based on official documents.

---

## 2. High-Level Architecture

The system consists of three main layers:
1.  **Frontend (UI Layer):** A React-based chat interface.
2.  **Backend (API Layer):** A FastAPI server that orchestrates the RAG pipeline.
3.  **Intelligence Layer:** A combination of local embedding models (Sentence Transformers), Vector Stores (FAISS), and an external LLM (Groq Llama 3).

---

## 3. Data Ingestion Pipeline (The "Brain" Building)

This offline process converts raw documents into a searchable knowledge base.

**Steps:**
1.  **Document Loading:**
    *   The system scans the `scraped_data` directory.
    *   It recursively reads PDF, DOCX, and TXT files.
2.  **Preprocessing & Chunking:**
    *   Text is extracted and cleaned.
    *   Large documents are split into smaller "chunks" (e.g., 500 words) using sliding windows to preserve context.
3.  **Vector Embedding:**
    *   Each text chunk is passed through the `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` model.
    *   This converts text into a **384-dimensional dense vector** (numerical representation of meaning).
4.  **Indexing (Hybrid Storage):**
    *   **Dense Index (FAISS):** Stores the vectors for semantic search (finding "matching meanings").
    *   **Sparse Index (BM25):** Stores keywords for exact matching (finding "specific terms").
    *   **Metadata Store:** Saves the actual text content and file source for each chunk.

---

## 4. Query Processing Flow (The "Thinking" Process)

When a user asks a question, the system executes the following real-time pipeline:

**Step 1: Query Analysis**
*   The backend receives the user's question (e.g., "What is the Seed Fund Scheme?").
*   It detects the language (English/Hindi).

**Step 2: Hybrid Retrieval**
*   **Dense Search:** The query is embedded (converted to vector) and compared against the FAISS index to find semantically similar chunks.
*   **Sparse Search:** The query keywords are matched against the BM25 index.
*   **Fusion:** Results from both methods are combined using **Reciprocal Rank Fusion (RRF)** to get the best of both worlds.

**Step 3: Neural Reranking (Refinement)**
*   The top 30+ results are passed to a **Cross-Encoder Model** (`cross-encoder/ms-marco-MiniLM-L-6-v2`).
*   This model strictly evaluates the relevance of each document to the specific question.
*   Only the **Top 5** most relevant chunks are selected.

**Step 4: Answer Generation**
*   **Context Assembly:** The top 5 text chunks are combined into a system prompt.
*   **LLM Invocation:** The prompt + user question is sent to **Groq (Llama 3.3-70B)**.
*   **Guardrails:** The system instructs the LLM to answer *only* using the provided context and citations.

**Step 5: Response**
*   The final answer, along with source document citations, is streamed back to the frontend.

---

## 5. Technology Stack

*   **LLM Provider:** Groq (Llama 3.3-70B Versatile)
*   **Backend Framework:** Python FastAPI
*   **Vector Database:** FAISS (Facebook AI Similarity Search)
*   **Embedding Model:** `paraphrase-multilingual-MiniLM-L12-v2` (Local)
*   **Reranking Model:** `ms-marco-MiniLM-L-6-v2` (Local)
*   **Frontend Library:** React + Vite
