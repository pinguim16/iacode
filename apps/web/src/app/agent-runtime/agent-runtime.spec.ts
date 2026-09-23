import { TestBed } from '@angular/core/testing';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { API_CONFIG } from '../api-config';
import { AgentRuntime } from './agent-runtime';

const TEAMS = [
  {
    team: 'single-agent',
    name: 'Single agent',
    description: 'One generalist answers the task.',
    version: '1.0.0',
    enabled: true,
    stages: [
      { index: 0, name: 'answer', agent: 'generalist', inputs: ['task'], outputName: 'answer' },
    ],
  },
  {
    team: 'planner-reviewer',
    name: 'Planner and reviewer',
    description: 'A planner produces a plan and a reviewer judges it.',
    version: '1.0.0',
    enabled: true,
    stages: [
      { index: 0, name: 'plan', agent: 'planner', inputs: ['task'], outputName: 'plan' },
      {
        index: 1,
        name: 'review',
        agent: 'reviewer',
        inputs: ['task', 'plan'],
        outputName: 'review',
      },
    ],
  },
];

const AGENTS = [
  {
    agent: 'generalist',
    name: 'Generalist',
    role: 'generalist',
    description: 'Answers a single task end to end.',
    version: '1.0.0',
    maxTurns: 4,
    allowedActions: [],
    promptTemplate: 'agents/prompts/generalist.v1.md',
    promptTemplateVersion: 'v1',
    enabled: true,
  },
];

const BUDGET = {
  maxTurns: 8,
  maxModelCalls: 12,
  maxDurationSeconds: 900,
  toolWaitTimeoutSeconds: 3600,
  maxTotalTokens: null,
  turnsUsed: 1,
  modelCallsUsed: 1,
  tokensUsed: 14,
  tokensEnforceable: true,
};

function run(overrides: Record<string, unknown> = {}) {
  return {
    runId: 'run-1',
    taskId: 'task-1',
    title: 'Reply with exactly: IACODE_AGENT_OK',
    task: 'Reply with exactly: IACODE_AGENT_OK',
    team: 'single-agent',
    state: 'SUCCEEDED',
    route: null,
    model: null,
    currentStage: 'answer',
    createdAt: '2026-09-22T12:00:00.000Z',
    startedAt: '2026-09-22T12:00:01.000Z',
    finishedAt: '2026-09-22T12:00:04.000Z',
    workflowId: 'iacode-agent-run-run-1',
    budget: BUDGET,
    stages: [
      {
        index: 0,
        name: 'answer',
        agent: 'generalist',
        agentRunId: 'agent-run-1',
        state: 'SUCCEEDED',
        profileVersion: '1.0.0',
        promptTemplateVersion: 'v1',
        promptTemplateHash: '0'.repeat(64),
        turns: 1,
        modelCalls: 1,
        outputName: 'answer',
        outputSummary: 'IACODE_AGENT_OK',
      },
    ],
    pendingToolRequest: null,
    toolRequests: [],
    toolExecutions: [],
    result: 'IACODE_AGENT_OK',
    resultSummary: 'IACODE_AGENT_OK',
    errorType: null,
    errorSummary: null,
    failedStage: null,
    correlationId: 'c-1',
    summary: {
      agentsExecuted: 1,
      turns: 1,
      modelCalls: 1,
      toolsRequested: 0,
      toolsResolved: 0,
      durationSeconds: 3,
      finalState: 'SUCCEEDED',
      totalTokens: 14,
      cost: null,
      costKnown: false,
    },
    trainingAllowed: false,
    ...overrides,
  };
}

/** A stand-in for the browser's EventSource. The page must never need a real one in a unit test. */
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

  emit(type: string, payload: Record<string, unknown>, sequence: number): void {
    const data = JSON.stringify({
      runId: 'run-1',
      sequence,
      type,
      createdAt: '2026-09-22T12:00:02.000Z',
      agentRunId: null,
      stage: 'answer',
      payload,
    });
    const handler = this.listeners.get(type);
    if (handler) {
      handler({ data } as MessageEvent<string>);
    } else {
      this.onmessage?.({ data } as MessageEvent<string>);
    }
  }
}

