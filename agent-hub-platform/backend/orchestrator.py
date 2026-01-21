"""Agent orchestration and routing logic."""

import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio

from agents.base import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple agents and routes requests.
    
    Responsibilities:
    - Maintain registry of available agents
    - Determine which agent(s) should handle a request
    - Execute agent tasks
    - Aggregate responses from multiple agents
    - Maintain conversation context
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.agents: List[BaseAgent] = []
        self.context_store: Dict[str, Dict[str, Any]] = {}  # session_id -> context
        self.logger = logging.getLogger("orchestrator")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent.
        
        Args:
            agent: Agent instance to register
        """
        if agent.enabled:
            self.agents.append(agent)
            self.logger.info(f"Registered agent: {agent.name}")
        else:
            self.logger.info(f"Skipped disabled agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent instance or None
        """
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents.
        
        Returns:
            List of agent info dictionaries
        """
        return [
            {
                "name": agent.name,
                "enabled": agent.enabled,
                "capabilities": agent.get_capabilities(),
                "keywords": agent.get_keywords()
            }
            for agent in self.agents
        ]
    
    def _select_agent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Optional[Tuple[BaseAgent, float]]:
        """Select the best agent for a request.
        
        Args:
            user_input: User's input
            context: Conversation context
            
        Returns:
            Tuple of (agent, confidence) or None if no agent can handle it
        """
        scores = []
        
        for agent in self.agents:
            confidence = agent.can_handle(user_input, context)
            if confidence > 0:
                scores.append((agent, confidence))
                self.logger.debug(f"Agent {agent.name} confidence: {confidence:.2f}")
        
        if not scores:
            return None
        
        # Return agent with highest confidence
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0]
    
    async def process(self, user_input: str, session_id: Optional[str] = None, extra_params: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process user input and route to appropriate agent.
        
        Args:
            user_input: User's natural language input
            session_id: Optional session ID for context
            extra_params: Optional dict with batch_id, output_format, etc.
            
        Returns:
            AgentResponse from the selected agent
        """
        # Get or create context
        context = self.context_store.get(session_id, {}) if session_id else {}
        
        # Merge extra params into context for agents to use
        if extra_params:
            context = {**context, **extra_params}
        
        self.logger.info(f"Processing: {user_input[:100]}...")
        
        # Handle meta commands
        if user_input.lower() in ['help', 'what can you do?', 'capabilities']:
            return self._handle_help()
        
        if user_input.lower().startswith('list agents'):
            return self._handle_list_agents()
        
        # Select agent
        agent_tuple = self._select_agent(user_input, context)
        
        if not agent_tuple:
            return AgentResponse(
                status="error",
                message="I'm not sure how to help with that. Try asking about:\n\n"
                        "- DB2 database health\n"
                        "- Kubernetes pod status\n"
                        "- Repository analysis\n\n"
                        "Or type 'help' to see all capabilities.",
                response_type="text"
            )
        
        agent, confidence = agent_tuple
        self.logger.info(f"Selected agent: {agent.name} (confidence: {confidence:.2f})")
        
        try:
            # Execute agent with context (includes batch_id, output_format if provided)
            response = await agent.execute(user_input, context)
            
            # Update context with response metadata
            if session_id and response.metadata:
                self.context_store.setdefault(session_id, {}).update(response.metadata)
            
            # Add agent info to metadata
            response.metadata['agent'] = agent.name
            response.metadata['confidence'] = confidence
            
            return response
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}", exc_info=True)
            return AgentResponse(
                status="error",
                message=f"Agent '{agent.name}' encountered an error: {str(e)}",
                data={"error": str(e)},
                response_type="text"
            )
    
    def _handle_help(self) -> AgentResponse:
        """Handle help request."""
        help_parts = [
            "# 🤖 Agent Hub - Available Agents\n",
            "I can help you with the following:\n"
        ]
        
        for agent in self.agents:
            help_parts.append(f"## {agent.name}")
            help_parts.append(agent.get_help())
            help_parts.append("")
        
        return AgentResponse(
            status="success",
            message="\n".join(help_parts),
            response_type="markdown"
        )
    
    def _handle_list_agents(self) -> AgentResponse:
        """Handle list agents request."""
        agent_info = self.list_agents()
        
        message_parts = ["**Available Agents:**\n"]
        for info in agent_info:
            message_parts.append(f"- **{info['name']}**: {', '.join(info['capabilities'][:2])}")
        
        return AgentResponse(
            status="success",
            message="\n".join(message_parts),
            data=agent_info,
            response_type="markdown"
        )
    
    def clear_context(self, session_id: str) -> None:
        """Clear context for a session.
        
        Args:
            session_id: Session ID
        """
        if session_id in self.context_store:
            del self.context_store[session_id]
            self.logger.info(f"Cleared context for session: {session_id}")
