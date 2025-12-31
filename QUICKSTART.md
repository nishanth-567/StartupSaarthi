# StartupSaarthi - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Backend (2 minutes)

```powershell
# Navigate to project
cd d:\A_VERSE\StartupSaarthi

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
```

**Edit `.env` file:**
- Add your `GEMINI_API_KEY` (get from https://makersuite.google.com/app/apikey)
- Set `ADMIN_API_KEY=mysecretkey123` (any secure string)

```powershell
# Start backend
python -m backend.main
```

✅ Backend running at http://localhost:8000

### Step 2: Setup Frontend (2 minutes)

```powershell
# Open new terminal
cd d:\A_VERSE\StartupSaarthi\startupsaarthi-ui

# Install dependencies
npm install

# Create .env file
copy .env.example .env
```

**Edit `.env` file:**
- Set `VITE_API_URL=http://localhost:8000`

```powershell
# Start frontend
npm run dev
```

✅ Frontend running at http://localhost:5173

### Step 3: Ingest Sample Data (1 minute)

```powershell
# Open new terminal
cd d:\A_VERSE\StartupSaarthi

# Ingest text document
curl -X POST http://localhost:8000/api/admin/ingest `
  -H "X-Admin-Key: mysecretkey123" `
  -H "Content-Type: application/json" `
  -d '{\"file_path\": \"d:\\A_VERSE\\StartupSaarthi\\sample_data\\sidbi_fund_of_funds.txt\", \"document_type\": \"txt\", \"metadata\": {\"category\": \"scheme\"}}'

# Ingest CSV data
curl -X POST http://localhost:8000/api/admin/ingest `
  -H "X-Admin-Key: mysecretkey123" `
  -H "Content-Type: application/json" `
  -d '{\"file_path\": \"d:\\A_VERSE\\StartupSaarthi\\sample_data\\investors.csv\", \"document_type\": \"csv\", \"metadata\": {\"category\": \"investors\"}}'
```

✅ Sample data ingested!

### Step 4: Test the System

Open http://localhost:5173 in your browser.

**Try these queries:**

1. **English**: "What is SIDBI Fund of Funds?"
2. **Hindi**: "SIDBI Fund of Funds क्या है?"
3. **Investor Query**: "List top 5 investors in technology"
4. **Specific Detail**: "What is the corpus of SIDBI FFS?"

✅ You should see answers with inline citations!

## 🎯 What You Get

- ✅ Multilingual AI assistant (English, Hindi, Tamil, Telugu)
- ✅ Hybrid retrieval (FAISS + BM25)
- ✅ Mandatory citations in every answer
- ✅ Premium dark mode UI
- ✅ Admin API for document ingestion
- ✅ Cloud-ready architecture

## 📚 Next Steps

1. **Add Your Documents**: Use the admin API to ingest PDFs, DOCX, CSV, Excel files
2. **Deploy to Cloud**: See README.md for Vercel + Railway deployment
3. **Customize**: Modify prompts in `backend/llm/prompt_templates.py`
4. **Scale**: Add more documents and test with real queries

## 🆘 Troubleshooting

**Backend won't start?**
- Check if Gemini API key is set in `.env`
- Ensure Python 3.11+ is installed

**Frontend shows errors?**
- Check if backend is running at http://localhost:8000
- Verify `VITE_API_URL` in frontend `.env`

**Ingestion fails?**
- Verify file paths are absolute
- Check admin API key matches in `.env`

**No results for queries?**
- Ensure documents are ingested successfully
- Check backend logs for errors

## 📖 Documentation

- **Full Documentation**: [README.md](file:///d:/A_VERSE/StartupSaarthi/README.md)
- **API Docs**: http://localhost:8000/docs
- **Walkthrough**: See artifacts for detailed walkthrough

## 🎉 Success!

You now have a fully functional StartupSaarthi system running locally!

**Share this folder** (`d:\A_VERSE\StartupSaarthi`) with anyone - it contains everything needed to run the system.