function stubBackend(
  options: {
    detail?: Record<string, unknown>;
    created?: Record<string, unknown>;
    status?: number;
  } = {},
): { created: unknown[]; cancelled: number[] } {
  const created: unknown[] = [];
  // An array rather than a number: the object this function returns is built once, so a counter
  // returned by value would be the value it had when the stub was installed.
  const cancelled: number[] = [];
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = String(input);
    const json = (body: unknown, status = 200) =>
      new Response(JSON.stringify(body), {
        status,
        headers: { 'Content-Type': 'application/json' },
      });

    if (url.includes('/agent-teams')) {
      return json(TEAMS);
    }
    if (url.endsWith('/agents')) {
      return json(AGENTS);
    }
    if (url.includes('/agent-runs?limit')) {
      return json({ total: 1, runs: [run()] });
    }
    if (url.includes('/cancel')) {
      cancelled.push(1);
      return json(run({ state: 'CANCELLED', result: null, resultSummary: null }));
    }
    if (init?.method === 'POST' && url.endsWith('/agent-runs')) {
      created.push(JSON.parse(String(init?.body)));
      if (options.status && options.status >= 400) {
        return json(
          { code: 'TEAM_NOT_FOUND', message: 'no team profile named "nope"' },
          options.status,
        );
      }
      return json(
        {
          runId: 'run-1',
          taskId: 'task-1',
          state: 'QUEUED',
          team: 'single-agent',
          createdAt: '2026-09-22T12:00:00.000Z',
          idempotentReplay: false,
        },
        202,
      );
    }
    return json(options.detail ?? run());
  });
  return { created, cancelled };
}

