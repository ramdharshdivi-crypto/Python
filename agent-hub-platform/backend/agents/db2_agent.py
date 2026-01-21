"""DB2 and Kubernetes monitoring agent."""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import re

from .base import BaseAgent, AgentResponse

# Add db2-monitoring-agent to path
# Check multiple possible locations for the db2-monitoring-agent
_possible_paths = [
    Path(__file__).parent.parent.parent.parent / "db2-monitoring-agent",  # Original relative path
    Path.home() / "OneDrive - Walmart Inc" / "Documents" / "db2-monitoring-agent",  # OneDrive location
    Path.home() / "Documents" / "db2-monitoring-agent",  # Standard Documents folder
    Path(os.environ.get("DB2_MONITORING_AGENT_PATH", "")) if os.environ.get("DB2_MONITORING_AGENT_PATH") else None,  # Environment variable
]

DB2_AGENT_PATH = None
for path in _possible_paths:
    if path and path.exists() and (path / "src").exists():
        DB2_AGENT_PATH = path
        break

if DB2_AGENT_PATH:
    sys.path.insert(0, str(DB2_AGENT_PATH / "src"))

try:
    from db2_checker import check_db2_health, is_db2_available
    from k8s_checker import check_k8s_health
    DB2_AVAILABLE = True
except ImportError as e:
    DB2_AVAILABLE = False
    _searched_paths = [str(p) for p in _possible_paths if p]
    print(f"Warning: Could not import DB2 monitoring modules: {e}")
    print(f"Searched paths: {_searched_paths}")
    if DB2_AGENT_PATH:
        print(f"Found DB2_AGENT_PATH at: {DB2_AGENT_PATH}")
    else:
        print("DB2_AGENT_PATH not found in any of the searched locations.")


class DB2MonitoringAgent(BaseAgent):
    """Agent for DB2 database and Kubernetes monitoring.
    
    Handles queries like:
    - "Check DB2 health"
    - "What's the database status?"
    - "Show me kubernetes pods"
    - "Are my pods running?"
    - "Check database response time"
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(name="db2_monitoring", config=config)
        
        if not DB2_AVAILABLE:
            self.logger.warning("DB2 monitoring modules not available")
        
        self.db2_config = config.get('db2', {})
        self.k8s_config = config.get('kubernetes', {})
    
    def get_keywords(self) -> List[str]:
        return [
            'db2', 'database', 'db', 'sql', 'query',
            'kubernetes', 'k8s', 'pod', 'pods', 'container',
            'health', 'status', 'check', 'monitor',
            'response time', 'connection', 'restart'
        ]
    
    def get_capabilities(self) -> List[str]:
        return [
            "Check DB2 database health and connectivity",
            "Execute DB2 queries and measure response time",
            "Monitor Kubernetes pod status",
            "Check pod restarts and health",
            "View container states"
        ]
    
    def get_help(self) -> str:
        return """
**DB2 & Kubernetes Monitoring Agent**

I can help you monitor your DB2 database and Kubernetes infrastructure!

**🗃️ DB2 Database Queries:**
- "Check DB2 status"
- "What's the batch status?"
- "Check database health"
- "Query order status"
- "Check batch 12345 status"

**☸️ Kubernetes Queries:**
- "Show me all pods in kubernetes"
- "Are my pods running ok?"
- "Check pod restart counts"
- "What's the k8s deployment status?"

**Note:** DB2 and Kubernetes are checked separately based on your query.
- Batch/order/database queries → DB2 only
- Pod/container/k8s queries → Kubernetes only

