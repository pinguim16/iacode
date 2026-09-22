import { describe, expect, it, vi } from 'vitest';

import { DEFAULT_API_CONFIG, loadApiConfig, normaliseBaseUrl } from './api-config';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('api configuration', () => {
  it('normalises a base address by removing trailing slashes', () => {
    expect(normaliseBaseUrl('http://localhost:18080/')).toBe('http://localhost:18080');
    expect(normaliseBaseUrl('http://localhost:18080///')).toBe('http://localhost:18080');
    expect(normaliseBaseUrl('  http://localhost:18080  ')).toBe('http://localhost:18080');
  });

  it('falls back to the same origin when the value is not a string', () => {
    expect(normaliseBaseUrl(undefined)).toBe(DEFAULT_API_CONFIG.baseUrl);
    expect(normaliseBaseUrl(42)).toBe(DEFAULT_API_CONFIG.baseUrl);
  });

  it('reads the address from the runtime configuration file', async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ apiBaseUrl: 'http://localhost:18080/' }));

    const config = await loadApiConfig(fetchImpl as unknown as typeof fetch);

    expect(config.baseUrl).toBe('http://localhost:18080');
    expect(fetchImpl).toHaveBeenCalledWith('config.json', { cache: 'no-store' });
  });

  it('falls back instead of throwing when the configuration cannot be read', async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new Error('offline'));
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => undefined);

    const config = await loadApiConfig(fetchImpl as unknown as typeof fetch);

    // A blank page is a worse outcome than a page that reports the backend as unreachable.
    expect(config).toEqual(DEFAULT_API_CONFIG);
    expect(warn).toHaveBeenCalled();
    warn.mockRestore();
  });

  it('falls back when the configuration file responds with an error status', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({}, 404));
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => undefined);

    const config = await loadApiConfig(fetchImpl as unknown as typeof fetch);

    expect(config).toEqual(DEFAULT_API_CONFIG);
    warn.mockRestore();
  });
});
