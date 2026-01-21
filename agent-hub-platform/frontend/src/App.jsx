import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Collapse,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import ClearIcon from '@mui/icons-material/Clear';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

import { sendQuery } from './services/api';
import MessageList from './components/MessageList';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [batchId, setBatchId] = useState('');
  const [outputFormat, setOutputFormat] = useState('json');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Generate session ID on mount
  useEffect(() => {
    const sid = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(sid);
    
    // Add welcome message
    setMessages([{
      id: 'welcome',
      type: 'agent',
      message: '👋 **Welcome to Agent Hub!**\n\nI can help you with:\n\n' +
               '🗄️ **DB2 & Kubernetes Monitoring**\n' +
               '📊 **Repository Analysis**\n\n' +
               'Try asking: "Check DB2 health" or "Help"',
      timestamp: new Date().toISOString(),
      response_type: 'markdown'
    }]);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || loading) return;

    const userMessage = {
      id: `msg-${Date.now()}`,
      type: 'user',
      message: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await sendQuery(input, sessionId, {
        batchId: batchId || null,
        outputFormat: outputFormat || null,
      });
      
      const agentMessage = {
        id: `resp-${Date.now()}`,
        type: 'agent',
        message: response.message,
        data: response.data,
        timestamp: response.timestamp,
        response_type: response.response_type,
        metadata: response.metadata,
        status: response.status
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'An error occurred');
      
      const errorMessage = {
        id: `error-${Date.now()}`,
        type: 'agent',
        message: `❌ **Error**: ${err.message || 'Could not process your request'}`,
        timestamp: new Date().toISOString(),
        response_type: 'markdown',
        status: 'error'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setError(null);
  };

  const handleExampleQuery = (query) => {
    setInput(query);
  };

  const exampleQueries = [
    'Check DB2 health',
    'Show kubernetes pods',
    'Check batch status',
    'Help',
  ];

  return (
    <Box sx={{ flexGrow: 1, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <AppBar position="static" sx={{ background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)' }}>
        <Toolbar>
          <SmartToyIcon sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Agent Hub Platform
          </Typography>
          <IconButton color="inherit" onClick={handleClear} title="Clear conversation">
            <ClearIcon />
          </IconButton>
          <IconButton 
            color="inherit" 
            onClick={() => handleExampleQuery('Help')}
            title="Show help"
          >
            <HelpOutlineIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container 
        maxWidth="lg" 
        sx={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          py: 3,
          overflow: 'hidden'
        }}
      >
        {/* Example Queries */}
        {messages.length <= 1 && (
          <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
            <Typography variant="body2" sx={{ width: '100%', textAlign: 'center', mb: 1, color: 'text.secondary' }}>
              Try these examples:
            </Typography>
            {exampleQueries.map((query, idx) => (
              <Chip
                key={idx}
                label={query}
                onClick={() => handleExampleQuery(query)}
                color="primary"
                variant="outlined"
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
        )}

        {/* Error Alert */}
        {error && (
          <Alert 
            severity="error" 
            onClose={() => setError(null)}
            sx={{ mb: 2 }}
          >
            {error}
          </Alert>
        )}

        {/* Messages */}
        <Paper 
          elevation={3} 
          sx={{ 
            flexGrow: 1, 
            p: 2, 
            mb: 2, 
            overflow: 'auto',
            background: '#f5f7fa'
          }}
        >
          <MessageList messages={messages} />
          <div ref={messagesEndRef} />
        </Paper>

        {/* Input */}
        <Paper elevation={3} sx={{ p: 2 }}>
          <form onSubmit={handleSubmit}>
            {/* Advanced Options Toggle */}
            <Box 
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 1, 
                cursor: 'pointer',
                color: 'text.secondary'
              }}
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              <Typography variant="body2" sx={{ mr: 0.5 }}>
                Advanced Options
              </Typography>
              {showAdvanced ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
            </Box>
            
            {/* Advanced Options (Batch ID & Output Format) */}
            <Collapse in={showAdvanced}>
              <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                <TextField
                  label="Batch ID"
                  variant="outlined"
                  size="small"
                  placeholder="e.g., 368451"
                  value={batchId}
                  onChange={(e) => setBatchId(e.target.value)}
                  disabled={loading}
                  sx={{ minWidth: 150 }}
                  aria-label="Batch ID for DB2 query"
                />
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel id="output-format-label">Output Format</InputLabel>
                  <Select
                    labelId="output-format-label"
                    id="output-format-select"
                    value={outputFormat}
                    label="Output Format"
                    onChange={(e) => setOutputFormat(e.target.value)}
                    disabled={loading}
                  >
                    <MenuItem value="json">JSON</MenuItem>
                    <MenuItem value="text">Text</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Collapse>
            
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Ask me anything... (e.g., 'Check DB2 health', 'Analyze repository')" 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
                autoFocus
                multiline
                maxRows={4}
              />
              <Button
                type="submit"
                variant="contained"
                disabled={loading || !input.trim()}
                endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                sx={{ 
                  minWidth: 100,
                  height: 56,
                  background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)'
                }}
              >
                {loading ? 'Thinking...' : 'Send'}
              </Button>
            </Box>
          </form>
        </Paper>
      </Container>

      {/* Footer */}
      <Box 
        sx={{ 
          py: 2, 
          px: 3, 
          borderTop: '1px solid #e0e0e0',
          background: '#fafafa',
          textAlign: 'center'
        }}
      >
        <Typography variant="caption" color="text.secondary">
          Agent Hub Platform v1.0 🐶 | {sessionId ? `Session: ${sessionId.split('-')[1]}` : ''}
        </Typography>
      </Box>
    </Box>
  );
}

export default App;
