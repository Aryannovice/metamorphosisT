/**
 * DataHaven Service - Express Microservice
 * 
 * This service wraps the DataHaven SDK and exposes REST endpoints
 * for the Python backend to consume.
 * 
 * Endpoints:
 *   GET  /policy/:userId     - Fetch user's policy configuration
 *   GET  /userdata/:userId   - Fetch authorized user data (metadata only)
 *   POST /log                - Log inference metadata (no raw prompts/PII)
 *   GET  /health             - Health check
 * 
 * IMPORTANT: This service NEVER receives raw prompts or PII.
 * Only metadata and policy information flows through here.
 */

import express from 'express';
import cors from 'cors';
import { v4 as uuidv4 } from 'uuid';

const app = express();
const PORT = process.env.DATAHAVEN_PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// ═══════════════════════════════════════════════════════════════════
// DataHaven SDK Integration Layer
// ═══════════════════════════════════════════════════════════════════

/**
 * Mock DataHaven SDK client.
 * 
 * Replace this with actual DataHaven SDK when available:
 *   import { DataHavenClient } from 'datahaven-sdk';
 *   const client = new DataHavenClient({ apiKey: process.env.DATAHAVEN_API_KEY });
 */
class DataHavenClient {
  constructor(config = {}) {
    this.apiKey = config.apiKey || process.env.DATAHAVEN_API_KEY || 'mock-key';
    this.baseUrl = config.baseUrl || process.env.DATAHAVEN_URL || 'https://api.datahaven.io';
    console.log(`[DataHaven] Initialized client (mock mode)`);
  }

  /**
   * Fetch policy for a user.
   * In production, this calls DataHaven's policy API.
   */
  async getPolicy(userId) {
    // Production implementation:
    // const response = await fetch(`${this.baseUrl}/v1/policies/${userId}`, {
    //   headers: { 'Authorization': `Bearer ${this.apiKey}` }
    // });
    // return response.json();

    // Mock implementation with sensible defaults
    const policies = {
      'enterprise-user': {
        mode: 'STRICT',
        allow_cloud: false,
        max_tokens: 2048,
        require_pii_masking: true,
        compression_enabled: true,
        whitelisted_providers: ['local']
      },
      'standard-user': {
        mode: 'BALANCED',
        allow_cloud: true,
        max_tokens: 4096,
        require_pii_masking: true,
        compression_enabled: true,
        whitelisted_providers: ['local', 'groq']
      },
      'power-user': {
        mode: 'PERFORMANCE',
        allow_cloud: true,
        max_tokens: 8192,
        require_pii_masking: true,
        compression_enabled: false,
        whitelisted_providers: ['local', 'groq', 'openai']
      }
    };

    return policies[userId] || {
      mode: 'BALANCED',
      allow_cloud: true,
      max_tokens: 4096,
      require_pii_masking: true,
      compression_enabled: true,
      whitelisted_providers: ['local', 'groq', 'openai']
    };
  }

  /**
   * Fetch authorized user data/metadata.
   * In production, this retrieves user context from DataHaven vault.
   */
  async getUserData(userId) {
    // Production implementation:
    // const response = await fetch(`${this.baseUrl}/v1/users/${userId}/data`, {
    //   headers: { 'Authorization': `Bearer ${this.apiKey}` }
    // });
    // return response.json();

    // Mock implementation
    return {
      user_id: userId,
      tier: 'standard',
      organization: 'default',
      created_at: new Date().toISOString(),
      preferences: {
        default_mode: 'BALANCED',
        preferred_provider: 'groq'
      },
      quotas: {
        requests_per_day: 1000,
        requests_used: 0,
        tokens_per_day: 100000,
        tokens_used: 0
      }
    };
  }

