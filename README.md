Local Multi-PDF Knowledge Base Chatbot (RAG System)

## 1.Project Background

Large Language Models (LLMs) may generate hallucinations when answering domain-specific or knowledge-intensive questions. In real-world scenarios, users often need answers grounded in private documents such as company manuals, technical reports, or internal knowledge bases.

To improve factual accuracy and domain relevance, this project implements a **Local Multi-PDF Knowledge Base Chatbot based on Retrieval-Augmented Generation (RAG)**.

The system supports PDF upload, text chunking, embedding generation, vector retrieval, metadata tracking, and multi-document question answering. By integrating document retrieval with LLM reasoning, the chatbot can provide more targeted and context-aware responses based on uploaded materials.



## 2.Features

- **Dual QA Modes**  
  Supports both general LLM chat and document-grounded question answering.

- **Multi-PDF Knowledge Base Management**  
  Upload, process, and manage multiple PDF documents for long-term reuse.

- **Semantic Retrieval with Vector Search**  
  Uses embedding-based semantic search (FAISS) to retrieve relevant document chunks.

- **Source Attribution & Traceability**  
  Returns source file information and document locations to help users verify answers.

- **Persistent Local Knowledge Base**  
  Stores processed documents and vector indexes locally for cross-session usage.

- **Retrieval Evaluation Pipeline**  
  Supports RAG evaluation and retrieval accuracy analysis for system performance assessment.

- **Adaptive Question Routing**  
  Automatically distinguishes between global questions and detail questions.  
  High-level document questions are handled by the Summary pipeline, while detailed questions use standard RAG retrieval.



## 3.Tech Stack
| Category            | Technology                 |
| ------------------- | -------------------------- |
| Backend             | FastAPI                    |
| LLM / Inference     | OpenAI API                 |
| Embedding           | sentence-transformers      |
| Retrieval           | FAISS                      |
| Document Processing | pypdf + custom chunking    |
| Storage             | pickle + FAISS persistence |



## 4.System Architecture

### Knowledge Base Building Pipeline

```text
Upload PDF
    ↓
Duplicate File Check
    ↓
PDF Parsing
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
FAISS Vector Indexing
    ↓
Metadata Construction
    ↓
Local Persistence
```

### Question Answering Pipeline

```text
User Question
      ↓
Question Router
      ↓
Global Question?
 ┌───────────────┴───────────────┐
 Yes                            No
 ↓                               ↓
Summary Pipeline           RAG Retrieval
                                 ↓
                         Prompt Construction
                                 ↓
                        LLM Answer Generation
                                 ↓
                         Source Attribution
```



## 5.Quick Start
### 5.1. Clone the Repository

```bash
git clone https://github.com/MYaiZERO/rag-pdf-assistant.git
cd rag_project
```

### 5.2. Create a Conda Environment

```bash
conda create -n rag python=3.10
conda activate rag
```

