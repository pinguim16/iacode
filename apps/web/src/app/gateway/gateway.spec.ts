import { TestBed } from '@angular/core/testing';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { API_CONFIG } from '../api-config';
import { Gateway } from './gateway';

const HEALTH = {
  status: 'READY',
  contractVersion: '1.0.0',
  providers: [
    {
      provider: 'devworld',
      displayName: 'DevWorld',
      adapter: 'openai-compatible',
      enabled: true,
      protocols: ['openai-chat-completions'],
      credentialConfigured: true,
      credentialVariable: 'IACODE_DEVWORLD_API_KEY',
      addressConfigured: true,
      addressVariable: 'IACODE_DEVWORLD_BASE_URL',
      healthy: true,
      lastHealthCheck: '2026-09-22T12:00:00Z',
      lastSync: '2026-09-22T12:00:00Z',
      modelCount: 2,
      detail: null,
    },
  ],
  circuits: {},
  catalogSize: 2,
  defaultModel: 'devworld:model-one',
  routes: ['default', 'fast'],
};

const MODELS = {
  total: 2,
  models: [
    {
      provider: 'devworld',
      model: 'model-two',
      displayName: 'Model Two',
      family: 'acme',
      contextWindow: null,
      maxOutputTokens: null,
      supportedEndpoints: [],
      capabilities: {
        streaming: { state: 'SUPPORTED', provenance: 'MANUAL_CONFIGURATION' },
        tools: { state: 'UNKNOWN', provenance: 'UNKNOWN' },
        'structured-output': { state: 'UNKNOWN', provenance: 'UNKNOWN' },
      },
      reasoningLevels: [],
      active: true,
      syncedAt: '2026-09-22T12:00:00Z',
    },
    {
      provider: 'devworld',
      model: 'model-one',
      displayName: 'Model One',
      family: 'acme',
      contextWindow: 128000,
      maxOutputTokens: 4096,
      supportedEndpoints: ['openai-chat-completions'],
      capabilities: {
        streaming: { state: 'SUPPORTED', provenance: 'PROVIDER_METADATA' },
        tools: { state: 'UNSUPPORTED', provenance: 'PROVIDER_METADATA' },
        'structured-output': { state: 'SUPPORTED', provenance: 'PROVIDER_METADATA' },
      },
      reasoningLevels: ['low', 'high'],
      active: true,
      syncedAt: '2026-09-22T12:00:00Z',
    },
  ],
};

const ANSWER = {
  contractVersion: '1.0.0',
  requestId: 'req-1',
  provider: 'devworld',
  model: 'model-one',
  endpoint: 'openai-chat-completions',
  content: 'IACODE_GATEWAY_OK',
  toolCalls: [],
  finishReason: 'STOP',
  usage: {
    inputTokens: 7,
    outputTokens: 3,
    totalTokens: 10,
    cachedInputTokens: null,
    reasoningTokens: null,
  },
  latencyMs: 412.5,
  route: { reason: 'DEFAULT_MODEL', route: null, considered: 1, rejected: [], chain: [] },
  cost: null,
};

function stubBackend(overrides: { infer?: unknown; status?: number } = {}): void {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = String(input);
    if (url.includes('/gateway/infer')) {
      return new Response(JSON.stringify(overrides.infer ?? ANSWER), {
        status: overrides.status ?? 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    if (url.includes('/gateway/models/sync')) {
      expect(init?.method).toBe('POST');
      return new Response(
        JSON.stringify({
          outcomes: [
            {
              provider: 'devworld',
              added: 1,
              updated: 0,
              deactivated: 0,
              unchanged: 1,
              errors: [],
            },
          ],
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    }
    const body = url.includes('/gateway/health') ? HEALTH : MODELS;
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  });
}

async function render() {
  TestBed.configureTestingModule({
    imports: [Gateway],
    providers: [{ provide: API_CONFIG, useValue: { baseUrl: 'http://api.test' } }],
  });
  const fixture = TestBed.createComponent(Gateway);
  fixture.detectChanges();
  await fixture.whenStable();
  fixture.detectChanges();
  return fixture;
}

afterEach(() => {
  vi.restoreAllMocks();
  TestBed.resetTestingModule();
});

describe('Model Gateway page', () => {
  it('shows the provider status, the model count and the last synchronisation', async () => {
    stubBackend();
    const element = (await render()).nativeElement as HTMLElement;

    const providers = element.querySelector('[data-testid="providers"]');
    expect(providers?.textContent).toContain('DevWorld');
    expect(providers?.textContent).toContain('openai-compatible');
    expect(providers?.textContent).toContain('2026-09-22T12:00:00Z');
    expect(element.querySelector('[data-testid="catalog-size"]')?.textContent).toContain('2');
  });

  it('lists the catalog with its capabilities in a stable order', async () => {
    stubBackend();
    const element = (await render()).nativeElement as HTMLElement;

    const rows = element.querySelectorAll('[data-testid="catalog"] tbody tr');
    expect(rows).toHaveLength(2);
    const names = Array.from(rows).map((row) => row.querySelector('td')?.textContent?.trim());
    expect(names).toEqual(['model-one', 'model-two']);
    expect(rows[0].textContent).toContain('UNSUPPORTED');
    expect(rows[1].textContent).toContain('UNKNOWN');
  });

  it('never shows a credential, only whether one is configured', async () => {
    stubBackend();
    const element = (await render()).nativeElement as HTMLElement;
    const text = element.textContent ?? '';

    expect(text).toContain('configured');
    expect(text).not.toContain('Bearer');
    expect(text).not.toContain('sk-');
  });

  it('names the missing variable when a provider has no credential', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input);
      const body = url.includes('/gateway/health')
        ? {
            ...HEALTH,
            status: 'DEGRADED',
            providers: [{ ...HEALTH.providers[0], credentialConfigured: false, healthy: false }],
          }
        : MODELS;
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    });

    const element = (await render()).nativeElement as HTMLElement;

    expect(element.querySelector('[data-testid="providers"]')?.textContent).toContain(
      'IACODE_DEVWORLD_API_KEY',
    );
  });

  it('sends a prompt and shows the chosen model, the latency and the usage', async () => {
    stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    (element.querySelector('[data-testid="send"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    const answer = element.querySelector('[data-testid="answer"]');
    expect(answer?.textContent).toContain('devworld:model-one');
    expect(answer?.textContent).toContain('412.5 ms');
    expect(answer?.textContent).toContain('7 in / 3 out');
    expect(answer?.textContent).toContain('unknown (no pricing configured)');
    expect(element.querySelector('[data-testid="answer-content"]')?.textContent).toContain(
      'IACODE_GATEWAY_OK',
    );
  });

  it('shows the backend error contract rather than a generic failure', async () => {
    stubBackend({
      status: 409,
      infer: { code: 'NO_CANDIDATE', message: 'no default model is configured' },
    });
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    (element.querySelector('[data-testid="send"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(element.querySelector('[data-testid="answer-error"]')?.textContent).toContain(
      'NO_CANDIDATE',
    );
  });

  it('reports what a synchronisation changed', async () => {
    stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    (element.querySelector('[data-testid="sync"]') as HTMLButtonElement).click();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(element.querySelector('[data-testid="sync-outcome"]')?.textContent).toContain('1 added');
  });

  it('renders an explicit failure panel when the gateway is unreachable', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('connection refused'));
    const element = (await render()).nativeElement as HTMLElement;

    expect(element.querySelector('[data-testid="gateway-error"]')?.textContent).toContain(
      'connection refused',
    );
    expect(element.querySelector('[data-testid="playground"]')).not.toBeNull();
  });
});