  /**
   * Log inference metadata to DataHaven for compliance.
   * IMPORTANT: Never send raw prompts or PII here.
   */
  async logInference(logEntry) {
    // Production implementation:
    // const response = await fetch(`${this.baseUrl}/v1/logs`, {
    //   method: 'POST',
    //   headers: {
    //     'Authorization': `Bearer ${this.apiKey}`,
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify(logEntry)
    // });
    // return response.json();

    // Mock implementation - just validate and echo
    const logId = uuidv4();
    console.log(`[DataHaven] Logged inference: ${logId}`, {
      request_id: logEntry.request_id,
      route: logEntry.route,
      provider: logEntry.provider,
      token_count: logEntry.token_count
    });

    return {
      log_id: logId,
      status: 'stored',
      timestamp: new Date().toISOString()
    };
  }
}

// Initialize client
const dataHavenClient = new DataHavenClient();

// ═══════════════════════════════════════════════════════════════════
// REST Endpoints
// ═══════════════════════════════════════════════════════════════════

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'datahaven-service',
    timestamp: new Date().toISOString()
  });
});

/**
 * GET /policy/:userId
 * Fetch policy configuration for a user
 */
app.get('/policy/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const policy = await dataHavenClient.getPolicy(userId);
    res.json({
      success: true,
      user_id: userId,
      policy
    });
  } catch (error) {
    console.error('[DataHaven] Policy fetch error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch policy',
      message: error.message
    });
  }
});

/**
 * GET /userdata/:userId
 * Fetch authorized user data/metadata
 */
app.get('/userdata/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const userData = await dataHavenClient.getUserData(userId);
    res.json({
      success: true,
      data: userData
    });
  } catch (error) {
    console.error('[DataHaven] User data fetch error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch user data',
      message: error.message
    });
  }
});

/**
 * POST /log
 * Log inference metadata for compliance
 * 
 * Expected body:
 * {
 *   request_id: string,
 *   user_id: string (optional),
 *   route: string,
 *   provider: string,
 *   model: string,
 *   token_count: number,
 *   latency_ms: number,
 *   privacy_level: string,
 *   cost_estimate: number,
 *   policy_mode: string,
 *   timestamp: string
 * }
 */
app.post('/log', async (req, res) => {
  try {
    // Validate required fields
    const requiredFields = ['request_id', 'route', 'provider'];
    for (const field of requiredFields) {
      if (!req.body[field]) {
        return res.status(400).json({
          success: false,
          error: `Missing required field: ${field}`
        });
      }
    }

    // Ensure no PII/prompt data is included
    const sanitizedEntry = {
      request_id: req.body.request_id,
      user_id: req.body.user_id || 'anonymous',
      route: req.body.route,
      provider: req.body.provider,
      model: req.body.model || '',
      token_count: req.body.token_count || 0,
      latency_ms: req.body.latency_ms || 0,
      privacy_level: req.body.privacy_level || 'BALANCED',
      cost_estimate: req.body.cost_estimate || 0,
      policy_mode: req.body.policy_mode || 'BALANCED',
      timestamp: req.body.timestamp || new Date().toISOString()
    };

    const result = await dataHavenClient.logInference(sanitizedEntry);
    res.json({
      success: true,
      ...result
    });
  } catch (error) {
    console.error('[DataHaven] Log error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to log inference',
      message: error.message
    });
  }
});

// ═══════════════════════════════════════════════════════════════════
// Start Server
// ═══════════════════════════════════════════════════════════════════

app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║           DataHaven Service Started                         ║
╠════════════════════════════════════════════════════════════╣
║  Port: ${PORT}                                               ║
║  Mode: ${process.env.NODE_ENV || 'development'}                                     ║
║                                                              ║
║  Endpoints:                                                  ║
║    GET  /health           - Health check                     ║
║    GET  /policy/:userId   - Fetch user policy                ║
║    GET  /userdata/:userId - Fetch user data                  ║
║    POST /log              - Log inference metadata           ║
╚════════════════════════════════════════════════════════════╝
  `);
});

export default app;
