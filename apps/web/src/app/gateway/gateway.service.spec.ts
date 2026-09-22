import { TestBed } from '@angular/core/testing';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { API_CONFIG } from '../api-config';
import { GatewayService } from './gateway.service';

function service(baseUrl = 'http://api.test'): GatewayService {
  TestBed.configureTestingModule({
    providers: [{ provide: API_CONFIG, useValue: { baseUrl } }],
  });
  return TestBed.inject(GatewayService);
}

afterEach(() => {
  vi.restoreAllMocks();
  TestBed.resetTestingModule();
});

describe('GatewayService', () => {
  it('calls only the configured IACode backend', async () => {
    const seen: string[] = [];
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      seen.push(String(input));
      const body = String(input).includes('health')
        ? { status: 'READY', providers: [], circuits: {}, routes: [] }
        : { models: [] };
      return new Response(JSON.stringify(body), { status: 200 });
    });

    await service().refresh();

    expect(seen).toEqual([
      'http://api.test/api/v1/gateway/health',
      'http://api.test/api/v1/gateway/models',
    ]);
    // A provider address would be a second destination. There is not one, and there is no field in
    // the request the page could put one in.
    expect(seen.every((url) => url.startsWith('http://api.test/api/v1/gateway/'))).toBe(true);
  });

  it('never rejects: an unreachable backend becomes a rendered state', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('connection refused'));
    const gateway = service();

    await gateway.refresh();

    expect(gateway.error()).toContain('connection refused');
    expect(gateway.health()).toBeNull();
    expect(gateway.loading()).toBe(false);
  });

  it('sends an explicit model as a model and an alias as a route', async () => {
    const bodies: unknown[] = [];
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (_input, init) => {
      bodies.push(JSON.parse(String(init?.body)));
      return new Response(JSON.stringify({ content: 'ok', usage: {}, route: {} }), {
        status: 200,
      });
    });
    const gateway = service();

    await gateway.infer({ prompt: 'hello', model: 'devworld:model-one' });
    await gateway.infer({ prompt: 'hello', route: 'fast', reasoningEffort: 'high' });

    expect(bodies[0]).toEqual({
      messages: [{ role: 'user', content: 'hello' }],
      model: 'devworld:model-one',
    });
    expect(bodies[1]).toEqual({
      messages: [{ role: 'user', content: 'hello' }],
      route: 'fast',
      reasoningEffort: 'high',
    });
  });

  it('surfaces the backend error contract', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ code: 'RATE_LIMITED', message: 'slow down' }), {
        status: 429,
      }),
    );
    const gateway = service();

    await gateway.infer({ prompt: 'hello' });

    expect(gateway.answerError()).toBe('RATE_LIMITED: slow down');
    expect(gateway.answer()).toBeNull();
  });

  it('records what a synchronisation changed', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('sync')) {
        return new Response(
          JSON.stringify({
            outcomes: [
              {
                provider: 'devworld',
                added: 2,
                updated: 0,
                deactivated: 1,
                unchanged: 3,
                errors: [],
              },
            ],
          }),
          { status: 200 },
        );
      }
      const body = url.includes('health')
        ? { status: 'READY', providers: [], circuits: {}, routes: [] }
        : { models: [] };
      return new Response(JSON.stringify(body), { status: 200 });
    });
    const gateway = service();

    await gateway.synchronise();

    expect(gateway.syncOutcomes()[0].added).toBe(2);
    expect(gateway.syncOutcomes()[0].deactivated).toBe(1);
    expect(gateway.syncing()).toBe(false);
  });
});
