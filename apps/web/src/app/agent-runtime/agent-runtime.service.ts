/**
 * Reads the Agent Runtime endpoints and exposes their state as signals.
 *
 * Every request goes through {@link API_CONFIG}, exactly like the Foundation and gateway services:
 * the backend address is one deployment decision, and a second copy of it here would be a second
 * thing to get wrong.
 *
 * **The browser never holds a provider credential, and it never executes anything.** It creates a
 * run, watches its events and reads the result. When a run pauses on a tool request the page says
 * so and offers nothing that would run it — Gate 2 executes no tool at all, and a button that
 * implied otherwise would be describing a capability that does not exist.
 *
 * Events arrive over Server-Sent Events, with the cursor the API assigns. A reconnection resumes
 * from that cursor rather than from the beginning, so a dropped connection costs nothing and
 * creates no duplicate.
 */

import { Injectable, PendingTasks, inject, signal } from '@angular/core';

import { API_CONFIG } from '../api-config';

export interface BudgetView {
  readonly maxTurns: number;
  readonly maxModelCalls: number;
  readonly maxDurationSeconds: number;
  readonly toolWaitTimeoutSeconds: number;
  readonly maxTotalTokens: number | null;
  readonly turnsUsed: number;
  readonly modelCallsUsed: number;
  readonly tokensUsed: number | null;
  readonly tokensEnforceable: boolean;
}

export interface StageView {
  readonly index: number;
  readonly name: string;
  readonly agent: string;
  readonly agentRunId: string | null;
  readonly state: string;
  readonly profileVersion: string | null;
  readonly promptTemplateVersion: string | null;
  readonly promptTemplateHash: string | null;
  readonly turns: number;
  readonly modelCalls: number;
  readonly outputName: string | null;
  readonly outputSummary: string | null;
}

export interface ToolRequestView {
  readonly toolRequestId: string;
  readonly agentRunId: string | null;
  readonly name: string;
  readonly arguments: Record<string, unknown>;
  readonly status: string;
  readonly createdAt: string;
  readonly resolvedAt: string | null;
}

/**
 * One tool the sandbox executed for the run (Gate 3): what, how it ended, how long, where. The page
 * never receives a tool's output; that stays with the agent and the artifact store.
 */
export interface ToolExecutionView {
  readonly toolRequestId: string;
  readonly tool: string;
  readonly status: string;
  readonly durationMs: number | null;
  readonly sandboxSession: string | null;
  readonly exitCode: number | null;
  readonly timedOut: boolean;
  readonly truncated: boolean;
  readonly errorCode: string | null;
  readonly summary: string;
  readonly createdAt: string;
}

export interface RunSummaryView {
  readonly agentsExecuted: number;
  readonly turns: number;
  readonly modelCalls: number;
  readonly toolsRequested: number;
  readonly toolsResolved: number;
  readonly durationSeconds: number | null;
  readonly finalState: string | null;
  readonly totalTokens: number | null;
  readonly cost: number | null;
  readonly costKnown: boolean;
}

export interface AgentRun {
  readonly runId: string;
  readonly taskId: string;
  readonly title: string | null;
  readonly task: string;
  readonly team: string;
  readonly state: string;
  readonly route: string | null;
  readonly model: string | null;
  readonly currentStage: string | null;
  readonly createdAt: string;
  readonly startedAt: string | null;
  readonly finishedAt: string | null;
  readonly workflowId: string | null;
  readonly budget: BudgetView;
  readonly stages: readonly StageView[];
  readonly pendingToolRequest: ToolRequestView | null;
  readonly toolRequests: readonly ToolRequestView[];
  readonly toolExecutions: readonly ToolExecutionView[];
  readonly result: string | null;
  readonly resultSummary: string | null;
  readonly errorType: string | null;
  readonly errorSummary: string | null;
  readonly failedStage: string | null;
  readonly correlationId: string | null;
  readonly summary: RunSummaryView;
  readonly trainingAllowed: boolean;
}

export interface RunEvent {
  readonly runId: string;
  readonly sequence: number;
  readonly type: string;
  readonly createdAt: string;
  readonly agentRunId: string | null;
  readonly stage: string | null;
  readonly payload: Record<string, unknown>;
}

export interface TeamStage {
  readonly index: number;
  readonly name: string;
  readonly agent: string;
  readonly inputs: readonly string[];
  readonly outputName: string;
}

export interface TeamProfile {
  readonly team: string;
  readonly name: string;
  readonly description: string;
  readonly version: string;
  readonly enabled: boolean;
  readonly stages: readonly TeamStage[];
}

export interface AgentProfile {
  readonly agent: string;
  readonly name: string;
  readonly role: string;
  readonly description: string;
  readonly version: string;
  readonly maxTurns: number;
  readonly allowedActions: readonly string[];
  readonly promptTemplate: string;
  readonly promptTemplateVersion: string;
  readonly enabled: boolean;
}

const READ_TIMEOUT_MS = 10000;
const CREATE_TIMEOUT_MS = 20000;

/** A run reaching one of these is finished; the page stops following it. */
export const TERMINAL_STATES = new Set(['SUCCEEDED', 'FAILED', 'CANCELLED']);

/**
 * The events after which the run itself looks different — a new stage, a pause, a resume, an
 * ending. The page re-reads the run for these and only these, so following a run costs one read
 * per visible change rather than one per event.
 */
const STATE_CHANGING = new Set([
  'RUN_STARTED',
  'AGENT_STARTED',
  'AGENT_COMPLETED',
  'TOOL_REQUESTED',
  'TOOL_RESULT_RECEIVED',
  'RUN_COMPLETED',
  'RUN_FAILED',
  'RUN_CANCELLED',
]);

