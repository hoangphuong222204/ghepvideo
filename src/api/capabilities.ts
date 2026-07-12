/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type CapabilityId = 'script_engine' | 'tts_engine' | 'subtitle_engine' | 'render_engine' | 'project_manager';

export interface CapabilityStatus {
  id: CapabilityId;
  name: string;
  isAvailable: boolean;
  version?: string;
  statusMessage?: string;
  latencyMs?: number;
}

export interface SystemCapabilities {
  capabilities: Record<CapabilityId, CapabilityStatus>;
  overallStatus: 'fully_available' | 'partially_available' | 'unavailable';
}
