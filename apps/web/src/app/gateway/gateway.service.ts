/**
 * Reads the Model Gateway endpoints and exposes their state as signals.
 *
 * Every request goes through {@link API_CONFIG}, exactly like the Foundation service: the backend
 * address is one deployment decision, and a second copy of it here would be a second thing to get
 * wrong.
 *
 * **The browser never holds a provider credential.** It asks the IACode backend, and the backend
 * calls the provider. The provider listing this service reads says whether a credential is
 * configured and which variable would carry it — never a value — because a page served
 * unauthenticated to anyone who can reach it is the last place a key should be.
 */

import { Injectable, PendingTasks, inject, signal } from '@angular/core';

import { API_CONFIG } from '../api-config';

export interface CapabilityView {
  readonly state: string;
  readonly provenance: string;
}

export interface ModelSummary {
  readonly provider: string;
  readonly model: string;
  readonly displayName: string;
  readonly family: string | null;
  readonly contextWindow: number | null;
  readonly maxOutputTokens: number | null;
  readonly supportedEndpoints: readonly string[];
  readonly capabilities: Record<string, CapabilityView>;
  readonly reasoningLevels: readonly string[];
  readonly active: boolean;
  readonly syncedAt: string | null;
}

export interface ProviderSummary {
  readonly provider: string;
  readonly displayName: string;
  readonly adapter: string;
  readonly enabled: boolean;
  readonly protocols: readonly string[];
  readonly credentialConfigured: boolean;
  readonly credentialVariable: string;
  readonly addressConfigured: boolean;
  readonly addressVariable: string;
  readonly healthy: boolean | null;
  readonly lastHealthCheck: string | null;
  readonly lastSync: string | null;
  readonly modelCount: number;
  readonly detail: string | null;
}

export interface GatewayHealth {
  readonly status: string;
  readonly contractVersion: string;
  readonly providers: readonly ProviderSummary[];
  readonly circuits: Record<string, string>;
  readonly catalogSize: number;
  readonly defaultModel: string | null;
  readonly routes: readonly string[];
}

export interface UsageView {
  readonly inputTokens: number | null;
  readonly outputTokens: number | null;
  readonly totalTokens: number | null;
  readonly cachedInputTokens: number | null;
  readonly reasoningTokens: number | null;
}

export interface InferenceAnswer {
  readonly requestId: string;
  readonly provider: string;
  readonly model: string;
  readonly endpoint: string;
  readonly content: string;
  readonly finishReason: string;
  readonly usage: UsageView;
  readonly latencyMs: number;
  readonly route: { readonly reason: string; readonly route: string | null };
  readonly cost: number | null;
}

export interface SyncOutcome {
  readonly provider: string;
  readonly added: number;
  readonly updated: number;
  readonly deactivated: number;
  readonly unchanged: number;
  readonly errors: readonly string[];
}

/** An inference can take a long time; a catalog read cannot. */
const READ_TIMEOUT_MS = 10000;
const INFERENCE_TIMEOUT_MS = 180000;

@Injectable({ providedIn: 'root' })
export class GatewayService {
  private readonly config = inject(API_CONFIG);
  private readonly pendingTasks = inject(PendingTasks);

  readonly health = signal<GatewayHealth | null>(null);
  readonly models = signal<readonly ModelSummary[]>([]);
  readonly error = signal<string | null>(null);
  readonly loading = signal(false);

  readonly answer = signal<InferenceAnswer | null>(null);
  readonly answerError = signal<string | null>(null);
  readonly sending = signal(false);

  readonly syncOutcomes = signal<readonly SyncOutcome[]>([]);
  readonly syncing = signal(false);

  /** Refresh the gateway health and the catalog. Never rejects: a failure becomes `error`. */
  async refresh(): Promise<void> {
    const done = this.pendingTasks.add();
    this.loading.set(true);
    this.error.set(null);
    try {
      const [health, models] = await Promise.all([
        this.read<GatewayHealth>('/api/v1/gateway/health', READ_TIMEOUT_MS),
        this.read<{ models: ModelSummary[] }>('/api/v1/gateway/models', READ_TIMEOUT_MS),
      ]);
      this.health.set(health);
      this.models.set(models.models);
    } catch (error) {
      this.health.set(null);
      this.models.set([]);
      this.error.set(error instanceof Error ? error.message : String(error));
    } finally {
      this.loading.set(false);
      done();
    }
  }

  /** Ask the backend to re-read every provider's catalog. */
  async synchronise(): Promise<void> {
    const done = this.pendingTasks.add();
    this.syncing.set(true);
    try {
      const body = await this.send<{ outcomes: SyncOutcome[] }>(
        '/api/v1/gateway/models/sync',
        {},
        READ_TIMEOUT_MS,
      );
      this.syncOutcomes.set(body.outcomes);
      await this.refresh();
    } catch (error) {
      this.error.set(error instanceof Error ? error.message : String(error));
    } finally {
      this.syncing.set(false);
      done();
    }
  }

  /** Run one inference request through the gateway. */
  async infer(request: {
    prompt: string;
    model?: string | null;
    route?: string | null;
    reasoningEffort?: string | null;
  }): Promise<void> {
    const done = this.pendingTasks.add();
    this.sending.set(true);
    this.answerError.set(null);
    this.answer.set(null);
    try {
      const payload: Record<string, unknown> = {
        messages: [{ role: 'user', content: request.prompt }],
      };
      if (request.model) {
        payload['model'] = request.model;
      } else if (request.route) {
        payload['route'] = request.route;
      }
      if (request.reasoningEffort) {
        payload['reasoningEffort'] = request.reasoningEffort;
      }
      this.answer.set(
        await this.send<InferenceAnswer>('/api/v1/gateway/infer', payload, INFERENCE_TIMEOUT_MS),
      );
    } catch (error) {
      this.answerError.set(error instanceof Error ? error.message : String(error));
    } finally {
      this.sending.set(false);
      done();
    }
  }

  private async read<T>(path: string, timeoutMs: number): Promise<T> {
    return this.request<T>(path, { method: 'GET' }, timeoutMs);
  }

  private async send<T>(path: string, body: unknown, timeoutMs: number): Promise<T> {
    return this.request<T>(
      path,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      },
      timeoutMs,
    );
  }

  private async request<T>(path: string, init: RequestInit, timeoutMs: number): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(`${this.config.baseUrl}${path}`, {
        ...init,
        signal: controller.signal,
        headers: { Accept: 'application/json', ...(init.headers ?? {}) },
        cache: 'no-store',
      });
      const payload: unknown = await response.json().catch(() => null);
      if (!response.ok) {
        // The backend's error contract carries a stable code and a safe message. Showing it beats
        // "request failed", which sends the reader to the browser console for an answer the page
        // already had.
        const detail = payload as { code?: string; message?: string } | null;
        throw new Error(
          detail?.code
            ? `${detail.code}: ${detail.message ?? ''}`.trim()
            : `${path} responded ${response.status}`,
        );
      }
      return payload as T;
    } finally {
      clearTimeout(timer);
    }
  }
}
