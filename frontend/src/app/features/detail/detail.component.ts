import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { combineLatest, map, switchMap } from 'rxjs';

import { MarketService } from '../../api/services/market.service';
import { ScenarioService } from '../../core/scenario.service';
import { Timeframe } from '../../api/models/timeframe';
import { QuoteService } from '../../core/quote.service';
import { formatSignedPercent } from '../../core/format';
import { ChartComponent } from './chart.component';

/** The four timeframes the API accepts. An unknown one is a 422, never a default. */
const TIMEFRAMES: Timeframe[] = [
  Timeframe.$1M,
  Timeframe.$5M,
  Timeframe.$15M,
  Timeframe.Session,
];

/**
 * The instrument detail: the series, the timeframe toggle and the activation marker.
 */
@Component({
  selector: 'app-detail',
  standalone: true,
  imports: [AsyncPipe, ChartComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="panel">
      <div class="chart-head">
        <span class="sym">{{ symbol() }}</span>
        @if (view$ | async; as view) {
          <span class="num" [class.up]="view.movePct >= 0" [class.down]="view.movePct < 0">
            {{ view.last.toFixed(2) }} {{ pct(view.movePct) }}
          </span>
        }
        <div class="timeframes">
          @for (tf of timeframes; track tf) {
            <button class="tf" [attr.aria-pressed]="tf === timeframe()"
                    (click)="setTimeframe(tf)">{{ tf }}</button>
          }
        </div>
      </div>
      @if (view$ | async; as view) {
        <app-chart [candles]="view.candles" [activatedAt]="view.activatedAt"
                   [markerLabel]="view.scenarioName" />
      }
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
      .chart-head {
        display: flex;
        align-items: center;
        gap: var(--sp-3);
        padding: var(--sp-3) var(--sp-4);
        border-bottom: 1px solid var(--n-3);
      }
      .sym { font-size: var(--ts-5); font-weight: 600; }
      .num {
        font-family: var(--font-num);
        font-variant-numeric: tabular-nums;
        font-size: var(--ts-4);
      }
      .timeframes { margin-left: auto; display: flex; gap: var(--sp-1); }
      .tf {
        padding: var(--sp-1) var(--sp-2);
        border-radius: var(--r-1);
        background: none;
        border: 1px solid transparent;
        color: var(--n-5);
        font: var(--ts-2) var(--font);
        cursor: pointer;
      }
      .tf[aria-pressed='true'] {
        background: var(--n-2);
        border-color: var(--n-4);
        color: var(--n-7);
      }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }
    `,
  ],
})
export class DetailComponent {
  private readonly market = inject(MarketService);
  private readonly scenarios = inject(ScenarioService);
  private readonly quotes = inject(QuoteService);

  readonly timeframes = TIMEFRAMES;
  readonly symbol = signal('XOM');
  readonly timeframe = signal<Timeframe>(Timeframe.$5M);
  readonly pct = formatSignedPercent;

  readonly view$ = this.quotes.tick$.pipe(
    switchMap(() =>
      combineLatest([
        this.market.listCandles({ symbol: this.symbol(), tf: this.timeframe() }),
        this.scenarios.active$,
      ]),
    ),
    map(([candles, active]) => {
      const first = candles.length ? candles[0].open : 0;
      const last = candles.length ? candles[candles.length - 1].close : 0;
      return {
        candles,
        last,
        movePct: first ? (last / first - 1) * 100 : 0,
        // Driven by the server's activation tick, not by a scenario being selected.
        activatedAt: active.activated_at,
        scenarioName: active.name,
      };
    }),
  );

  setTimeframe(tf: Timeframe): void {
    this.timeframe.set(tf);
  }
}
