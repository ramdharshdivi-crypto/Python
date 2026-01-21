import React from 'react';
import { Box, Paper, Typography, Chip, Avatar } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MessageList = ({ messages }) => {
  const renderMessage = (message) => {
    const { response_type, data } = message;

    // Render based on response type
    if (response_type === 'markdown') {
      return (
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {message.message}
        </ReactMarkdown>
      );
    }

    if (response_type === 'table' && data) {
      return (
        <Box>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {message.message}
          </Typography>
          <Box sx={{ overflowX: 'auto' }}>
            <pre style={{ background: '#f5f5f5', padding: '12px', borderRadius: '4px' }}>
              {JSON.stringify(data, null, 2)}
            </pre>
          </Box>
        </Box>
      );
    }

    if (response_type === 'json' && data) {
      return (
        <Box>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {message.message}
          </Typography>
          <SyntaxHighlighter language="json" style={vscDarkPlus}>
            {JSON.stringify(data, null, 2)}
          </SyntaxHighlighter>
        </Box>
      );
    }

    // Default: plain text with markdown
    return (
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {message.message}
      </ReactMarkdown>
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <Box>
      {messages.map((message) => (
        <Box
          key={message.id}
          sx={{
            display: 'flex',
            justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
            mb: 2,
          }}
        >
          <Box
            sx={{
              maxWidth: '80%',
              display: 'flex',
              flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
              gap: 1,
            }}
          >
            {/* Avatar */}
            <Avatar
              sx={{
                bgcolor: message.type === 'user' ? '#667eea' : '#10b981',
                width: 36,
                height: 36,
              }}
            >
              {message.type === 'user' ? <PersonIcon /> : <SmartToyIcon />}
            </Avatar>

            {/* Message Content */}
            <Box sx={{ flexGrow: 1 }}>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: message.type === 'user' ? '#e3f2fd' : '#ffffff',
                  border: message.status === 'error' ? '1px solid #f44336' : 'none',
                }}
              >
                {/* Agent name and status */}
                {message.type === 'agent' && message.metadata?.agent && (
                  <Box sx={{ mb: 1, display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                    <Chip
                      label={message.metadata.agent}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                    {message.status && (
                      <Chip
                        label={message.status}
                        size="small"
                        color={getStatusColor(message.status)}
                      />
                    )}
                  </Box>
                )}

                {/* Message body */}
                <Box sx={{ '& p:last-child': { mb: 0 } }}>
                  {renderMessage(message)}
                </Box>

                {/* Timestamp */}
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: 'block', mt: 1, textAlign: message.type === 'user' ? 'right' : 'left' }}
                >
                  {new Date(message.timestamp).toLocaleTimeString()}
                </Typography>
              </Paper>
            </Box>
          </Box>
        </Box>
      ))}
    </Box>
  );
};

export default MessageList;
