import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';

import { MoversService } from '../../api/services/movers.service';
import { formatSignedPercent } from '../../core/format';

/** The five factors as display labels. The API's keys are identifier-style. */
const FACTOR_LABELS: Record<string, string> = {
  market: 'Market',
  rates: 'Rates',
  oil: 'Oil',
  usd: 'USD',
  credit: 'Credit',
};

/**
 * The five macro drivers, one per factor, in factor order.
 *
 * This is where an audience sees a shock land: under an oil scenario the Oil tile moves
 * hard and the other four barely, which makes the factor model legible without anyone
 * explaining what a factor is.
 *
 * Rendered in the order the API returns. `GET /macro` iterates the factor keys, so the
 * order is `market, rates, oil, usd, credit` and nothing here sorts it.
 */
@Component({
  selector: 'app-macro-strip',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="macro">
      @for (driver of drivers$ | async; track driver.symbol) {
        <div class="tile">
          <span class="name">{{ label(driver.factor) }}</span>
          <span class="px num">{{ driver.last.toFixed(2) }}</span>
          <span class="num" [class.up]="driver.day_change_pct >= 0"
                [class.down]="driver.day_change_pct < 0">
            {{ pct(driver.day_change_pct) }}
          </span>
        </div>
      } @empty {
        @for (slot of [1, 2, 3, 4, 5]; track slot) {
          <div class="tile"><span class="name">—</span><span class="px num">—</span></div>
        }
      }
    </div>
  `,
  styles: [
    `
      .macro {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: var(--sp-3);
      }
      @media (max-width: 760px) {
        .macro { grid-template-columns: repeat(2, 1fr); }
      }
      .tile {
        background: var(--n-1);
        border: 1px solid var(--n-3);
        border-radius: var(--r-2);
        padding: var(--sp-3) var(--sp-4);
        display: grid;
        gap: var(--sp-1);
        min-height: 76px;
      }
      .name {
        font-size: var(--ts-1);
        color: var(--n-5);
        text-transform: uppercase;
        letter-spacing: 0.06em;
      }
      .px { font-size: var(--ts-5); }
      .num { font-family: var(--font-num); font-variant-numeric: tabular-nums; }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }
    `,
  ],
})
export class MacroStripComponent {
  readonly drivers$ = inject(MoversService).listMacroDrivers();
  readonly pct = formatSignedPercent;
  label(factor: string): string {
    return FACTOR_LABELS[factor] ?? factor;
  }
}
