/**
 * Reads the Foundation endpoints and exposes their state as signals.
 *
 * Every request goes through {@link API_CONFIG}; no URL is written anywhere else in the
 * application, which is what keeps the backend address a single deployment decision.
 *
 * `/ready` answers 503 when a dependency is down, and that response body is the useful one — it
 * names which dependency failed. So a non-2xx from `/ready` is parsed rather than discarded: a
 * client that treated it as an error would throw away exactly the information the page exists to
 * show.
 */

import { Injectable, PendingTasks, inject, signal } from '@angular/core';

import { API_CONFIG } from './api-config';

export type ServiceStatus = 'UP' | 'DOWN';
export type ReadinessStatus = 'READY' | 'NOT_READY';
export type DependencyState = 'UP' | 'DOWN' | 'SKIPPED';

export interface HealthResponse {
  readonly service: string;
  readonly status: ServiceStatus;
  readonly version: string;
  readonly commit: string;
  readonly timestamp: string;
}

export interface DependencyReport {
  readonly name: string;
  readonly status: DependencyState;
  readonly mandatory: boolean;
  readonly latencyMs: number | null;
  readonly detail: string | null;
}

export interface ReadinessResponse {
  readonly service: string;
  readonly status: ReadinessStatus;
  readonly version: string;
  readonly commit: string;
  readonly timestamp: string;
  readonly dependencies: readonly DependencyReport[];
}

export interface VersionResponse {
  readonly service: string;
  readonly version: string;
  readonly commit: string;
  readonly buildTimestamp: string | null;
  readonly pythonVersion: string;
  readonly environment: string;
}

const REQUEST_TIMEOUT_MS = 8000;

@Injectable({ providedIn: 'root' })
export class FoundationStatusService {
  private readonly config = inject(API_CONFIG);
  /**
   * Angular is zoneless here, so nothing knows about a bare `fetch`. Registering the refresh
   * as a pending task is what makes the application observably unstable while it is in
   * flight: without it `whenStable()` resolves immediately and a test asserts against the
   * empty first render, which is exactly what it did before this was added.
   */
  private readonly pendingTasks = inject(PendingTasks);

  readonly health = signal<HealthResponse | null>(null);
  readonly readiness = signal<ReadinessResponse | null>(null);
  readonly version = signal<VersionResponse | null>(null);
  readonly error = signal<string | null>(null);
  readonly loading = signal(false);

  /** Refresh all three endpoints. Never rejects: a failure becomes the `error` signal. */
  async refresh(): Promise<void> {
    // `add()` rather than `run()`: it returns the removal function, so the task is cleared in a
    // `finally` and a failed refresh cannot leave the application permanently unstable.
    const done = this.pendingTasks.add();
    try {
      await this.load();
    } finally {
      done();
    }
  }

  private async load(): Promise<void> {
    this.loading.set(true);
    this.error.set(null);
    try {
      const [health, readiness, version] = await Promise.all([
        this.read<HealthResponse>('/health'),
        this.read<ReadinessResponse>('/ready'),
        this.read<VersionResponse>('/version'),
      ]);
      this.health.set(health);
      this.readiness.set(readiness);
      this.version.set(version);
    } catch (error) {
      // The page must still render. An unreachable API is a state to display, not a crash.
      this.health.set(null);
      this.readiness.set(null);
      this.version.set(null);
      this.error.set(error instanceof Error ? error.message : String(error));
    } finally {
      this.loading.set(false);
    }
  }

  private async read<T>(path: string): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      const response = await fetch(`${this.config.baseUrl}${path}`, {
        signal: controller.signal,
        headers: { Accept: 'application/json' },
        cache: 'no-store',
      });
      // 503 from /ready is a real answer with a real body. Only a response with no usable body is
      // treated as a failure.
      if (!response.ok && response.status !== 503) {
        throw new Error(`${path} responded ${response.status}`);
      }
      return (await response.json()) as T;
    } finally {
      clearTimeout(timer);
    }
  }
}