**Capabilities:**
- DB2 health checks with query results display
- Batch status queries with row-level details
- Response time monitoring
- Kubernetes pod status
- Container health checks
        """.strip()
    
    def can_handle(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent can handle the request."""
        if not self.enabled:
            return 0.0
        
        context = context or {}
        user_input_lower = user_input.lower()
        
        # Check if batch_id is in context - this is a strong signal for DB2
        has_batch_id = bool(context.get('batch_id'))
        
        # DB2/database keywords (includes batch for batch status queries)
        db_keywords = ['db2', 'database', 'db', 'sql', 'query', 'connection', 'batch', 'order']
        db_score = sum(1 for kw in db_keywords if kw in user_input_lower)
        
        # Kubernetes keywords
        k8s_keywords = ['kubernetes', 'k8s', 'pod', 'pods', 'container', 'deployment', 'namespace']
        k8s_score = sum(1 for kw in k8s_keywords if kw in user_input_lower)
        
        # Action keywords
        action_keywords = ['health', 'status', 'check', 'monitor', 'show', 'list']
        has_action = any(kw in user_input_lower for kw in action_keywords)
        
        # If batch_id is provided in context, this is definitely a DB2 query
        if has_batch_id:
            db_score += 2  # Strong boost for DB2 when batch_id is provided
            self.logger.debug(f"batch_id detected in context, boosting DB2 score")
        
        # Only return confidence if we have domain-specific keywords OR batch_id
        if db_score == 0 and k8s_score == 0:
            return 0.0
        
        # Calculate score based on domain keywords + action bonus
        total_score = db_score + k8s_score
        if has_action:
            total_score += 0.5
        
        # Normalize to 0-1 range
        confidence = min(total_score / 4.0, 1.0)
        
        return confidence
    
    async def execute(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute monitoring task."""
        if not DB2_AVAILABLE:
            return AgentResponse(
                status="error",
                message="DB2 monitoring modules not available",
                data={"error": "Required modules not found. Please check installation."},
                response_type="text"
            )
        
        context = context or {}
        user_input_lower = user_input.lower()
        
        # Extract batch_id and output_format from context
        batch_id = context.get('batch_id')
        output_format = context.get('output_format', 'json')  # default to json
        
        # Determine what to check - DB2 and K8s are now ISOLATED
        # DB2 keywords include batch/order for batch status queries
        db_keywords = ['db2', 'database', 'db', 'sql', 'batch', 'order']
        k8s_keywords = ['kubernetes', 'k8s', 'pod', 'pods', 'container', 'deployment', 'namespace']
        
        check_db2 = any(kw in user_input_lower for kw in db_keywords)
        check_k8s = any(kw in user_input_lower for kw in k8s_keywords)
        
        # If batch_id is provided, force DB2 check (batch queries always go to DB2)
        if batch_id:
            check_db2 = True
            self.logger.info(f"batch_id provided ({batch_id}), forcing DB2 check")
        
        # If neither is detected and no batch_id, default to DB2
        if not check_db2 and not check_k8s:
            self.logger.warning("No specific domain detected, defaulting to DB2 check")
            check_db2 = True
        
        results = {}
        overall_status = "healthy"
        messages = []
        
        # Check DB2
        if check_db2 and self.db2_config:
            try:
                # Make a copy of config to avoid modifying original
                db2_config_copy = self.db2_config.copy()
                
                # Substitute {batch_id} placeholder in query if batch_id provided
                if batch_id and 'query' in db2_config_copy:
                    original_query = db2_config_copy['query']
                    db2_config_copy['query'] = original_query.replace('{batch_id}', str(batch_id))
                    self.logger.info(f"Using batch_id: {batch_id}")
                elif '{batch_id}' in db2_config_copy.get('query', ''):
                    self.logger.warning("Query contains {batch_id} placeholder but no batch_id provided!")
                
                db2_result = check_db2_health(db2_config_copy)
                results['db2'] = db2_result
                
                # Add batch_id to results for transparency
                if batch_id:
                    results['db2']['batch_id_used'] = batch_id
                
                if db2_result['status'] == 'healthy':
                    messages.append(f"✅ **DB2 Database**: Healthy (Response time: {db2_result['response_time_ms']}ms)")
                    
                    # Show query results if available (for batch status queries)
                    query_results = db2_result.get('query_results', [])
                    row_count = db2_result.get('row_count', 0)
                    
                    if query_results and row_count > 0:
                        messages.append(f"\n📊 **Query Results**: {row_count} row(s) returned\n")
                        
                        # Format results as a readable table
                        if row_count <= 20:  # Show all rows if <= 20
                            for i, row in enumerate(query_results, 1):
                                row_str = " | ".join([f"**{k}**: {v}" for k, v in row.items()])
                                messages.append(f"{i}. {row_str}")
                        else:  # Summarize if too many rows
                            messages.append(f"*Showing first 10 of {row_count} rows:*")
                            for i, row in enumerate(query_results[:10], 1):
                                row_str = " | ".join([f"**{k}**: {v}" for k, v in row.items()])
                                messages.append(f"{i}. {row_str}")
                            messages.append(f"... and {row_count - 10} more rows")
                    elif row_count == 0:
                        messages.append("\n📊 **Query Results**: No rows returned")
                else:
                    messages.append(f"❌ **DB2 Database**: {db2_result['status'].upper()} - {db2_result.get('details', '')}")
                    overall_status = "unhealthy"
            except Exception as e:
                self.logger.error(f"DB2 check failed: {e}")
                results['db2'] = {"error": str(e)}
                messages.append(f"❌ **DB2 Database**: Error - {str(e)}")
                overall_status = "error"
        
        # Check Kubernetes
        if check_k8s and self.k8s_config:
            try:
                k8s_result = check_k8s_health(self.k8s_config)
                results['kubernetes'] = k8s_result
                
                if k8s_result['status'] == 'healthy':
                    messages.append(
                        f"✅ **Kubernetes**: {k8s_result['healthy_pods']}/{k8s_result['total_pods']} pods healthy"
                    )
                else:
                    messages.append(
                        f"⚠️ **Kubernetes**: {k8s_result['status'].upper()} - "
                        f"{k8s_result['healthy_pods']}/{k8s_result['total_pods']} pods healthy"
                    )
                    if overall_status == "healthy":
                        overall_status = "degraded"
            except Exception as e:
                self.logger.error(f"K8s check failed: {e}")
                results['kubernetes'] = {"error": str(e)}
                messages.append(f"❌ **Kubernetes**: Error - {str(e)}")
                overall_status = "error"
        
        # Build response
        message = "\n".join(messages) if messages else "No checks performed"
        
        # Add batch_id info to message if provided
        if batch_id:
            message = f"🔍 **Batch ID**: {batch_id}\n\n" + message
        
        # Determine response type based on output_format or user input
        if output_format == 'text':
            response_type = "text"
        elif output_format == 'json':
            response_type = "json"
        elif "show" in user_input_lower or "list" in user_input_lower:
            response_type = "table"
        else:
            response_type = "markdown"
        
        return AgentResponse(
            status="success" if overall_status in ["healthy", "degraded"] else "error",
            message=message,
            data=results,
            response_type=response_type,
            metadata={
                "overall_status": overall_status,
                "checks_performed": list(results.keys()),
                "batch_id": batch_id,
                "output_format": output_format
            }
        )
