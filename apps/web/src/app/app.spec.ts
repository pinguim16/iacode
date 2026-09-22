import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { API_CONFIG } from './api-config';
import { App } from './app';
import { routes } from './app.routes';

function stubBackend(): void {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const url = String(input);
    const body = url.includes('/gateway/health')
      ? {
          status: 'DEGRADED',
          contractVersion: '1.0.0',
          providers: [],
          circuits: {},
          catalogSize: 0,
          defaultModel: null,
          routes: [],
        }
      : url.includes('/gateway/models')
        ? { total: 0, models: [] }
        : { service: 'iacode-api', status: 'UP', version: '0.1.0', commit: 'abc', timestamp: 'x' };
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  });
}

/**
 * Render the shell and navigate it.
 *
 * `RouterTestingHarness` mounts the *routed* component as the root, which is the wrong subject
 * here: the shell is what carries the identity and the navigation, and a harness that replaced it
 * would leave both untested.
 */
async function renderShell(path: string) {
  TestBed.configureTestingModule({
    imports: [App],
    providers: [
      provideRouter(routes),
      { provide: API_CONFIG, useValue: { baseUrl: 'http://api.test' } },
    ],
  });
  const fixture = TestBed.createComponent(App);
  fixture.detectChanges();
  await TestBed.inject(Router).navigateByUrl(path);
  await fixture.whenStable();
  fixture.detectChanges();
  return fixture;
}

afterEach(() => {
  vi.restoreAllMocks();
  TestBed.resetTestingModule();
});

describe('App shell', () => {
  it('identifies the product and offers every page it has', async () => {
    stubBackend();
    const element = (await renderShell('/')).nativeElement as HTMLElement;

    expect(element.querySelector('h1')?.textContent).toContain('IACode');
    const links = Array.from(element.querySelectorAll('nav a')).map((item) =>
      item.textContent?.trim(),
    );
    expect(links).toEqual(['Foundation', 'Model Gateway', 'Agent Runtime']);
  });

  it('renders the Foundation page at the root', async () => {
    stubBackend();
    const element = (await renderShell('/')).nativeElement as HTMLElement;

    expect(element.querySelector('[data-testid="liveness"]')).not.toBeNull();
  });

  it('routes to the Model Gateway page', async () => {
    stubBackend();
    const element = (await renderShell('/gateway')).nativeElement as HTMLElement;

    expect(element.querySelector('[data-testid="providers"]')).not.toBeNull();
    expect(element.querySelector('[data-testid="playground"]')).not.toBeNull();
  });

  it('adds no conversation capability', async () => {
    stubBackend();
    const element = (await renderShell('/gateway')).nativeElement as HTMLElement;
    // The page, not the shell: Gate 2 adds an Agent Runtime link to the navigation, and reading
    // the navigation as page content would make this assertion about the menu rather than about
    // what the gateway page offers.
    const text = element.querySelector('router-outlet')?.parentElement?.textContent ?? '';

    // The gateway is a gateway, not a chat application. No history, no persona, no tool execution.
    for (const absent of ['Conversation', 'History', 'Persona', 'Run tool', 'Execute']) {
      expect(text.replace(/Foundation|Model Gateway|Agent Runtime/g, '')).not.toContain(absent);
    }
  });
});
