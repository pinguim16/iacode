/**
 * The three pages this build has.
 *
 * Lazy, so a page's code is not in the bundle a visitor downloads to look at something else. The
 * wildcard redirects rather than 404s: a mistyped path in an operational tool should land
 * somewhere useful, and there is no content here worth telling a visitor they failed to find.
 */

import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    title: 'IACode — Foundation',
    loadComponent: () => import('./foundation/foundation').then((module) => module.Foundation),
  },
  {
    path: 'gateway',
    title: 'IACode — Model Gateway',
    loadComponent: () => import('./gateway/gateway').then((module) => module.Gateway),
  },
  {
    path: 'agent-runtime',
    title: 'IACode — Agent Runtime',
    loadComponent: () =>
      import('./agent-runtime/agent-runtime').then((module) => module.AgentRuntime),
  },
  { path: '**', redirectTo: '' },
];
