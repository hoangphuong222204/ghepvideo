/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export class ApiError extends Error {
  public readonly status: number;
  public readonly code?: string;
  public readonly correlationId?: string;
  public readonly details?: any;

  constructor(message: string, status: number, code?: string, correlationId?: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.correlationId = correlationId;
    this.details = details;
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

export class ApiTimeoutError extends ApiError {
  constructor(message: string, correlationId?: string) {
    super(message, 408, 'TIMEOUT', correlationId);
    this.name = 'ApiTimeoutError';
    Object.setPrototypeOf(this, ApiTimeoutError.prototype);
  }
}

export class ApiNetworkError extends ApiError {
  constructor(message: string, correlationId?: string) {
    super(message, 0, 'NETWORK_ERROR', correlationId);
    this.name = 'ApiNetworkError';
    Object.setPrototypeOf(this, ApiNetworkError.prototype);
  }
}

export class ApiCancellationError extends ApiError {
  constructor(message: string, correlationId?: string) {
    super(message, 499, 'CANCELLED', correlationId);
    this.name = 'ApiCancellationError';
    Object.setPrototypeOf(this, ApiCancellationError.prototype);
  }
}
