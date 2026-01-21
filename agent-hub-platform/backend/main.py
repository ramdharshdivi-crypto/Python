"""FastAPI main application for Agent Hub."""

import logging
import sys
from pathlib import Path
from typing import Optional
import yaml
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from orchestrator import AgentOrchestrator
from agents.db2_agent import DB2MonitoringAgent
from agents.repo_agent import RepositoryAnalyzerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agent Hub Platform",
    description="Multi-agent orchestration platform with conversational interface",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()


# Pydantic models
class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str
    session_id: Optional[str] = None
    batch_id: Optional[str] = None
    output_format: Optional[str] = None  # 'json' or 'text'


class QueryResponse(BaseModel):
    """Response model for queries."""
    status: str
    message: str
    data: Optional[dict] = None
    response_type: str = "text"
    metadata: Optional[dict] = None
    timestamp: str
    session_id: str
    batch_id: Optional[str] = None
    output_format: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    logger.info("Starting Agent Hub Platform...")
    
    # Load configuration
    config_path = Path(__file__).parent / "config" / "agents.yaml"
    logger.info(f"Loading config from: {config_path}")
    
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        logger.info("Config loaded successfully")
    else:
        logger.warning("No config file found, using defaults")
        config = {
            "db2_agent": {"enabled": False},
            "repo_agent": {"enabled": False}
        }
    
    # Register agents
    logger.info("Registering agents...")
    
    # DB2 Monitoring Agent
    if config.get('db2_agent', {}).get('enabled', False):
        try:
            logger.info("Initializing DB2 agent...")
            db2_agent = DB2MonitoringAgent(config.get('db2_agent', {}))
            orchestrator.register_agent(db2_agent)
            logger.info("DB2 agent registered")
        except Exception as e:
            logger.error(f"Failed to register DB2 agent: {e}", exc_info=True)
    else:
        logger.info("DB2 agent disabled")
    
    # Repository Analyzer Agent
    if config.get('repo_agent', {}).get('enabled', False):
        try:
            logger.info("Initializing Repository agent...")
            repo_agent = RepositoryAnalyzerAgent(config.get('repo_agent', {}))
            orchestrator.register_agent(repo_agent)
            logger.info("Repository agent registered")
        except Exception as e:
            logger.error(f"Failed to register repo analyzer agent: {e}", exc_info=True)
    else:
        logger.info("Repository agent disabled")
    
    logger.info(f"Registered {len(orchestrator.agents)} agents")
    logger.info("Agent Hub Platform ready!")
    logger.info("Startup complete!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Agent Hub Platform!",
        "version": "1.0.0",
        "docs": "/docs",
        "agents": len(orchestrator.agents)
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agents": len(orchestrator.agents),
        "registered_agents": [agent.name for agent in orchestrator.agents]
    }


@app.get("/agents")
async def list_agents():
    """List all registered agents."""
    return {
        "agents": orchestrator.list_agents(),
        "total": len(orchestrator.agents)
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Process a query.
    
    Args:
        request: Query request
        
    Returns:
        Query response
    """
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Build extra params for agents
    extra_params = {}
    if request.batch_id:
        extra_params['batch_id'] = request.batch_id
    if request.output_format:
        extra_params['output_format'] = request.output_format
    
    # Process query with extra params
    response = await orchestrator.process(request.query, session_id, extra_params=extra_params)
    
    return QueryResponse(
        status=response.status,
        message=response.message,
        data=response.data,
        response_type=response.response_type,
        metadata=response.metadata,
        timestamp=response.timestamp,
        session_id=session_id,
        batch_id=request.batch_id,
        output_format=request.output_format
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    logger.info(f"WebSocket connected: {session_id}")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            query = data.get('query', '')
            batch_id = data.get('batch_id')
            output_format = data.get('output_format')
            
            if not query:
                await websocket.send_json({
                    "error": "No query provided"
                })
                continue
            
            # Build extra params
            extra_params = {}
            if batch_id:
                extra_params['batch_id'] = batch_id
            if output_format:
                extra_params['output_format'] = output_format
            
            # Process query
            response = await orchestrator.process(query, session_id, extra_params=extra_params)
            
            # Send response
            await websocket.send_json({
                "status": response.status,
                "message": response.message,
                "data": response.data,
                "response_type": response.response_type,
                "metadata": response.metadata,
                "timestamp": response.timestamp
            })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        orchestrator.clear_context(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "error": str(e)
            })
        except:
            pass


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session context."""
    orchestrator.clear_context(session_id)
    return {"message": f"Session {session_id} cleared"}


if __name__ == "__main__":
    import uvicorn
    
    # Use app directly instead of string reference to avoid module resolution issues
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Reload doesn't work well when running script directly
        log_level="info"
    )
