# Agent Hub Platform 🚀🐶

**A unified multi-agent orchestration platform with a beautiful web UI**

Chat with your infrastructure, databases, repositories, and services through a single, intelligent interface.

## 🎯 What Is This?

Agent Hub is a conversational AI platform that lets you interact with various systems through natural language:

- 💾 **DB2 & Kubernetes Monitoring** - Check database health, query status, pod health
- 📊 **Repository Analysis** - Analyze codebases, track dependencies, generate docs
- 🎫 **JIRA Integration** (Coming Soon) - Create tickets, query status, track issues
- 📚 **Confluence Search** (Coming Soon) - Search docs, retrieve knowledge
- 🔐 **Akeyless Secrets** (Coming Soon) - Manage secrets, retrieve credentials
- 🏥 **Health Checks** - Monitor deployments, check pod status, view logs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           React Frontend (Chat UI)          │
│  - Natural language input                   │
│  - Rich response rendering                  │
│  - Multi-format output (text, tables, etc.) │
└──────────────────┬──────────────────────────┘
                   │ HTTP/WebSocket
                   ▼
┌─────────────────────────────────────────────┐
│         FastAPI Backend (Orchestrator)       │
│  - Intent recognition                        │
│  - Agent routing                             │
│  - Response aggregation                      │
└──────────────────┬──────────────────────────┘
                   │
      ┌────────────┼────────────┬─────────────┐
      ▼            ▼            ▼             ▼
  ┌───────┐  ┌──────────┐  ┌────────┐  ┌─────────┐
  │  DB2  │  │   Repo   │  │  JIRA  │  │ More... │
  │ Agent │  │ Analyzer │  │ Agent  │  │ Agents  │
  └───────┘  └──────────┘  └────────┘  └─────────┘
```

## ✨ Features

### Current Features
- ✅ **Conversational Interface** - Ask questions in natural language
- ✅ **Multi-Agent Support** - Multiple specialized agents working together
- ✅ **DB2 & K8s Monitoring** - Real-time health checks and queries
- ✅ **Repository Analysis** - Code analysis, dependency tracking
- ✅ **Plugin Architecture** - Easy to add new agents
- ✅ **Beautiful UI** - Modern, responsive React interface
- ✅ **Real-time Updates** - WebSocket support for live data
- ✅ **Rich Responses** - Tables, charts, JSON, markdown rendering

### Coming Soon
- 🔄 **JIRA Integration** - Ticket management through chat
- 🔄 **Confluence Search** - Knowledge base queries
- 🔄 **Akeyless Integration** - Secret management
- 🔄 **Deployment Monitoring** - Track deployments across environments
- 🔄 **Log Aggregation** - Query and analyze logs
- 🔄 **Alert Management** - Create and manage alerts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- Access to DB2 database (optional)
- Kubernetes cluster access (optional)

### Installation

#### 1. Backend Setup

```bash
cd agent-hub-platform/backend

# Create virtual environment
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
uv pip install -r requirements.txt --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com

# Configure agents
cp config/agents.example.yaml config/agents.yaml
# Edit config/agents.yaml with your settings

# Run backend
python main.py
```

Backend will start at: http://localhost:8000

#### 2. Frontend Setup

```bash
cd agent-hub-platform/frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open at: http://localhost:3000

### First Conversation

Once both are running, try asking:

```
"Check DB2 health status"
"What pods are running in my kubernetes cluster?"
"Analyze the repository in C:\path\to\repo"
"Show me the database response time"
```

## 📁 Project Structure

