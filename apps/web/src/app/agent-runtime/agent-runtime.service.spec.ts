import { TestBed } from '@angular/core/testing';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { API_CONFIG } from '../api-config';
import { AgentRuntimeService } from './agent-runtime.service';

class StubEventSource {
  static instances: StubEventSource[] = [];
  onmessage: ((event: MessageEvent<string>) => void) | null = null;
  onerror: (() => void) | null = null;
  closed = false;
  readonly listeners = new Map<string, (event: MessageEvent<string>) => void>();

  constructor(readonly url: string) {
    StubEventSource.instances.push(this);
  }

  addEventListener(name: string, handler: (event: MessageEvent<string>) => void): void {
    this.listeners.set(name, handler);
  }

  close(): void {
    this.closed = true;
  }

  deliver(type: string, sequence: number): void {
    const data = JSON.stringify({
      runId: 'run-1',
      sequence,
      type,
      createdAt: '2026-09-22T12:00:02.000Z',
      agentRunId: null,
      stage: null,
      payload: {},
    });
    const handler = this.listeners.get(type);
    (handler ?? this.onmessage)?.({ data } as MessageEvent<string>);
  }
}

const RUN = {
  runId: 'run-1',
  taskId: 'task-1',
  title: null,
  task: 'a task',
  team: 'single-agent',
  state: 'RUNNING',
  route: null,
  model: null,
  currentStage: null,
  createdAt: '2026-09-22T12:00:00.000Z',
  startedAt: null,
  finishedAt: null,
  workflowId: 'iacode-agent-run-run-1',
  budget: {
    maxTurns: 8,
    maxModelCalls: 12,
    maxDurationSeconds: 900,
    toolWaitTimeoutSeconds: 3600,
    maxTotalTokens: null,
    turnsUsed: 0,
    modelCallsUsed: 0,
    tokensUsed: null,
    tokensEnforceable: true,
  },
  stages: [],
  pendingToolRequest: null,
  toolRequests: [],
  toolExecutions: [],
  result: null,
  resultSummary: null,
  errorType: null,
  errorSummary: null,
  failedStage: null,
  correlationId: null,
  summary: {
    agentsExecuted: 0,
    turns: 0,
    modelCalls: 0,
    toolsRequested: 0,
    toolsResolved: 0,
    durationSeconds: null,
    finalState: null,
    totalTokens: null,
    cost: null,
    costKnown: false,
  },
  trainingAllowed: false,
};

function service(): AgentRuntimeService {
  TestBed.configureTestingModule({
    providers: [{ provide: API_CONFIG, useValue: { baseUrl: 'http://api.test' } }],
  });
  return TestBed.inject(AgentRuntimeService);
}

function stub(reads: string[]): void {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const url = String(input);
    reads.push(url);
    const body = url.includes('/agent-teams') || url.endsWith('/agents') ? [] : RUN;
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  });
}

beforeEach(() => {
  StubEventSource.instances = [];
  vi.stubGlobal('EventSource', StubEventSource);
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  TestBed.resetTestingModule();
});

describe('AgentRuntimeService', () => {
  it('subscribes from the cursor it already has', async () => {
    const reads: string[] = [];
    stub(reads);
    const runtime = service();

    await runtime.follow('run-1');
    const first = StubEventSource.instances.at(-1);
    expect(first?.url).toContain('after=0');

    first?.deliver('AGENT_STARTED', 4);
    await runtime.follow('run-1');

    // A fresh follow starts from zero again, because it clears what it had. What must never happen
    // is a subscription that replays from the beginning while keeping the events it already holds.
    expect(runtime.events()).toHaveLength(0);
    expect(StubEventSource.instances.at(-1)?.url).toContain('after=0');
    expect(first?.closed).toBe(true);
  });

  it('keeps events in sequence order however they arrive', async () => {
    stub([]);
    const runtime = service();
    await runtime.follow('run-1');
    const stream = StubEventSource.instances.at(-1);

    stream?.deliver('MODEL_CALL_STARTED', 3);
    stream?.deliver('AGENT_STARTED', 2);
    stream?.deliver('RUN_STARTED', 1);

    expect(runtime.events().map((item) => item.sequence)).toEqual([1, 2, 3]);
  });

  it('re-reads the run when a state-changing event arrives and not otherwise', async () => {
    const reads: string[] = [];
    stub(reads);
    const runtime = service();
    await runtime.follow('run-1');
    const before = reads.filter((url) => url.endsWith('/agent-runs/run-1')).length;
    const stream = StubEventSource.instances.at(-1);

    stream?.deliver('MODEL_CALL_STARTED', 1);
    await Promise.resolve();
    expect(reads.filter((url) => url.endsWith('/agent-runs/run-1')).length).toBe(before);

    stream?.deliver('AGENT_COMPLETED', 2);
    await Promise.resolve();
    await Promise.resolve();
    expect(reads.filter((url) => url.endsWith('/agent-runs/run-1')).length).toBeGreaterThan(before);
  });

  it('treats the end of a stream as the end of the run rather than as an error', async () => {
    const reads: string[] = [];
    stub(reads);
    const runtime = service();
    await runtime.follow('run-1');
    const stream = StubEventSource.instances.at(-1);

    stream?.onerror?.();
    await Promise.resolve();

    expect(runtime.following()).toBe(false);
    expect(runtime.error()).toBeNull();
  });

  it('ignores a frame that is not the event shape', async () => {
    stub([]);
    const runtime = service();
    await runtime.follow('run-1');
    const stream = StubEventSource.instances.at(-1);

    stream?.onmessage?.({ data: 'not json' } as MessageEvent<string>);

    expect(runtime.events()).toHaveLength(0);
  });

  it('sends no credential and no address when it creates a run', async () => {
    const bodies: string[] = [];
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      if (init?.method === 'POST') {
        bodies.push(String(init.body));
        return new Response(JSON.stringify({ runId: 'run-1' }), {
          status: 202,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      const url = String(input);
      const body = url.includes('/agent-teams') || url.endsWith('/agents') ? [] : RUN;
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    });
    const runtime = service();

    await runtime.start({ task: 'a task', team: 'single-agent' });

    expect(bodies).toHaveLength(1);
    const sent = bodies[0].toLowerCase();
    for (const forbidden of ['apikey', 'api_key', 'authorization', 'baseurl', 'bearer']) {
      expect(sent).not.toContain(forbidden);
    }
  });

  it('turns a backend refusal into the code and message the contract carries', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      if (init?.method === 'POST') {
        return new Response(
          JSON.stringify({ code: 'PAYLOAD_TOO_LARGE', message: 'the task is too large' }),
          { status: 413, headers: { 'Content-Type': 'application/json' } },
        );
      }
      const url = String(input);
      const body = url.includes('/agent-teams') || url.endsWith('/agents') ? [] : RUN;
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    });
    const runtime = service();

    await runtime.start({ task: 'x'.repeat(10), team: 'single-agent' });

    expect(runtime.error()).toContain('PAYLOAD_TOO_LARGE');
    expect(runtime.error()).toContain('the task is too large');
  });
});
