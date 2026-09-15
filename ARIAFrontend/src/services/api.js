import axios from 'axios';

const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://127.0.0.1:8080';

const client = axios.create({
  baseURL: GATEWAY_URL,
  timeout: 60000, // 60 seconds timeout for full AI cognitive planning
});

/**
 * Send text command to ARIA Gateway API
 */
export const sendTextCommand = async (command, language = 'auto') => {
  try {
    const response = await client.post('/api/gateway/command/text', {
      command: command.trim(),
      language: language,
    });
    return response.data;
  } catch (err) {
    if (err.response?.data) {
      return err.response.data;
    }
    return {
      command: command,
      intent: 'unknown',
      status: 'offline',
      executed_by: 'gateway',
      steps_completed: 0,
      response: `Gateway connection error: ${err.message}. Ensure Gateway is running on Port 8080.`,
      time: '0.0s',
      error: err.message,
    };
  }
};

/**
 * Send recorded audio blob to ARIA Gateway API
 */
export const sendAudioCommand = async (audioBlob, filename = 'command.wav') => {
  try {
    const formData = new FormData();
    formData.append('file', audioBlob, filename);
    // Also append 'audio' in case gateway reads audio key
    formData.append('audio', audioBlob, filename);

    const response = await client.post('/api/gateway/command/audio', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (err) {
    if (err.response?.data) {
      return err.response.data;
    }
    return {
      command: '[Voice Command]',
      intent: 'unknown',
      status: 'offline',
      executed_by: 'gateway',
      steps_completed: 0,
      response: `Gateway connection error: ${err.message}.`,
      time: '0.0s',
      error: err.message,
    };
  }
};

/**
 * Fetch status of all 5 subsystem APIs and Ollama
 */
export const getSystemStatus = async () => {
  try {
    const response = await client.get('/api/gateway/status', { timeout: 12000 });
    return response.data;
  } catch (err) {
    return {
      gateway: 'offline',
      apis: {
        speech_api: { status: 'offline', port: 8000 },
        brain_api: { status: 'offline', port: 8001 },
        browser_api: { status: 'offline', port: 8002 },
        desktop_api: { status: 'offline', port: 8003 },
        file_api: { status: 'offline', port: 8004 },
      },
      ollama: 'disconnected',
    };
  }
};

/**
 * Fetch last 50 executed commands history
 */
export const getHistory = async (limit = 50) => {
  try {
    const response = await client.get(`/api/gateway/history?limit=${limit}`, { timeout: 4000 });
    return response.data;
  } catch (err) {
    return { total: 0, history: [] };
  }
};

export default {
  sendTextCommand,
  sendAudioCommand,
  getSystemStatus,
  getHistory,
};
