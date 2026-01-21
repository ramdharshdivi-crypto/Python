"""Base agent interface for all agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentResponse:
    """Standardized agent response format."""
    
    def __init__(
        self,
        status: str,
        message: str,
        data: Optional[Any] = None,
        response_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize agent response.
        
        Args:
            status: "success", "error", "warning", "info"
            message: Human-readable message
            data: Response data (can be dict, list, str, etc.)
            response_type: "text", "table", "chart", "json", "markdown"
            metadata: Additional metadata
        """
        self.status = status
        self.message = message
        self.data = data
        self.response_type = response_type
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat() + 'Z'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "response_type": self.response_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """Base class for all agents.
    
    All agents must inherit from this class and implement:
    - can_handle(): Determine if agent can handle the request
    - execute(): Execute the agent's task
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize base agent.
        
        Args:
            name: Agent name (unique identifier)
            config: Agent configuration dictionary
        """
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    def can_handle(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent can handle the request.
        
        Args:
            user_input: User's natural language input
            context: Optional context from previous interactions
            
        Returns:
            Confidence score (0.0 to 1.0). Higher = more confident.
            0.0 means agent cannot handle this request.
        """
        pass
    
    @abstractmethod
    async def execute(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute the agent's task.
        
        Args:
            user_input: User's natural language input
            context: Optional context from previous interactions
            
        Returns:
            AgentResponse with results
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities.
        
        Returns:
            List of capability descriptions
        """
        return []
    
    def get_keywords(self) -> List[str]:
        """Get keywords this agent responds to.
        
        Returns:
            List of keywords
        """
        return []
    
    def get_help(self) -> str:
        """Get help text for this agent.
        
        Returns:
            Help text describing what the agent does and example queries
        """
        return f"Agent: {self.name}\nNo help available."
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})>"
