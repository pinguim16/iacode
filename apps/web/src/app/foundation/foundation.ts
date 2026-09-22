/**
 * The Foundation page.
 *
 * It identifies nothing and navigates nowhere: the shell does both. This renders the live state of
 * the backend — liveness, readiness with the state of every dependency, and the running version —
 * which is enough to answer "is the stack up" from a browser.
 */

import { Component, OnInit, inject, signal } from '@angular/core';

import { FoundationStatusService } from './foundation-status.service';

@Component({
  selector: 'app-foundation',
  standalone: true,
  imports: [],
  templateUrl: './foundation.html',
})
export class Foundation implements OnInit {
  protected readonly status = inject(FoundationStatusService);
  protected readonly lastRefreshed = signal<string | null>(null);

  ngOnInit(): void {
    void this.refresh();
  }

  protected async refresh(): Promise<void> {
    await this.status.refresh();
    this.lastRefreshed.set(new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'));
  }

  /** The CSS modifier for a status word, so the template has no branching logic in it. */
  protected tone(value: string | null | undefined): string {
    if (value === 'UP' || value === 'READY') {
      return 'ok';
    }
    if (value === 'SKIPPED' || value === null || value === undefined) {
      return 'unknown';
    }
    return 'bad';
  }
}
