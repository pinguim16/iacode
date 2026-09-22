/**
 * Where the backend lives — resolved once, at start-up, and never written anywhere else.
 *
 * The address is read from `config.json`, which the container writes from its environment when it
 * starts. That is deliberate: an address compiled into the bundle would mean one image per
 * environment, and the whole point of building an artefact is that the same bytes run everywhere.
 *
 * `config.json` holds an address and nothing else. It is served unauthenticated to every visitor,
 * so a credential placed here would be published to anyone who opens the page.
 */

import { InjectionToken } from '@angular/core';

export interface ApiConfig {
  /** Absolute base URL of the IACode API, without a trailing slash. */
  readonly baseUrl: string;
}

export const API_CONFIG = new InjectionToken<ApiConfig>('IACODE_API_CONFIG');

/**
 * Used when `config.json` cannot be read. Same origin, so a reverse proxy in front of both the
 * page and the API keeps working; a developer running the two separately gets a visible failure
 * instead of a silent fallback to somebody else's backend.
 */
export const DEFAULT_API_CONFIG: ApiConfig = { baseUrl: '' };

const CONFIG_URL = 'config.json';

/** Strip a trailing slash so callers can always join with `/path`. */
export function normaliseBaseUrl(value: unknown): string {
  if (typeof value !== 'string') {
    return DEFAULT_API_CONFIG.baseUrl;
  }
  return value.trim().replace(/\/+$/, '');
}

/**
 * Read the runtime configuration.
 *
 * A failure is logged and answered with the default rather than thrown: an unreachable
 * `config.json` should produce an application that renders and reports that the backend is
 * unreachable, not a blank page with an error in the console.
 */
export async function loadApiConfig(fetchImpl: typeof fetch = fetch): Promise<ApiConfig> {
  try {
    const response = await fetchImpl(CONFIG_URL, { cache: 'no-store' });
    if (!response.ok) {
      throw new Error(`config.json responded ${response.status}`);
    }
    const body: unknown = await response.json();
    const baseUrl = normaliseBaseUrl((body as Record<string, unknown>)?.['apiBaseUrl']);
    return { baseUrl };
  } catch (error) {
    console.warn('falling back to the same-origin API base address', error);
    return DEFAULT_API_CONFIG;
  }
}
