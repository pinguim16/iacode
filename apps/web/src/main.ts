/**
 * Bootstrap.
 *
 * The runtime configuration is read *before* the application starts, so no component ever has to
 * handle a half-configured state. The alternative — bootstrapping first and resolving the address
 * later — means every request has to wait on a promise that may not have settled, and the first
 * render happens against a backend address that is not yet known.
 */

import { bootstrapApplication } from '@angular/platform-browser';

import { API_CONFIG, loadApiConfig } from './app/api-config';
import { App } from './app/app';
import { appConfig } from './app/app.config';

loadApiConfig()
  .then((config) =>
    bootstrapApplication(App, {
      ...appConfig,
      providers: [...appConfig.providers, { provide: API_CONFIG, useValue: config }],
    }),
  )
  .catch((error) => console.error(error));
