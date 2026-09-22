import { TestBed } from '@angular/core/testing';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { API_CONFIG } from '../api-config';
import { Foundation } from './foundation';

const HEALTH = {
  service: 'iacode-api',
  status: 'UP',
  version: '0.1.0',
  commit: 'abc1234',
  timestamp: '2026-01-01T00:00:00.000Z',
};

const READINESS = {
  service: 'iacode-api',
  status: 'READY',
  version: '0.1.0',
  commit: 'abc1234',
  timestamp: '2026-01-01T00:00:00.000Z',
  dependencies: [
    { name: 'postgres', status: 'UP', mandatory: true, latencyMs: 1.2, detail: null },
    { name: 'redis', status: 'UP', mandatory: true, latencyMs: 0.8, detail: null },
    { name: 'minio', status: 'UP', mandatory: true, latencyMs: 2.1, detail: null },
    { name: 'temporal', status: 'UP', mandatory: true, latencyMs: 4.5, detail: null },
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

function stubBackend(): void {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const url = String(input);
    const body = url.endsWith('/health') ? HEALTH : url.endsWith('/ready') ? READINESS : VERSION;
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  });
}

async function render() {
  TestBed.configureTestingModule({
    imports: [Foundation],
    providers: [{ provide: API_CONFIG, useValue: { baseUrl: 'http://api.test' } }],
  });
  const fixture = TestBed.createComponent(Foundation);
  // detectChanges runs ngOnInit, which starts the refresh; whenStable waits for it, because the
  // service registers the request as a pending task rather than leaving a floating promise.
  fixture.detectChanges();
  await fixture.whenStable();
  fixture.detectChanges();
  return fixture;
}

afterEach(() => {
  vi.restoreAllMocks();
  TestBed.resetTestingModule();
});

describe('Foundation', () => {
  it('renders liveness, readiness and version from the backend', async () => {
    stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    expect(element.querySelector('[data-testid="liveness"]')?.textContent).toContain('UP');
    expect(element.querySelector('[data-testid="readiness"]')?.textContent).toContain('READY');
    expect(element.querySelector('[data-testid="version"]')?.textContent).toContain('3.13.15');
  });

  it('lists every dependency the readiness probe reported', async () => {
    stubBackend();
    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    const rows = element.querySelectorAll('[data-testid="readiness"] tbody tr');
    expect(rows).toHaveLength(4);
    const names = Array.from(rows).map((row) => row.querySelector('td')?.textContent?.trim());
    expect(names).toEqual(['postgres', 'redis', 'minio', 'temporal']);
  });

  it('renders an explicit failure panel when the backend is unreachable', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('connection refused'));

    const fixture = await render();
    const element = fixture.nativeElement as HTMLElement;

    // The page still renders. An unreachable API must be a visible state, not a blank page.
    expect(element.querySelector('[data-testid="liveness"]')).not.toBeNull();
    expect(element.querySelector('[data-testid="error"]')?.textContent).toContain(
      'connection refused',
    );
  });
});
