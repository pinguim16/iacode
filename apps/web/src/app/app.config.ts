import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';

/**
 * Providers shared by the real bootstrap and by the tests.
 *
 * `API_CONFIG` is deliberately absent: it is resolved at run time in `main.ts` and supplied by each
 * test with the value that test needs. A default here would let a test pass against a configuration
 * nobody meant to exercise.
 */
export const appConfig: ApplicationConfig = {
  providers: [provideBrowserGlobalErrorListeners()],
};
