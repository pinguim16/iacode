/**
 * The Agent Runtime page.
 *
 * Operational, not a product surface: write a task, choose a team, start it, watch it, read the
 * answer, cancel it. There is deliberately no conversation, no editor, no file tree and no tool
 * button — those belong to later Gates, and a page that showed a control for one would describe a
 * capability that does not exist.
 *
 * The one thing this page is careful about is the tool pause. When a run is waiting it says which
 * tool it is waiting for and that the request is pending, and it offers **nothing** that would run
 * it. Gate 2 executes no tool at all; Gate 3's sandbox is what will.
 */

import { Component, OnDestroy, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AgentRuntimeService, TERMINAL_STATES } from './agent-runtime.service';

@Component({
  selector: 'app-agent-runtime',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './agent-runtime.html',
  styleUrl: './agent-runtime.css',
})
export class AgentRuntime implements OnInit, OnDestroy {
  protected readonly runtime = inject(AgentRuntimeService);

  protected readonly task = signal('Reply with exactly: IACODE_AGENT_OK');
  protected readonly team = signal('single-agent');
  protected readonly target = signal('');

  protected readonly run = computed(() => this.runtime.run());
  protected readonly events = computed(() => this.runtime.events());

  protected readonly finished = computed(() => {
    const current = this.runtime.run();
    return current !== null && TERMINAL_STATES.has(current.state);
  });

  protected readonly waiting = computed(() => this.runtime.run()?.state === 'WAITING_FOR_TOOL');

  protected readonly canCancel = computed(() => {
    const current = this.runtime.run();
    return current !== null && !TERMINAL_STATES.has(current.state);
  });

  ngOnInit(): void {
    void this.runtime.refresh();
  }

  ngOnDestroy(): void {
    this.runtime.stopFollowing();
  }

  protected async start(): Promise<void> {
    await this.runtime.start({
      task: this.task(),
      team: this.team(),
      target: this.target() || null,
    });
  }

  protected async cancel(): Promise<void> {
    await this.runtime.cancel();
  }

  protected async open(runId: string): Promise<void> {
    await this.runtime.follow(runId);
  }

  /** A class name for a state, so the page reads at a glance without repeating the vocabulary. */
  protected tone(state: string | null | undefined): string {
    if (state === 'SUCCEEDED') {
      return 'ok';
    }
    if (state === 'FAILED') {
      return 'bad';
    }
    if (state === 'WAITING_FOR_TOOL') {
      return 'waiting';
    }
    return 'unknown';
  }

  /** How much of a run's budget is gone, for the two limits that always apply. */
  protected spent(): string {
    const current = this.runtime.run();
    if (!current) {
      return '';
    }
    const budget = current.budget;
    return `${budget.turnsUsed}/${budget.maxTurns} turns, ${budget.modelCallsUsed}/${budget.maxModelCalls} calls`;
  }

  /** What a run cost, or that it is not knowable. Never zero, which would be a different claim. */
  protected cost(): string {
    const summary = this.runtime.run()?.summary;
    if (!summary) {
      return '';
    }
    return summary.costKnown && summary.cost !== null ? summary.cost.toFixed(6) : 'UNKNOWN';
  }

  /** One short line per event, built from the fields the payload is allowed to carry. */
  protected describe(payload: Record<string, unknown>): string {
    const parts: string[] = [];
    for (const key of ['agent', 'tool', 'provider', 'model', 'turn', 'errorType', 'summary']) {
      const value = payload[key];
      if (value !== undefined && value !== null && value !== '') {
        parts.push(`${key}=${String(value)}`);
      }
    }
    return parts.join(' ');
  }
}
