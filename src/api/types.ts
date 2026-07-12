/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number; // timeout in milliseconds
  signal?: AbortSignal;
  correlationId?: string;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
  correlationId: string;
}
