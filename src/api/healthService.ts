/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { ApiClient } from './client';
import { SystemCapabilities, CapabilityId, CapabilityStatus } from './capabilities';

export interface BackendHealthResponse {
  status: 'healthy' | 'unhealthy' | 'degraded';
  version?: string;
  capabilities?: Record<string, {
    status: 'online' | 'offline' | 'degraded';
    message?: string;
    latency_ms?: number;
  }>;
}

export class HealthApiService {
  private client: ApiClient;

  constructor(client: ApiClient = new ApiClient()) {
    this.client = client;
  }

  public async checkHealth(): Promise<SystemCapabilities> {
    const defaultCapabilities: Record<CapabilityId, CapabilityStatus> = {
      script_engine: { id: 'script_engine', name: 'Script Generation Engine', isAvailable: false },
      tts_engine: { id: 'tts_engine', name: 'Text-to-Speech Engine', isAvailable: false },
      subtitle_engine: { id: 'subtitle_engine', name: 'Subtitle Generation Engine', isAvailable: false },
      render_engine: { id: 'render_engine', name: 'Video Render Engine', isAvailable: false },
      project_manager: { id: 'project_manager', name: 'Project Manager', isAvailable: false },
    };

    try {
      const response = await this.client.get<BackendHealthResponse>('/api/health', { timeout: 5000 });
      const data = response.data;

      const capabilities: Record<CapabilityId, CapabilityStatus> = { ...defaultCapabilities };
      let onlineCount = 0;
      let totalCount = Object.keys(defaultCapabilities).length;

      const apiCapabilities = data.capabilities || {};

      for (const key of Object.keys(defaultCapabilities) as CapabilityId[]) {
        const backendCap = apiCapabilities[key];
        if (backendCap) {
          const isOnline = backendCap.status === 'online';
          capabilities[key] = {
            id: key,
            name: defaultCapabilities[key].name,
            isAvailable: isOnline,
            statusMessage: backendCap.message,
            latencyMs: backendCap.latency_ms,
          };
          if (isOnline) {
            onlineCount++;
          }
        }
      }

      let overallStatus: 'fully_available' | 'partially_available' | 'unavailable' = 'unavailable';
      if (onlineCount === totalCount) {
        overallStatus = 'fully_available';
      } else if (onlineCount > 0) {
        overallStatus = 'partially_available';
      }

      return {
        capabilities,
        overallStatus,
      };

    } catch (error) {
      // Backend unavailable health state
      return {
        capabilities: defaultCapabilities,
        overallStatus: 'unavailable',
      };
    }
  }
}
