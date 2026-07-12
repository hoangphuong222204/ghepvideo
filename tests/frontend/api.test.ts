/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { test, describe, before, beforeEach, afterEach, after } from 'node:test';
import assert from 'node:assert/strict';

import { ApiClient } from '../../src/api/client';
import { ApiError, ApiTimeoutError, ApiNetworkError, ApiCancellationError } from '../../src/api/errors';
import { HealthApiService } from '../../src/api/healthService';
import { CapabilityId } from '../../src/api/capabilities';

describe('Frontend API & Health Service Foundations', () => {
  let originalFetch: any;
  let fetchMock: any;

  before(() => {
    originalFetch = globalThis.fetch;
  });

  beforeEach(() => {
    fetchMock = null;
    globalThis.fetch = async (url: any, init: any) => {
      if (fetchMock) {
        return fetchMock(url, init);
      }
      return new Response(JSON.stringify({}), { status: 200 });
    };
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  after(() => {
    globalThis.fetch = originalFetch;
  });

  // 1. Successful JSON request
  test('Successful JSON request parses correctly and extracts metadata', async () => {
    const client = new ApiClient();
    const mockData = { result: 'ok', scenes: [1, 2] };
    
    fetchMock = async (url: string, init: any) => {
      const headers = new Headers({
        'Content-Type': 'application/json',
        'X-Correlation-ID': 'test-corr-123'
      });
      return new Response(JSON.stringify(mockData), {
        status: 200,
        headers
      });
    };

    const response = await client.request<{ result: string }>('/api/test');
    assert.equal(response.status, 200);
    assert.deepEqual(response.data, mockData);
    assert.equal(response.correlationId, 'test-corr-123');
    assert.equal(response.headers['x-correlation-id'], 'test-corr-123');
  });

  // 2. Network failure
  test('Network failure maps to ApiNetworkError', async () => {
    const client = new ApiClient();
    fetchMock = async () => {
      throw new Error('TypeError: Failed to fetch');
    };

    await assert.rejects(
      async () => {
        await client.request('/api/test');
      },
      (err: any) => {
        assert.ok(err instanceof ApiNetworkError);
        assert.equal(err.code, 'NETWORK_ERROR');
        assert.match(err.message, /Failed to fetch/);
        return true;
      }
    );
  });

  // 3. Timeout
  test('Request timeout throws ApiTimeoutError', async () => {
    const client = new ApiClient();
    
    fetchMock = async (url: string, init: any) => {
      return new Promise((resolve, reject) => {
        const checkAborted = () => {
          if (init.signal?.aborted) {
            const err = new Error('The user aborted a request.');
            err.name = 'AbortError';
            reject(err);
          } else {
            setTimeout(checkAborted, 5);
          }
        };
        checkAborted();
      });
    };

    await assert.rejects(
      async () => {
        await client.request('/api/test', { timeout: 10 });
      },
      (err: any) => {
        assert.ok(err instanceof ApiTimeoutError);
        assert.equal(err.status, 408);
        assert.equal(err.code, 'TIMEOUT');
        assert.match(err.message, /timed out after/);
        return true;
      }
    );
  });

  // 4. Cancellation
  test('Request cancellation throws ApiCancellationError', async () => {
    const client = new ApiClient();
    const abortController = new AbortController();

    fetchMock = async (url: string, init: any) => {
      return new Promise((resolve, reject) => {
        const checkAborted = () => {
          if (init.signal?.aborted) {
            const err = new Error('The user aborted a request.');
            err.name = 'AbortError';
            reject(err);
          } else {
            setTimeout(checkAborted, 5);
          }
        };
        checkAborted();
      });
    };

    // Cancel the request after 5ms
    setTimeout(() => {
      abortController.abort();
    }, 5);

    await assert.rejects(
      async () => {
        await client.request('/api/test', { signal: abortController.signal });
      },
      (err: any) => {
        assert.ok(err instanceof ApiCancellationError);
        assert.equal(err.status, 499);
        assert.equal(err.code, 'CANCELLED');
        assert.match(err.message, /cancelled by user/i);
        return true;
      }
    );
  });

  // 5. Correlation ID extraction
  test('Correlation ID is extracted from headers, falling back if not provided', async () => {
    const client = new ApiClient();
    
    // Header present
    fetchMock = async (url: string, init: any) => {
      const headers = new Headers({
        'Content-Type': 'application/json',
        'x-correlation-id': 'header-correlation-id'
      });
      return new Response(JSON.stringify({}), { status: 200, headers });
    };

    const resWithHeader = await client.request('/api/test');
    assert.equal(resWithHeader.correlationId, 'header-correlation-id');

    // Header missing, falls back to requested correlationId or generated
    fetchMock = async (url: string, init: any) => {
      return new Response(JSON.stringify({}), { status: 200 });
    };

    const resNoHeader = await client.request('/api/test', { correlationId: 'custom-requested-id' });
    assert.equal(resNoHeader.correlationId, 'custom-requested-id');
  });

  // 6. Safe API error mapping
  test('Safe API error mapping for non-ok responses', async () => {
    const client = new ApiClient();
    
    fetchMock = async () => {
      const headers = new Headers({ 'Content-Type': 'application/json' });
      return new Response(
        JSON.stringify({ error: 'Database conflict', code: 'DB_ERROR', details: 'Record 123 is locked' }),
        { status: 409, headers }
      );
    };

    await assert.rejects(
      async () => {
        await client.request('/api/test');
      },
      (err: any) => {
        assert.ok(err instanceof ApiError);
        assert.equal(err.status, 409);
        assert.equal(err.code, 'DB_ERROR');
        assert.equal(err.message, 'Database conflict');
        assert.deepEqual(err.details, { error: 'Database conflict', code: 'DB_ERROR', details: 'Record 123 is locked' });
        return true;
      }
    );
  });

  // 7. Capability mapping
  test('Capability mapping for fully online backend', async () => {
    const client = new ApiClient();
    const service = new HealthApiService(client);

    fetchMock = async () => {
      const healthData = {
        status: 'healthy',
        capabilities: {
          script_engine: { status: 'online', latency_ms: 12 },
          tts_engine: { status: 'online', latency_ms: 45 },
          subtitle_engine: { status: 'online', latency_ms: 5 },
          render_engine: { status: 'online', latency_ms: 110 },
          project_manager: { status: 'online', latency_ms: 2 }
        }
      };
      return new Response(JSON.stringify(healthData), {
        status: 200,
        headers: new Headers({ 'Content-Type': 'application/json' })
      });
    };

    const sysCaps = await service.checkHealth();
    assert.equal(sysCaps.overallStatus, 'fully_available');
    assert.equal(sysCaps.capabilities.script_engine.isAvailable, true);
    assert.equal(sysCaps.capabilities.script_engine.latencyMs, 12);
    assert.equal(sysCaps.capabilities.render_engine.isAvailable, true);
    assert.equal(sysCaps.capabilities.render_engine.latencyMs, 110);
  });

  // 8. Backend unavailable health state
  test('Backend unavailable health state triggers full offline degradation', async () => {
    const client = new ApiClient();
    const service = new HealthApiService(client);

    fetchMock = async () => {
      throw new Error('Connection refused');
    };

    const sysCaps = await service.checkHealth();
    assert.equal(sysCaps.overallStatus, 'unavailable');
    
    const keys = Object.keys(sysCaps.capabilities) as CapabilityId[];
    assert.equal(keys.length, 5);
    for (const key of keys) {
      assert.equal(sysCaps.capabilities[key].isAvailable, false);
    }
  });

  // 9. Partial capability health state
  test('Partial capability health state handles degraded or offline services', async () => {
    const client = new ApiClient();
    const service = new HealthApiService(client);

    fetchMock = async () => {
      const healthData = {
        status: 'degraded',
        capabilities: {
          script_engine: { status: 'online', latency_ms: 12 },
          tts_engine: { status: 'offline', message: 'Fish Speech node offline' },
          subtitle_engine: { status: 'online', latency_ms: 5 },
          render_engine: { status: 'offline', message: 'FFmpeg lock timeout' },
          project_manager: { status: 'online', latency_ms: 2 }
        }
      };
      return new Response(JSON.stringify(healthData), {
        status: 200,
        headers: new Headers({ 'Content-Type': 'application/json' })
      });
    };

    const sysCaps = await service.checkHealth();
    assert.equal(sysCaps.overallStatus, 'partially_available');
    
    assert.equal(sysCaps.capabilities.script_engine.isAvailable, true);
    assert.equal(sysCaps.capabilities.tts_engine.isAvailable, false);
    assert.equal(sysCaps.capabilities.tts_engine.statusMessage, 'Fish Speech node offline');
    assert.equal(sysCaps.capabilities.subtitle_engine.isAvailable, true);
    assert.equal(sysCaps.capabilities.render_engine.isAvailable, false);
    assert.equal(sysCaps.capabilities.render_engine.statusMessage, 'FFmpeg lock timeout');
  });
});