### 5.3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5.4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
API_KEY=your_api_key
MODEL_NAME=your_model_name
BASE_URL=your_api_base_url
```

Users should configure their own API provider and credentials.

### 5.5. Run the Application

```bash
uvicorn app.main:app --reload
```

### 5.6. Access the API

Open:

```text
http://127.0.0.1:8000/docs
```

Use the Swagger UI to test:

* `/upload`
* `/ask`
* `/summary`
* `/status`
* `/source`



## 6.API Reference
|Endpoint    | Method |                                Description                                         |
-----------------------------------------------------------------------------------------------------------|
| `/chat`    | GET    | General LLM chat without using the knowledge base                                  |
| `/upload`  | POST   | Upload and process PDF documents into the knowledge base                           |
| `/ask`     | GET    | Main adaptive QA endpoint with automatic routing between Summary and RAG pipelines |
| `/summary` | GET    | Standalone document summarization endpoint for debugging and evaluation            |
| `/status`  | GET    | View knowledge base status and storage information                                 |
| `/source`  | GET    | Inspect document metadata and source information                                   |

### `/chat`

General-purpose LLM conversation.

This endpoint does **not** use the knowledge base.

Example:
```http
GET /chat?message=What is artificial intelligence?
```

### `/upload`

Upload a PDF document and add it to the local knowledge base.

Processing pipeline:

```text
Duplicate Check
→ PDF Parsing
→ Text Chunking
→ Embedding Generation
→ FAISS Indexing
→ Metadata Construction
→ Local Persistence
```

Returns:

* filename
* page count
* chunk count
* duplicate upload status (`skipped`)
* knowledge base status

### `/ask`

Main user-facing QA endpoint.

The system automatically determines the question type and selects the appropriate pipeline.

Routing logic:

```text
Question
↓
Question Router
↓
Global Question?
├── Yes → Summary Pipeline
└── No → RAG Retrieval Pipeline
```

Examples:
Global Question:
```text
What is this document mainly about?
```
→ Summary pipeline

Detail Question:
```text
What is the definition of intelligence?
```
→ RAG retrieval pipeline

Returns:

* question
* generated answer
* retrieved sources
* retrieval contexts

### `/summary`

Standalone document summarization interface.

Mainly used for:

* module testing
* debugging
* evaluation
* direct document summarization

Parameters:

* filename
* batch_size
* max_batches

### `/status`

View current knowledge base status.

Returns:

* chunk count
* processed files
* FAISS index status
* local storage information

### `/source`

Inspect stored document metadata.

Returns:

* source filename
* page number
* chunk id
* metadata information



## 7.Evaluation Results

The RAG system was evaluated using retrieval-based metrics and routing validation.

### Retrieval Evaluation

The following metrics were used to measure retrieval performance:

* **Top-K Retrieval**
* **Total Hit Count**
* **Hit Rate**
* **MRR (Mean Reciprocal Rank)**

Evaluation records include:

* question id
* query content
* expected source document
* retrieved pages
* retrieval hit status

Example evaluation format:

| ID |              Question                   | Expected Source | Retrieved Pages | Hit |
| -- | --------------------------------------- | --------------- | --------------- | --- |
| 1  | What is the definition of intelligence? | AI_Basics.pdf   | 1               | ✓   |
| 2  | What does this document mainly discuss? | ML_Stage1.pdf   | 3               | ✓   |

### Retrieval Verification Strategy

Retrieval correctness was verified using:

### 7.1.**Source Matching**
The retrieved document source should match the expected source.

### 7.2. **Page-level Validation**
Retrieved pages should contain the target information.

### 7.3. **Ranking Quality**
MRR was used to evaluate whether relevant chunks appeared near the top retrieval positions.

### Question Routing Validation

The adaptive QA router was manually tested.
Expected behavior:
Global Questions:

```text
What is this document mainly about?
```

→ Summary Pipeline

Detail Questions:

```text
What is the definition of intelligence?
```

→ RAG Retrieval Pipeline

The routing path was verified to ensure correct pipeline selection.



## 8.Engineering Challenges & Solutions

### 8.1. Dependency Management

**Problem**
Using `pip freeze` produced environment-specific dependencies such as:
```text
package @ file:///...
```

Using `pipreqs` introduced additional issues including package resolution timeouts.

**Solution**
A lightweight and portable `requirements.txt` was manually curated by:

* removing environment-specific local paths
* keeping only project-level dependencies
* validating reproducibility in a clean environment

### 8.2. PDF Page Tracking Bug

**Problem**
Initially, retrieved chunks always reported:
```text
page = 1
```

which made source attribution unreliable.

**Cause**
The original PDF loader extracted only merged text and discarded page-level metadata.

**Solution**
The loader was redesigned to preserve page information during parsing.

A page-aware loading pipeline was implemented to maintain:

* text content
* page number
* metadata consistency

### 8.3. Duplicate File Upload Handling

**Problem**
Repeated uploads of the same PDF caused duplicated chunks and repeated vector indexing.

**Solution**
A duplicate detection mechanism was introduced using:
```text
processed_files
```

The system now:

* checks upload history
* skips previously processed files
* prevents redundant indexing

### 8.4. Adaptive Question Routing

**Problem**
Different question types require different answering strategies.

Examples:
* global document questions
* detail-oriented factual questions

Using a single retrieval strategy reduced answer quality.

**Solution**
An adaptive router was implemented.

Routing logic:
```text
Global Question → Summary Pipeline
Detail Question → RAG Retrieval Pipeline
```

The unified `/ask` endpoint automatically selects the appropriate pipeline.



## 9.Project Structure

```text
RAG_PROJECT/
│
├── app/
│   ├── main.py                  # FastAPI application entrypoint
│   ├── config.py                # Environment configuration
│   ├── llm.py                   # LLM API wrapper
│   ├── embeddings.py            # Embedding generation
│   ├── pdf_loader.py            # PDF parsing
│   ├── text_splitter.py         # Text chunking logic
│   ├── vector_store.py          # FAISS vector storage & persistence
│   ├── rag.py                   # RAG retrieval and prompt pipeline
│   ├── document_summary.py      # Document summarization pipeline
│   └── question_router.py       # Adaptive question routing
│
├── data/                        # Uploaded PDF files
│
├── storage/
│   ├── faiss.index              # Saved FAISS index
│   ├── chunks.pkl               # Chunk storage
│   └── processed_files.pkl      # Duplicate upload tracking
│
├── eval/
│   ├── eval_retrieval.py        # Retrieval evaluation script
│   ├── questions.json           # Evaluation dataset
│   └── retrieval_eval_top3.json # Evaluation results
│
├── docs/
│   └── dev_notes.md             # Development logs & debugging notes
│
├── .env                         # Environment variables
├── requirements.txt            # Project dependencies
├── .gitignore
└── README.md
```



## 10.Future Improvements

Several improvements can further enhance the system.

### 10.1. OCR Support for Scanned PDFs

The current implementation mainly supports text-based PDFs.

Future work includes integrating OCR pipelines to process:

* scanned documents
* image-based PDFs
* photographed lecture notes

This would improve robustness in real-world document scenarios.

### 10.2. Web UI Interface

The current system is API-oriented.

A future web interface could provide:

* file upload panel
* interactive chat window
* source citation display
* retrieval visualization

This would improve usability and create a more product-oriented user experience.

### 10.3. Docker Deployment

The current setup requires manual environment configuration.

Future deployment improvements may include:

* Docker containerization
* one-command startup
* simplified environment reproducibility

This would improve portability and deployment efficiency.
