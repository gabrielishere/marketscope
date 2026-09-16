import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';

import { PortfolioService } from '../../api/services/portfolio.service';
import { formatCurrency, formatSignedCurrency, formatSignedPercent } from '../../core/format';

/**
 * The dashboard's first element: what the book is worth, and what it has done.
 *
 * One block of figures, not one per currency — the universe is denominated in a single
 * currency and there is no FX rate, so there is nothing to sum across.
 */
@Component({
  selector: 'app-portfolio-summary',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="panel">
      @if (portfolio$ | async; as portfolio) {
        <div class="summary">
          <div class="figure">
            <span class="label">Portfolio value</span>
            <span class="value num">{{ money(portfolio.totals.value) }}</span>
          </div>
          <div class="figure">
            <span class="label">Total return</span>
            <span class="value sub num" [class.up]="portfolio.totals.total_return >= 0"
                  [class.down]="portfolio.totals.total_return < 0">
              {{ signed(portfolio.totals.total_return) }}
              {{ pct(portfolio.totals.total_return_pct) }}
            </span>
          </div>
          <div class="figure">
            <span class="label">Today</span>
            <span class="value sub num" [class.up]="portfolio.totals.day_change >= 0"
                  [class.down]="portfolio.totals.day_change < 0">
              {{ signed(portfolio.totals.day_change) }}
              {{ pct(portfolio.totals.day_change_pct) }}
            </span>
          </div>
          <div class="figure">
            <span class="label">Cash</span>
            <span class="value sub num">{{ money(portfolio.totals.cash) }}</span>
          </div>
        </div>
      } @else {
        <div class="summary"><span class="label">Loading portfolio…</span></div>
      }
    </section>
  `,
  styles: [
    `
      .panel {
        background: var(--n-1);
        border: 1px solid var(--n-3);
        border-radius: var(--r-2);
      }
      .summary {
        display: flex;
        gap: var(--sp-6);
        padding: var(--sp-4) var(--sp-5);
        flex-wrap: wrap;
        min-height: 68px;
      }
      .figure { display: grid; gap: var(--sp-1); }
      .label {
        font-size: var(--ts-1);
        color: var(--n-5);
        text-transform: uppercase;
        letter-spacing: 0.06em;
      }
      .value { font-size: var(--ts-6); }
      .value.sub { font-size: var(--ts-5); }
      .num {
        font-family: var(--font-num);
        font-variant-numeric: tabular-nums;
      }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }
    `,
  ],
})
export class PortfolioSummaryComponent {
  readonly portfolio$ = inject(PortfolioService).getPortfolio();
  readonly money = formatCurrency;
  readonly signed = formatSignedCurrency;
  readonly pct = formatSignedPercent;
}
