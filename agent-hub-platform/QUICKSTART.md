# Quick Start Guide 🚀

Get Agent Hub Platform running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- (Optional) DB2 database access
- (Optional) Kubernetes cluster access

## Step 1: Backend Setup (2 minutes)

### Windows:

```bash
cd Documents\agent-hub-platform\backend

# Create virtual environment
uv venv
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com

# Create config file
copy config\agents.example.yaml config\agents.yaml

# Edit config\agents.yaml with your settings (optional for testing)

# Start backend
python main.py
```

### Linux/Mac:

```bash
cd Documents/agent-hub-platform/backend

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com

# Create config file
cp config/agents.example.yaml config/agents.yaml

# Edit config/agents.yaml with your settings (optional for testing)

# Start backend
python main.py
```

**Backend will start at**: http://localhost:8000

Check it's running: http://localhost:8000/health

---

## Step 2: Frontend Setup (3 minutes)

Open a **new terminal** window:

```bash
cd Documents\agent-hub-platform\frontend

# Install dependencies (first time only - takes ~2-3 minutes)
npm install

# Start development server
npm start
```

**Frontend will open at**: http://localhost:3000

The browser should automatically open!

---

## Step 3: Try It Out! (∞ fun)

Once both backend and frontend are running, try these queries:

### Example Queries:

```
"Help"
"What can you do?"
"Check DB2 health"
"Show kubernetes pods"
"Analyze repository at C:\path\to\repo"
"List agents"
```

---

## 🎉 That's It!

You now have a fully functional multi-agent platform!

## Next Steps

### Configure Your Agents

Edit `backend/config/agents.yaml` to add your:

- DB2 database credentials
- Kubernetes cluster settings
- Repository paths

### Add More Agents

See the full README.md for how to add:
- JIRA integration
- Confluence search
- Akeyless secrets
- Custom agents

### Production Deployment

See `DEPLOYMENT.md` for production setup instructions.

---

## Troubleshooting

### Backend won't start

**Error**: `No module named 'fastapi'`

**Fix**: Install dependencies
```bash
cd backend
pip install -r requirements.txt --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com
```

### Frontend won't start

**Error**: `command not found: npm`

**Fix**: Install Node.js from https://nodejs.org

**Error**: `npm install` fails

**Fix**: Clear cache and retry
```bash
npm cache clean --force
npm install
```

### "Cannot connect to backend"

1. Check backend is running: http://localhost:8000/health
2. Check there are no firewall issues
3. Verify backend logs for errors

### Agents not working

**DB2 Agent**: 
- Check `backend/config/agents.yaml` has correct DB2 credentials
- Verify DB2 drivers are installed (see db2-monitoring-agent/WALMART_SETUP.md)

**Repo Analyzer**:
- Verify path to repository exists
- Check you have read permissions

---

## Architecture Overview

```
Frontend (React)          Backend (FastAPI)              Agents
     |                          |                            |
     |------- HTTP/WS --------->|                            |
     |                          |---- routes query -------->|
     |                          |                            |
     |                          |<----- response -----------|
     |<------ response ---------|                            |
```

---

## Useful Commands

### Backend:

```bash
# Run with auto-reload
python main.py

# Run on different port
uvicorn main:app --port 8080 --reload

# View API docs
open http://localhost:8000/docs
```

### Frontend:

```bash
# Development server
npm start

# Production build
npm run build

# Run tests
npm test
```

---

## Port Reference

- **8000**: Backend API
- **3000**: Frontend development server
- **8000/docs**: API documentation (Swagger UI)
- **8000/redoc**: API documentation (ReDoc)

---

## What's Next?

✅ Platform is running  
✅ Agents are loaded  
✅ UI is responsive  

Now you can:

1. **Customize agents** - Edit `backend/config/agents.yaml`
2. **Add new agents** - See README.md for agent development guide
3. **Deploy to production** - See DEPLOYMENT.md
4. **Integrate with your tools** - JIRA, Confluence, etc.

Happy agent orchestration! 🐶🚀