@Injectable({ providedIn: 'root' })
export class AgentRuntimeService {
  private readonly config = inject(API_CONFIG);
  private readonly pendingTasks = inject(PendingTasks);

  readonly teams = signal<readonly TeamProfile[]>([]);
  readonly agents = signal<readonly AgentProfile[]>([]);
  readonly recent = signal<readonly AgentRun[]>([]);

  readonly run = signal<AgentRun | null>(null);
  readonly events = signal<readonly RunEvent[]>([]);
  readonly error = signal<string | null>(null);
  readonly starting = signal(false);
  readonly following = signal(false);

  private stream: EventSource | null = null;

  /** Read the declared teams, agents and the most recent runs. Never rejects. */
  async refresh(): Promise<void> {
    const done = this.pendingTasks.add();
    this.error.set(null);
    try {
      const [teams, agents, recent] = await Promise.all([
        this.read<TeamProfile[]>('/api/v1/agent-teams', READ_TIMEOUT_MS),
        this.read<AgentProfile[]>('/api/v1/agents', READ_TIMEOUT_MS),
        this.read<{ runs: AgentRun[] }>('/api/v1/agent-runs?limit=10', READ_TIMEOUT_MS),
      ]);
      this.teams.set(teams);
      this.agents.set(agents);
      this.recent.set(recent.runs);
    } catch (error) {
      this.error.set(error instanceof Error ? error.message : String(error));
    } finally {
      done();
    }
  }

  /** Create a run and start following it. */
  async start(request: {
    task: string;
    team: string;
    target?: string | null;
    maxTurns?: number | null;
  }): Promise<void> {
    const done = this.pendingTasks.add();
    this.starting.set(true);
    this.error.set(null);
    this.events.set([]);
    this.run.set(null);
    try {
      const target = (request.target ?? '').trim();
      const payload: Record<string, unknown> = {
        task: request.task,
        team: request.team,
      };
      // A qualified reference is an explicit model; anything else is a route alias. One field
      // rather than two, because the contract refuses a request that names both.
      if (target.includes(':')) {
        payload['model'] = target;
      } else if (target) {
        payload['route'] = target;
      }
      if (request.maxTurns) {
        payload['maxTurns'] = request.maxTurns;
      }
      const created = await this.send<{ runId: string }>(
        '/api/v1/agent-runs',
        payload,
        CREATE_TIMEOUT_MS,
      );
      await this.follow(created.runId);
      await this.refresh();
    } catch (error) {
      this.error.set(error instanceof Error ? error.message : String(error));
    } finally {
      this.starting.set(false);
      done();
    }
  }

  /** Follow a run: read it once, then subscribe to its events. */
  async follow(runId: string): Promise<void> {
    this.stopFollowing();
    this.events.set([]);
    await this.reload(runId);
    this.subscribe(runId);
  }

  /** Read a run's current state. */
  async reload(runId: string): Promise<void> {
    try {
      this.run.set(await this.read<AgentRun>(`/api/v1/agent-runs/${runId}`, READ_TIMEOUT_MS));
    } catch (error) {
      this.error.set(error instanceof Error ? error.message : String(error));
    }
  }

  /** Ask the backend to cancel the run being followed. */
  async cancel(): Promise<void> {
    const current = this.run();
    if (!current) {
      return;
    }
    const done = this.pendingTasks.add();
    try {
      this.run.set(
        await this.send<AgentRun>(
          `/api/v1/agent-runs/${current.runId}/cancel`,
          {},
          READ_TIMEOUT_MS,
        ),
      );
    } catch (error) {
      this.error.set(error instanceof Error ? error.message : String(error));
    } finally {
      done();
    }
  }

  /** Stop the event subscription. Called when the page is destroyed or a new run starts. */
  stopFollowing(): void {
    this.stream?.close();
    this.stream = null;
    this.following.set(false);
  }

  private subscribe(runId: string): void {
    const cursor = this.events().at(-1)?.sequence ?? 0;
    const url = `${this.config.baseUrl}/api/v1/agent-runs/${runId}/events/stream?after=${cursor}`;
    const source = new EventSource(url);
    this.stream = source;
    this.following.set(true);

    source.onmessage = (message: MessageEvent<string>) => this.accept(runId, message.data);
    // Every event type is delivered under its own name as well as on the default channel, so a
    // handler is attached per name rather than relying on `onmessage` alone.
    for (const name of [
      'RUN_CREATED',
      'RUN_STARTED',
      'AGENT_STARTED',
      'MODEL_CALL_STARTED',
      'MODEL_CALL_COMPLETED',
      'TOOL_REQUESTED',
      'TOOL_RESULT_RECEIVED',
      'AGENT_COMPLETED',
      'RUN_COMPLETED',
      'RUN_FAILED',
      'RUN_CANCELLED',
      'RUN_NOTE',
    ]) {
      source.addEventListener(name, (message) =>
        this.accept(runId, (message as MessageEvent<string>).data),
      );
    }
    source.onerror = () => {
      // A stream that ends is normal: the API closes it when the run is over. Reading the run once
      // more is what turns "the connection went away" into "the run finished", and it is also the
      // recovery path for a proxy that dropped an idle connection.
      this.stopFollowing();
      void this.reload(runId);
    };
  }

  private accept(runId: string, raw: string): void {
    let event: RunEvent;
    try {
      event = JSON.parse(raw) as RunEvent;
    } catch {
      return;
    }
    if (this.events().some((item) => item.sequence === event.sequence)) {
      return;
    }
    this.events.set(
      [...this.events(), event].sort((left, right) => left.sequence - right.sequence),
    );
    if (STATE_CHANGING.has(event.type)) {
      void this.reload(runId);
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
        // "request failed", which sends the reader to the console for an answer the page had.
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
