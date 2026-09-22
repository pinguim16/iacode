/**
 * The Model Gateway page.
 *
 * Operational, not a product surface: provider state, the discovered catalog, a synchronisation
 * button and a minimal playground for one prompt. There is deliberately no conversation, no
 * history, no persona and no tool execution — those belong to later Gates, and a page that showed
 * empty panels for them would describe capabilities that do not exist.
 */

import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { GatewayService, ModelSummary } from './gateway.service';

/** The efforts the contract accepts. The models that accept them are a catalog question. */
const REASONING_EFFORTS = ['', 'low', 'medium', 'high', 'max'] as const;

@Component({
  selector: 'app-gateway',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './gateway.html',
  styleUrl: './gateway.css',
})
export class Gateway implements OnInit {
  protected readonly gateway = inject(GatewayService);
  protected readonly efforts = REASONING_EFFORTS;

  protected readonly prompt = signal('Reply with exactly: IACODE_GATEWAY_OK');
  protected readonly target = signal('');
  protected readonly effort = signal('');

  /** Models first, then a stable order, so a refresh does not reshuffle the table. */
  protected readonly catalog = computed(() =>
    [...this.gateway.models()].sort((left, right) =>
      `${left.provider}:${left.model}`.localeCompare(`${right.provider}:${right.model}`),
    ),
  );

  protected readonly routes = computed(() => this.gateway.health()?.routes ?? []);

  ngOnInit(): void {
    void this.gateway.refresh();
  }

  protected async refresh(): Promise<void> {
    await this.gateway.refresh();
  }

  protected async synchronise(): Promise<void> {
    await this.gateway.synchronise();
  }

  protected async send(): Promise<void> {
    const target = this.target();
    await this.gateway.infer({
      prompt: this.prompt(),
      // A qualified reference is an explicit model; anything else is a route alias. One field
      // rather than two, because a form that lets you fill in both has to decide which wins, and
      // the contract deliberately refuses a request that names both.
      model: target.includes(':') ? target : null,
      route: target && !target.includes(':') ? target : null,
      reasoningEffort: this.effort() || null,
    });
  }

  protected tone(value: string | boolean | null | undefined): string {
    if (value === true || value === 'READY' || value === 'SUPPORTED') {
      return 'ok';
    }
    if (value === false || value === 'DEGRADED' || value === 'UNSUPPORTED') {
      return 'bad';
    }
    return 'unknown';
  }

  protected capability(model: ModelSummary, name: string): string {
    return model.capabilities[name]?.state ?? 'UNKNOWN';
  }

  protected provenance(model: ModelSummary, name: string): string {
    return model.capabilities[name]?.provenance ?? 'UNKNOWN';
  }
}
