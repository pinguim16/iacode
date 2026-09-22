/**
 * The Foundation page.
 *
 * Gate 0's frontend is a shell, on purpose. It identifies the product, and it renders the live
 * state of the backend — liveness, readiness with the state of every dependency, and the running
 * version. That is enough to answer "is the stack up" from a browser, which is the only question
 * this Gate's frontend needs to answer.
 *
 * There is no dashboard, no navigation and no screen for agents, models or training. Those belong
 * to later Gates, and a page that showed empty panels for them would describe capabilities that do
 * not exist.
 */

import { Component, OnInit, inject, signal } from '@angular/core';

import { FoundationStatusService } from './foundation-status.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
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
