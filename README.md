# StartupSaarthi 🚀

**Multilingual RAG-based Startup Funding Intelligence System**

A production-grade AI assistant specialized in Indian startup funding, government schemes, investor ecosystems, and entrepreneurship policies. Built with FastAPI, React, and cloud-ready architecture.

## ✨ Features

- **🌍 Multilingual Support**: English, Hindi, Tamil, Telugu with automatic language detection
- **📚 Hybrid Retrieval**: FAISS (dense) + BM25 (sparse) + Reciprocal Rank Fusion
- **🎯 Cross-Encoder Reranking**: Improved retrieval quality with batch inference
- **🤖 Gemini LLM Integration**: Context-only generation with mandatory citations
- **📊 Structured & Unstructured Data**: PDF, DOCX, TXT, CSV, Excel support
- **🔗 Citation Tracking**: Every answer includes inline citations and source references
- **🚀 Cloud-Ready**: Stateless, API-first, deployable on free-tier platforms
- **🎨 Premium UI**: Modern React interface with glassmorphism and dark mode

## 🏗️ Architecture

```
Frontend (Vercel)          Backend API (Railway/Render)          Storage
┌──────────────┐          ┌────────────────────────────┐       ┌─────────────┐
│              │          │  Query Pipeline:           │       │             │
│  React UI    │◄────────►│  1. Language Detection     │◄─────►│ FAISS Index │
│  TypeScript  │   REST   │  2. Translation (optional) │       │             │
│  Vite        │   API    │  3. Hybrid Retrieval       │       ├─────────────┤
│              │          │  4. RRF Fusion             │       │             │
└──────────────┘          │  5. Reranking              │◄─────►│ BM25 Index  │
                          │  6. LLM Generation         │       │             │
                          │                            │       ├─────────────┤
                          │  Ingestion Pipeline:       │       │             │
                          │  - PDF/DOCX/TXT Parser     │◄─────►│ Documents   │
                          │  - CSV/Excel Parser        │       │ (S3/Local)  │
                          │  - Index Builder           │       │             │
                          └────────────────────────────┘       └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key

### 1. Backend Setup

```bash
# Clone repository
cd StartupSaarthi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY and ADMIN_API_KEY

# Run backend
python -m backend.main
```

Backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
cd startupsaarthi-ui

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env and set VITE_API_URL=http://localhost:8000

# Run frontend
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 3. Ingest Sample Data

```bash
# Use the admin API to ingest documents
curl -X POST http://localhost:8000/api/admin/ingest \
  -H "X-Admin-Key: your_admin_key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/document.pdf",
    "document_type": "pdf",
    "metadata": {"category": "government_scheme"}
  }'
```

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### User Endpoints

- `POST /api/query` - Submit a query and get an answer with citations
- `GET /api/languages` - Get supported languages

#### Admin Endpoints (require `X-Admin-Key` header)

- `POST /api/admin/ingest` - Ingest a document
- `POST /api/admin/reindex` - Rebuild indices
- `GET /api/admin/stats` - Get system statistics

## 🌐 Deployment

### Frontend (Vercel)

```bash
cd startupsaarthi-ui
vercel deploy
```

### Backend (Railway)

1. Create a new project on Railway
2. Connect your GitHub repository
3. Add environment variables from `.env.example`
4. Deploy

### Backend (Render)

1. Create a new Web Service
2. Connect your GitHub repository
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Docker Deployment

```bash
# Build image
docker build -t startupsaarthi .

# Run container
docker run -p 8000:8000 --env-file .env startupsaarthi
```

## 🧪 Testing

```bash
# Run tests
pytest backend/tests/ -v --cov=backend

# Test multilingual queries
pytest backend/tests/test_multilingual.py -v
```

## 📁 Project Structure

```
StartupSaarthi/
├── backend/
│   ├── api/              # FastAPI routes and models
│   ├── graph/            # LangGraph orchestration
│   ├── retriever/        # Hybrid retrieval (FAISS, BM25, RRF, reranker)
│   ├── llm/              # Gemini LLM client and prompts
│   ├── ingestion/        # Document processing and indexing
│   ├── utils/            # Language detection, translation
│   ├── config.py         # Configuration management
│   └── main.py           # FastAPI application
├── startupsaarthi-ui/    # React frontend
├── storage/              # Local storage for indices and documents
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── Dockerfile            # Docker configuration
└── README.md             # This file
```

## 🔑 Environment Variables

See `.env.example` for all configuration options. Key variables:

- `GEMINI_API_KEY` - Google Gemini API key (required)
- `ADMIN_API_KEY` - Admin authentication key (required)
- `EMBEDDING_MODEL` - Multilingual embedding model
- `ENABLE_TRANSLATION` - Enable query translation for better retrieval
- `CORS_ORIGINS` - Allowed frontend origins

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with FastAPI, React, LangGraph, FAISS, and Gemini
- Inspired by the need for accessible startup funding information in India
- Designed for Indian founders and the startup ecosystem

## 📞 Support

For issues and questions:
- Open a GitHub issue
- Check the documentation at `/docs`
- Review the implementation plan in `docs/`

---

**Made with ❤️ for Indian Startups**
