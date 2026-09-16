import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';

import { ScenarioService } from '../../core/scenario.service';
import { ScenarioId } from '../../api/models/scenario-id';

/**
 * The control the whole demo is driven from — the thing a presenter clicks.
 *
 * "Reset to normal" is first because it is the state a presenter returns to between
 * scenarios, and it reads as plain language rather than as `baseline`.
 *
 * Selecting POSTs and *then* refreshes quotes. The ordering lives in `ScenarioService`,
 * in the response's `tap`: refreshing beside the POST would fetch quotes the server has
 * not yet changed, so the click would appear to do nothing and the market would move two
 * seconds later.
 */
@Component({
  selector: 'app-scenario-selector',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="panel">
      <h2>Scenario</h2>
      <div class="select-wrap">
        <select [value]="(active$ | async)?.id ?? ''" (change)="choose($event)">
          <option value="__reset__">Reset to normal</option>
          @for (item of library$ | async; track item.id) {
            @if (!isBaseline(item.id)) {
              <option [value]="item.id">{{ item.name }}</option>
            }
          }
        </select>
      </div>
    </section>
  `,
  styles: [
    `
      .panel {
        background: var(--n-1);
        border: 1px solid var(--n-3);
        border-radius: var(--r-2);
        overflow: hidden;
      }
      h2 {
        font-size: var(--ts-1);
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--n-5);
        padding: var(--sp-3) var(--sp-4);
        border-bottom: 1px solid var(--n-3);
      }
      .select-wrap { padding: var(--sp-3) var(--sp-4); }
      select {
        width: 100%;
        height: 32px;
        padding: 0 var(--sp-2);
        background: var(--n-2);
        color: var(--n-7);
        border: 1px solid var(--n-4);
        border-radius: var(--r-1);
        font: var(--ts-3) var(--font);
      }
    `,
  ],
})
export class ScenarioSelectorComponent {
  private readonly scenarios = inject(ScenarioService);
  readonly library$ = this.scenarios.library$;
  readonly active$ = this.scenarios.active$;

  isBaseline(id: string): boolean {
    return id === 'baseline';
  }

  choose(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    if (value === '__reset__') {
      this.scenarios.reset().subscribe();
    } else {
      this.scenarios.activate(value as ScenarioId).subscribe();
    }
  }
}
