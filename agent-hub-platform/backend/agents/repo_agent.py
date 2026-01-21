"""Repository analysis agent."""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import re
import json

from .base import BaseAgent, AgentResponse

# Add repo-flow-analyzer to path
REPO_ANALYZER_PATH = Path(__file__).parent.parent.parent.parent / "repo-flow-analyzer"
sys.path.insert(0, str(REPO_ANALYZER_PATH))

try:
    from analyzer import RepoAnalyzer
    from models import AnalysisResult
    ANALYZER_AVAILABLE = True
except ImportError as e:
    ANALYZER_AVAILABLE = False
    print(f"Warning: Could not import repository analyzer modules: {e}")


class RepositoryAnalyzerAgent(BaseAgent):
    """Agent for repository analysis and code insights.
    
    Handles queries like:
    - "Analyze repository at /path/to/repo"
    - "What dependencies does this repo have?"
    - "Show me the code structure"
    - "Generate documentation for this codebase"
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(name="repo_analyzer", config=config)
        
        if not ANALYZER_AVAILABLE:
            self.logger.warning("Repository analyzer modules not available")
        
        self.default_analysis_depth = config.get('default_analysis_depth', 'full')
        self.output_formats = config.get('output_formats', ['json', 'markdown'])
    
    def get_keywords(self) -> List[str]:
        return [
            'repository', 'repo', 'code', 'codebase', 'analyze',
            'dependencies', 'structure', 'files', 'documentation',
            'language', 'tech stack', 'architecture'
        ]
    
    def get_capabilities(self) -> List[str]:
        return [
            "Analyze repository structure and organization",
            "Detect programming languages and frameworks",
            "Extract and analyze dependencies",
            "Generate documentation from code",
            "Assess code quality metrics",
            "Identify tech stack and architecture patterns"
        ]
    
    def get_help(self) -> str:
        return """
**Repository Analyzer Agent**

I can analyze codebases and provide insights about your repositories!

**Example Questions:**
- "Analyze the repository at C:\\path\\to\\repo"
- "What dependencies does this repo have?"
- "Show me the code structure"
- "What programming languages are used?"
- "Generate documentation for this codebase"
- "What's the tech stack?"
- "Assess code quality"

**Capabilities:**
- Language and framework detection
- Dependency analysis
- Code structure mapping
- Documentation generation
- Quality metrics
- Tech stack identification
        """.strip()
    
    def can_handle(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this agent can handle the request."""
        if not self.enabled:
            return 0.0
        
        user_input_lower = user_input.lower()
        
        # Repository keywords
        repo_keywords = ['repository', 'repo', 'code', 'codebase']
        repo_score = sum(2 for kw in repo_keywords if kw in user_input_lower)
        
        # Analysis keywords
        analysis_keywords = ['analyze', 'check', 'scan', 'review', 'inspect']
        analysis_score = sum(1 for kw in analysis_keywords if kw in user_input_lower)
        
        # Feature keywords
        feature_keywords = ['dependencies', 'structure', 'documentation', 'language', 'tech stack']
        feature_score = sum(1.5 for kw in feature_keywords if kw in user_input_lower)
        
        # Path detection (likely repo path)
        path_score = 2 if re.search(r'[/\\]|C:', user_input) else 0
        
        total_score = repo_score + analysis_score + feature_score + path_score
        
        # Normalize to 0-1 range
        confidence = min(total_score / 6.0, 1.0)
        
        return confidence
    
    def _extract_path(self, user_input: str) -> Optional[str]:
        """Extract repository path from user input."""
        # Look for paths in common formats
        patterns = [
            r'([A-Za-z]:[/\\][^\s]+)',  # Windows absolute path
            r'(/[^\s]+)',                # Unix absolute path
            r'(\.\.?/[^\s]+)',          # Relative path
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                path = match.group(1)
                # Clean up common trailing characters
                path = path.rstrip('.,;:"\'')
                if Path(path).exists():
                    return path
        
        return None
    
    async def execute(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute repository analysis."""
        if not ANALYZER_AVAILABLE:
            return AgentResponse(
                status="error",
                message="Repository analyzer modules not available",
                data={"error": "Required modules not found. Please check installation."},
                response_type="text"
            )
        
        # Extract repository path
        repo_path = self._extract_path(user_input)
        
        # Check context for previously analyzed repo
        if not repo_path and context and 'last_repo_path' in context:
            repo_path = context['last_repo_path']
        
        if not repo_path:
            return AgentResponse(
                status="error",
                message="Please provide a repository path to analyze.\n\nExample: 'Analyze repository at C:\\\\path\\\\to\\\\repo'",
                response_type="text"
            )
        
        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            return AgentResponse(
                status="error",
                message=f"Repository path not found: {repo_path}",
                response_type="text"
            )
        
        try:
            # Analyze repository
            self.logger.info(f"Analyzing repository: {repo_path}")
            
            # Initialize analyzer with Path object
            analyzer = RepoAnalyzer(repo_path_obj)
            analysis_result = analyzer.analyze()
            
            # Get summary statistics
            summary_stats = analyzer.get_analysis_summary()
            
            # Build summary message
            summary_parts = [
                f"✅ **Repository Analysis Complete**: `{repo_path_obj.name}`",
                "",
                f"**📊 Overview:**",
                f"- Total Services: {summary_stats.get('total_services', 0)}",
                f"- REST Endpoints: {summary_stats.get('total_endpoints', 0)}",
                f"- Kafka Flows: {summary_stats.get('total_kafka_flows', 0)}",
                f"- Database Connections: {summary_stats.get('total_databases', 0)}",
                f"- Data Models: {summary_stats.get('total_data_models', 0)}",
                f"- Service Dependencies: {summary_stats.get('total_dependencies', 0)}",
            ]
            
            message = "\n".join(summary_parts)
            
            # Convert AnalysisResult to dictionary for JSON serialization
            results_dict = {
                'summary': summary_stats,
                'services': [s.__dict__ for s in analysis_result.services],
                'rest_endpoints': [e.__dict__ for e in analysis_result.rest_endpoints],
                'kafka_flows': [k.__dict__ for k in analysis_result.kafka_flows],
                'database_connections': [d.__dict__ for d in analysis_result.database_connections],
                'data_models': [m.__dict__ for m in analysis_result.data_models]
            }
            
            # Update context
            metadata = {
                "repo_path": repo_path,
                "repo_name": repo_path_obj.name
            }
            
            return AgentResponse(
                status="success",
                message=message,
                data=results_dict,
                response_type="markdown",
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Repository analysis failed: {e}", exc_info=True)
            return AgentResponse(
                status="error",
                message=f"Analysis failed: {str(e)}",
                data={"error": str(e), "repo_path": repo_path},
                response_type="text"
            )