async function render() {
  TestBed.configureTestingModule({
    imports: [AgentRuntime],
    providers: [{ provide: API_CONFIG, useValue: { baseUrl: 'http://api.test' } }],
  });
  const fixture = TestBed.createComponent(AgentRuntime);
  fixture.detectChanges();
  await fixture.whenStable();
  fixture.detectChanges();
  return fixture;
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

describe('Agent Runtime page', () => {
  it('offers the declared teams and the recent runs', async () => {
    stubBackend();
    const element = (await render()).nativeElement as HTMLElement;

    const options = element.querySelectorAll('[data-testid="team"] option');
    expect(Array.from(options).map((item) => item.textContent?.trim())).toEqual([
      'Single agent — 1 stage(s)',
      'Planner and reviewer — 2 stage(s)',
    ]);
    expect(element.querySelector('[data-testid="recent"]')?.textContent).toContain('single-agent');
  });

  it('creates a run from the written task and the chosen team', async () => {
    const backend = stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    const target = element.querySelector('[data-testid="target"]') as HTMLInputElement;
    target.value = 'devworld:model-one';
    target.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(backend.created).toHaveLength(1);
    expect(backend.created[0]).toMatchObject({
      team: 'single-agent',
      model: 'devworld:model-one',
    });
    expect(element.querySelector('[data-testid="run-state"]')?.textContent).toContain('SUCCEEDED');
  });

  it('sends a bare target as a route rather than as a model', async () => {
    const backend = stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    const target = element.querySelector('[data-testid="target"]') as HTMLInputElement;
    target.value = 'balanced';
    target.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();

    expect(backend.created[0]).toMatchObject({ route: 'balanced' });
    expect(backend.created[0]).not.toHaveProperty('model');
  });

  it('follows the run and renders the events it receives', async () => {
    stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    const stream = StubEventSource.instances.at(-1);
    expect(stream?.url).toContain('/api/v1/agent-runs/run-1/events/stream?after=0');
    stream?.emit('AGENT_STARTED', { agent: 'generalist' }, 1);
    stream?.emit('MODEL_CALL_COMPLETED', { provider: 'devworld', model: 'model-one' }, 2);
    await fixture.whenStable();
    fixture.detectChanges();

    const rows = element.querySelectorAll('[data-testid="events"] tbody tr');
    expect(rows).toHaveLength(2);
    expect(rows[0].textContent).toContain('AGENT_STARTED');
    expect(rows[1].textContent).toContain('devworld');
  });

  it('ignores a duplicated event rather than showing it twice', async () => {
    stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;
    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();

    const stream = StubEventSource.instances.at(-1);
    stream?.emit('AGENT_STARTED', { agent: 'generalist' }, 1);
    stream?.emit('AGENT_STARTED', { agent: 'generalist' }, 1);
    await fixture.whenStable();
    fixture.detectChanges();

    expect(element.querySelectorAll('[data-testid="events"] tbody tr')).toHaveLength(1);
  });

  it('shows the result and the stages of a finished run', async () => {
    stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;
    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(element.querySelector('[data-testid="result"]')?.textContent).toContain(
      'IACODE_AGENT_OK',
    );
    expect(element.querySelector('[data-testid="stages"]')?.textContent).toContain('generalist');
    expect(element.querySelector('[data-testid="budget"]')?.textContent).toContain('1/8 turns');
    expect(element.querySelector('[data-testid="cost"]')?.textContent).toContain('UNKNOWN');
  });

  it('shows the tools the sandbox executed, summarised and without their output', async () => {
    stubBackend({
      detail: run({
        toolExecutions: [
          {
            toolRequestId: 'tr-1',
            tool: 'shell.exec',
            status: 'SUCCEEDED',
            durationMs: 412,
            sandboxSession: '0199aa0000ab',
            exitCode: 0,
            timedOut: false,
            truncated: false,
            errorCode: null,
            summary: 'succeeded, exit 0',
            createdAt: '2026-09-22T12:00:04.000Z',
          },
          {
            toolRequestId: 'tr-2',
            tool: 'filesystem.read',
            status: 'DENIED',
            durationMs: 3,
            sandboxSession: null,
            exitCode: null,
            timedOut: false,
            truncated: false,
            errorCode: 'PATH_ESCAPE',
            summary: 'denied, PATH_ESCAPE',
            createdAt: '2026-09-22T12:00:05.000Z',
          },
        ],
      }),
    });
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;
    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    const rows = element.querySelectorAll('[data-testid="tool-execution"]');
    expect(rows).toHaveLength(2);
    expect(rows[0].textContent).toContain('shell.exec');
    expect(rows[0].textContent).toContain('SUCCEEDED');
    expect(rows[0].textContent).toContain('412 ms');
    expect(rows[0].textContent).toContain('0199aa0000ab');
    expect(rows[0].textContent).toContain('succeeded, exit 0');
    expect(rows[1].textContent).toContain('DENIED');
    expect(rows[1].textContent).toContain('PATH_ESCAPE');
    const table = element.querySelector('[data-testid="tool-executions"]');
    expect(table?.querySelectorAll('button, a, input')).toHaveLength(0);
  });

  it('cancels a run that is still executing', async () => {
    const backend = stubBackend({ detail: run({ state: 'RUNNING', result: null }) });
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;
    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    (element.querySelector('[data-testid="cancel"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(backend.cancelled).toHaveLength(1);
    expect(element.querySelector('[data-testid="run-state"]')?.textContent).toContain('CANCELLED');
    expect(element.querySelector('[data-testid="cancel"]')).toBeNull();
  });

  it('shows a waiting run as waiting, and offers nothing that would execute the tool', async () => {
    stubBackend({
      detail: run({
        state: 'WAITING_FOR_TOOL',
        result: null,
        pendingToolRequest: {
          toolRequestId: 'tr-1',
          agentRunId: 'agent-run-1',
          name: 'repo.read',
          arguments: { path: 'README.md' },
          status: 'PENDING',
          createdAt: '2026-09-22T12:00:03.000Z',
          resolvedAt: null,
        },
      }),
    });
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;
    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    const panel = element.querySelector('[data-testid="waiting-for-tool"]');
    expect(panel).not.toBeNull();
    expect(element.querySelector('[data-testid="pending-tool"]')?.textContent).toContain(
      'repo.read',
    );
    expect(element.querySelector('[data-testid="pending-status"]')?.textContent).toContain(
      'PENDING',
    );

    // The panel that announces the pause offers no control at all, and nothing anywhere on the
    // page offers to execute, approve or allow the tool. "Start run" and "Cancel run" are about
    // the run, which is why the check is about the verbs rather than about the word "run".
    expect(panel?.querySelectorAll('button')).toHaveLength(0);
    expect(panel?.querySelectorAll('a')).toHaveLength(0);
    expect(panel?.querySelectorAll('input')).toHaveLength(0);
    const labels = Array.from(element.querySelectorAll('button, a, input')).map((item) =>
      `${item.textContent ?? ''} ${item.getAttribute('data-testid') ?? ''}`.toLowerCase(),
    );
    for (const forbidden of ['execute', 'approve', 'allow', 'shell', 'run tool', 'resolve']) {
      expect(labels.some((label) => label.includes(forbidden))).toBe(false);
    }
  });

  it('shows a failure as a type, a safe message and a correlation identifier', async () => {
    stubBackend({
      detail: run({
        state: 'FAILED',
        result: null,
        errorType: 'INVALID_AGENT_OUTPUT',
        errorSummary: 'the agent answered with an invalid envelope twice',
        failedStage: 'answer',
      }),
    });
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;
    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    const failure = element.querySelector('[data-testid="failure"]');
    expect(element.querySelector('[data-testid="error-type"]')?.textContent).toContain(
      'INVALID_AGENT_OUTPUT',
    );
    expect(failure?.textContent).toContain('invalid envelope twice');
    expect(element.querySelector('[data-testid="correlation"]')?.textContent).toContain('c-1');
    expect(failure?.textContent).not.toContain('Traceback');
  });

  it('shows the backend error contract when a run cannot be created', async () => {
    stubBackend({ status: 404 });
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(element.querySelector('[data-testid="runtime-error"]')?.textContent).toContain(
      'TEAM_NOT_FOUND',
    );
  });

  it('renders model output as text, never as markup', async () => {
    const hostile = '<img src=x onerror="alert(1)"><script>alert(2)</script>';
    stubBackend({ detail: run({ result: hostile }) });
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;
    (element.querySelector('[data-testid="start"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    const result = element.querySelector('[data-testid="result"]') as HTMLElement;
    expect(result.textContent).toContain('<script>');
    expect(result.querySelector('script')).toBeNull();
    expect(result.querySelector('img')).toBeNull();
  });
});
