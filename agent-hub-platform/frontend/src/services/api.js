import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Send a query to the backend
 * @param {string} query - User's query
 * @param {string} sessionId - Session ID for context
 * @param {object} options - Additional options (batch_id, output_format)
 * @returns {Promise<object>} - Response from backend
 */
export const sendQuery = async (query, sessionId = null, options = {}) => {
  try {
    const response = await api.post('/query', {
      query,
      session_id: sessionId,
      batch_id: options.batchId || null,
      output_format: options.outputFormat || null,
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.response?.data?.message || 
      'Failed to send query'
    );
  }
};

/**
 * Get list of available agents
 * @returns {Promise<object>} - List of agents
 */
export const getAgents = async () => {
  try {
    const response = await api.get('/agents');
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error('Failed to get agents');
  }
};

/**
 * Health check
 * @returns {Promise<object>} - Health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error('Failed to check health');
  }
};

/**
 * Clear session context
 * @param {string} sessionId - Session ID to clear
 * @returns {Promise<object>} - Response
 */
export const clearSession = async (sessionId) => {
  try {
    const response = await api.delete(`/session/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error('Failed to clear session');
  }
};

export default api;
