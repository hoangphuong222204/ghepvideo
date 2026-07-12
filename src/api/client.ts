/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { ApiRequestOptions, ApiResponse } from './types';
import { ApiError, ApiTimeoutError, ApiNetworkError, ApiCancellationError } from './errors';

function generateCorrelationId(): string {
  return 'corr-' + Math.random().toString(36).substring(2, 15);
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  public async request<T>(path: string, options: ApiRequestOptions = {}): Promise<ApiResponse<T>> {
    const method = options.method || 'GET';
    const correlationId = options.correlationId || generateCorrelationId();
    
    const headers = {
      'Content-Type': 'application/json',
      'X-Correlation-ID': correlationId,
      ...(options.headers || {})
    };

    const url = `${this.baseUrl}${path}`;

    // Handle timeout and cancellation with AbortController
    const controller = new AbortController();
    const { signal } = controller;

    // Hook up external signal if provided
    let externalSignalListener: (() => void) | null = null;
    if (options.signal) {
      if (options.signal.aborted) {
        throw new ApiCancellationError('Request aborted by user', correlationId);
      }
      externalSignalListener = () => {
        controller.abort();
      };
      options.signal.addEventListener('abort', externalSignalListener);
    }

    let timeoutId: any = null;
    if (options.timeout && options.timeout > 0) {
      timeoutId = setTimeout(() => {
        controller.abort();
      }, options.timeout);
    }

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal
      });

      if (timeoutId) {
        clearTimeout(timeoutId);
      }

      if (options.signal && externalSignalListener) {
        options.signal.removeEventListener('abort', externalSignalListener);
      }

      // Extract headers and correlation ID
      const responseHeaders: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        responseHeaders[key.toLowerCase()] = value;
      });

      const respCorrelationId = responseHeaders['x-correlation-id'] || responseHeaders['X-Correlation-ID'] || correlationId;

      let responseData: any = null;
      const contentType = responseHeaders['content-type'] || '';
      if (contentType.includes('application/json')) {
        try {
          responseData = await response.json();
        } catch (e) {
          responseData = null;
        }
      } else {
        responseData = await response.text();
      }

      if (!response.ok) {
        const errorMsg = (responseData && typeof responseData === 'object' && responseData.error) || responseData || `Request failed with status ${response.status}`;
        const errorCode = (responseData && typeof responseData === 'object' && responseData.code) || undefined;
        throw new ApiError(errorMsg, response.status, errorCode, respCorrelationId, responseData);
      }

      return {
        data: responseData as T,
        status: response.status,
        headers: responseHeaders,
        correlationId: respCorrelationId
      };

    } catch (error: any) {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      if (options.signal && externalSignalListener) {
        options.signal.removeEventListener('abort', externalSignalListener);
      }

      if (error.name === 'AbortError') {
        // Distinguish between manual cancel and timeout
        if (options.signal?.aborted) {
          throw new ApiCancellationError('Request cancelled by user', correlationId);
        } else {
          throw new ApiTimeoutError(`Request timed out after ${options.timeout}ms`, correlationId);
        }
      }

      if (error instanceof ApiError) {
        throw error;
      }

      // Default network/connection error
      throw new ApiNetworkError(error.message || 'Network request failed', correlationId);
    }
  }

  public async get<T>(path: string, options: Omit<ApiRequestOptions, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(path, { ...options, method: 'GET' });
  }

  public async post<T>(path: string, body: any, options: Omit<ApiRequestOptions, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(path, { ...options, method: 'POST', body });
  }
}
