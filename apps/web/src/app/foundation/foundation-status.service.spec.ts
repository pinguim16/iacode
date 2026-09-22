import { TestBed } from '@angular/core/testing';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { API_CONFIG } from '../api-config';
import { FoundationStatusService } from './foundation-status.service';

const HEALTH = {
  service: 'iacode-api',
  status: 'UP',
  version: '0.1.0',
  commit: 'abc1234',
  timestamp: '2026-01-01T00:00:00.000Z',
};

const READINESS = {
  service: 'iacode-api',
  status: 'NOT_READY',
  version: '0.1.0',
  commit: 'abc1234',
  timestamp: '2026-01-01T00:00:00.000Z',
  dependencies: [
    { name: 'postgres', status: 'UP', mandatory: true, latencyMs: 1.2, detail: null },
    { name: 'redis', status: 'DOWN', mandatory: true, latencyMs: 5.4, detail: 'refused' },
  ],
};

const VERSION = {
  service: 'iacode-api',
  version: '0.1.0',
  commit: 'abc1234',
  buildTimestamp: '2026-01-01T00:00:00Z',
  pythonVersion: '3.13.15',
  environment: 'local',
};

function respond(url: string): Response {
  const body = url.endsWith('/health') ? HEALTH : url.endsWith('/ready') ? READINESS : VERSION;
  // /ready answers 503 when a dependency is down, and the body is the useful part.
  const status = url.endsWith('/ready') ? 503 : 200;
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function service(baseUrl = 'http://api.test'): FoundationStatusService {
  TestBed.configureTestingModule({
    providers: [{ provide: API_CONFIG, useValue: { baseUrl } }],
  });
  return TestBed.inject(FoundationStatusService);
}

afterEach(() => {
  vi.restoreAllMocks();
  TestBed.resetTestingModule();
});

describe('FoundationStatusService', () => {
  it('reads every foundation endpoint through the configured base address', async () => {
    const fetchImpl = vi
      .spyOn(globalThis, 'fetch')
      .mockImplementation(async (input) => respond(String(input)));

    const instance = service();
    await instance.refresh();

    const requested = fetchImpl.mock.calls.map((call) => String(call[0])).sort();
    expect(requested).toEqual([
      'http://api.test/health',
      'http://api.test/ready',
      'http://api.test/version',
    ]);
  });

  it('keeps the readiness payload of a 503, because that is where the reason is', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => respond(String(input)));

    const instance = service();
    await instance.refresh();

    expect(instance.readiness()?.status).toBe('NOT_READY');
    expect(instance.readiness()?.dependencies).toHaveLength(2);
    expect(instance.readiness()?.dependencies[1]).toMatchObject({
      name: 'redis',
      status: 'DOWN',
      detail: 'refused',
    });
    expect(instance.error()).toBeNull();
  });

  it('exposes liveness and version separately from readiness', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => respond(String(input)));

    const instance = service();
    await instance.refresh();

    expect(instance.health()?.status).toBe('UP');
    expect(instance.version()?.pythonVersion).toBe('3.13.15');
  });

  it('records an unreachable backend as an error instead of throwing', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('connection refused'));

    const instance = service();
    await expect(instance.refresh()).resolves.toBeUndefined();

    expect(instance.error()).toContain('connection refused');
    expect(instance.health()).toBeNull();
    expect(instance.loading()).toBe(false);
  });

  it('clears the loading flag even when the request fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('boom'));

    const instance = service();
    await instance.refresh();

    expect(instance.loading()).toBe(false);
  });
});
