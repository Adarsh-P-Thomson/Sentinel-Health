# 🚀 Sentinel Health - Run Instructions

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** installed
3. **MongoDB** running locally (port 27017)
4. **PostgreSQL** running locally (port 5432)
5. **Azure OpenAI** deployment created

---

## 🔧 Setup Instructions

### 1. Fix Azure OpenAI Configuration

**IMPORTANT:** Your Azure OpenAI deployment name is wrong!

1. Go to **Azure Portal** → **Your OpenAI Resource** → **Model Deployments**
2. Find your actual deployment name (it's NOT "gpt-4")
3. Update `Backend/.env`:

```bash
# Change this line:
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# To your actual deployment name, for example:
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-deployment
# or
AZURE_OPENAI_DEPLOYMENT_NAME=my-gpt4-model
# or whatever you named it in Azure
```

### 2. Install Backend Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd Frontend
npm install
```

---

## 🏃‍♂️ Running the Application

### Terminal 1: Start Backend

```bash
cd Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
🚀 Starting Sentinel Health API v1.0.0
📍 Environment: development
✓ Connected to MongoDB: Sentinel_health
✓ Application startup complete
```

### Terminal 2: Start Frontend

```bash
cd Frontend
npm run dev
```

**Expected Output:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000

✓ Ready in 2.1s
```

---

## 🧪 Testing the Application

### 1. Open Browser
Go to: **http://localhost:3000**

### 2. Test Search
1. Click **"Search"** in navigation
2. Enter query: `"Lisinopril side effects"`
3. Select **Reddit JSON** source
4. Click **"Execute Search"**
5. Wait for results

### 3. Test Process & Analyze
1. Go to **"Suggestions"** page
2. Click **"Clean & Anonymize Data"** (Step 1)
   - This removes PII/PHI locally (NO AI cost)
3. Click **"Analyze with AI"** (Step 2)
   - This sends to Azure OpenAI (costs money)
4. View categorized results

---

## 🔍 API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Search
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Lisinopril side effects",
    "sources": ["reddit_json"],
    "limit": 50
  }'
```

### Process (Clean)
```bash
curl -X POST http://localhost:8000/api/v1/clean/latest
```

### Analyze (AI)
```bash
curl -X POST http://localhost:8000/api/v1/analyze/latest
```

### View Categories
```bash
curl http://localhost:8000/api/v1/categories
```

---

## 🐛 Troubleshooting

### Backend Issues

**Error: "DeploymentNotFound"**
- Fix your `AZURE_OPENAI_DEPLOYMENT_NAME` in `.env`
- Check Azure Portal for correct deployment name

**Error: "MongoDB connection failed"**
- Start MongoDB: `mongod` or `brew services start mongodb-community`
- Check port 27017 is available

**Error: "PostgreSQL connection failed"**
- Start PostgreSQL service
- Check credentials in `.env`

### Frontend Issues

**Error: "Failed to fetch"**
- Make sure backend is running on port 8000
- Check `Frontend/.env.local` has correct API URL:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
  ```

**Error: "CORS error"**
- Backend CORS is configured for localhost:3000
- Make sure frontend runs on port 3000

---

## 📊 Database Setup

### MongoDB Collections
The following collections are created automatically:
- `raw_posts` - Search results
- `cleaned_posts` - Processed data
- `processed_categories` - AI analysis results
- `processing_batches` - Batch tracking

### PostgreSQL Tables
Currently using MongoDB for main data storage.

---

## 💰 Cost Monitoring

### Azure OpenAI Usage
- **PROCESS** = FREE (local cleaning only)
- **ANALYZE** = PAID (Azure OpenAI API calls)
- Each post costs ~$0.001-0.01 depending on length
- 100 posts ≈ $0.10-1.00

### Monitor Usage
Check Azure Portal → OpenAI Resource → Usage & Quotas

---

## 🔄 Development Workflow

1. **Search** → Get raw posts from Reddit/social media
2. **Process** → Clean & anonymize locally (free)
3. **Analyze** → Send to AI agents (costs money)
4. **View** → See categorized insights

### File Structure
```
Sentinel-Health/
├── Backend/
│   ├── app/
│   │   ├── agents/          # AI agents (anonymizer, extractor, etc.)
│   │   ├── api/             # FastAPI endpoints
│   │   ├── core/            # Database, config, LLM
│   │   ├── services/        # Business logic
│   │   └── utils/           # Text cleaning, anonymization
│   └── requirements.txt
├── Frontend/
│   ├── app/
│   │   ├── search/          # Search page
│   │   └── suggestions/     # Results page
│   └── package.json
└── DOCS/                    # Documentation
```

---

## 🆘 Need Help?

1. Check backend logs in terminal
2. Check browser console for frontend errors
3. Verify all services are running:
   - Backend: http://localhost:8000/api/v1/health
   - Frontend: http://localhost:3000
   - MongoDB: port 27017
   - PostgreSQL: port 5432

---

## 🎯 Quick Start (TL;DR)

```bash
# 1. Fix Azure deployment name in Backend/.env
# 2. Start backend
cd Backend && uvicorn app.main:app --reload

# 3. Start frontend (new terminal)
cd Frontend && npm run dev

# 4. Open http://localhost:3000
# 5. Search → Process → Analyze → View Results
```