```
agent-hub-platform/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── orchestrator.py         # Agent orchestration logic
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py            # Base agent interface
│   │   ├── db2_agent.py       # DB2 monitoring agent
│   │   ├── repo_agent.py      # Repository analyzer agent
│   │   ├── jira_agent.py      # JIRA integration (coming soon)
│   │   └── confluence_agent.py # Confluence (coming soon)
│   ├── models/
│   │   ├── request.py         # Request models
│   │   └── response.py        # Response models
│   ├── config/
│   │   ├── agents.yaml        # Agent configuration
│   │   └── settings.py        # Application settings
│   ├── utils/
│   │   ├── intent_parser.py   # Natural language understanding
│   │   └── response_formatter.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.jsx       # Main chat interface
│   │   │   ├── MessageList.jsx
│   │   │   ├── InputBox.jsx
│   │   │   └── ResponseRenderer.jsx  # Rich response display
│   │   ├── services/
│   │   │   └── api.js         # Backend API client
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── README.md
│
├── shared/
│   └── schemas/               # Shared data schemas
│
└── docs/
    ├── AGENT_DEVELOPMENT.md   # How to create new agents
    ├── API.md                 # API documentation
    └── DEPLOYMENT.md          # Production deployment guide
```

## 🔌 Adding New Agents

Agents are plugins! Here's how to add one:

### 1. Create Agent Class

```python
# backend/agents/my_agent.py
from agents.base import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(name="my_agent", config=config)
    
    def can_handle(self, user_input: str) -> bool:
        """Determine if this agent can handle the request."""
        keywords = ["my", "service", "check"]
        return any(kw in user_input.lower() for kw in keywords)
    
    async def execute(self, user_input: str, context: dict) -> dict:
        """Execute the agent's task."""
        # Your logic here
        return {
            "status": "success",
            "data": {...},
            "message": "Task completed"
        }
```

### 2. Register Agent

```yaml
# config/agents.yaml
agents:
  - name: my_agent
    enabled: true
    module: agents.my_agent
    class: MyAgent
    config:
      api_url: "https://my-service.com"
```

### 3. That's It!

The orchestrator will automatically load and use your agent!

## 💬 Example Conversations

### DB2 & Kubernetes Monitoring

```
User: "Is my DB2 database healthy?"
Agent: ✅ DB2 Status: HEALTHY
       - Connected: Yes
       - Response Time: 45ms
       - Query Executed: Successfully

User: "Show me all pods in production namespace"
Agent: 📊 Found 12 pods:
       [Table with pod details]

User: "What's the restart count for my-app pod?"
Agent: Pod 'my-app-abc123' has 2 restarts in the last 24 hours
```

### Repository Analysis

```
User: "Analyze the repository at C:\projects\my-app"
Agent: 📊 Repository Analysis Complete:
       - Language: Python
       - Files: 145
       - Dependencies: 32
       - Code Quality: A
       [Detailed metrics...]

User: "What dependencies does this repo have?"
Agent: 📦 Dependencies (32 total):
       [Table with dependency details]
```

## 🛠️ Configuration

Edit `backend/config/agents.yaml` to configure agents:

```yaml
# DB2 Monitoring Agent
db2_agent:
  enabled: true
  db2:
    host: "your-db2-host"
    port: 50000
    database: "YOURDB"
    username: "user"
    password: "pass"
  kubernetes:
    namespace: "default"
    kubeconfig_path: null

# Repository Analyzer Agent  
repo_agent:
  enabled: true
  default_analysis_depth: "full"
  output_formats: ["json", "markdown"]
```

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Hot Reload

Both backend and frontend support hot reload during development!

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚢 Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment instructions.

## 🤝 Contributing

Want to add a new agent? See [AGENT_DEVELOPMENT.md](docs/AGENT_DEVELOPMENT.md)

## 📝 License

MIT License - Built with 🐶 Code Puppy

## 🎉 What Makes This Special?

- **Conversational**: Talk to your infrastructure like a human
- **Unified**: One interface for all your tools
- **Extensible**: Add new agents in minutes
- **Beautiful**: Modern, responsive UI
- **Production-Ready**: Proper error handling, logging, security
- **Open**: Open source, no vendor lock-in

Let's make infrastructure management fun again! 🚀🐶
