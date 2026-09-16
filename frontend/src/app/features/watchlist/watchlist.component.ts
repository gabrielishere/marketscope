import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { combineLatest, map, of, startWith, switchMap, catchError } from 'rxjs';

import { PortfolioService } from '../../api/services/portfolio.service';
import { Quote } from '../../api/models/quote';
import { QuoteService } from '../../core/quote.service';
import { formatSignedPercent } from '../../core/format';
import { SparklineComponent } from './sparkline.component';

/**
 * Three symbols from sectors that move **against** the holdings.
 *
 * The dashboard should show disagreement rather than everything moving together: under an
 * oil shock a refiner and an airline go opposite ways, and a watchlist of only the book's
 * own names would show one side of that. The markets tab has the full universe; this is
 * the curated view, and something has to curate it.
 */
export const WATCHLIST_EXTRAS = ['DAL', 'LUV', 'VLO'];

interface Row {
  symbol: string;
  last: number;
  dayChangePct: number;
  sparkline: number[];
  flash: 'up' | 'down' | null;
}

/**
 * The watchlist: symbol, price, day change and a sparkline, off the shared poll.
 *
 * **No layout shift on poll** is the rule that matters most here. A list that jitters
 * every two and a half seconds reads as broken however good the palette is, so the row
 * height is fixed, the numeric columns are fixed-width, and the figures are tabular.
 */
@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [AsyncPipe, SparklineComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="panel">
      <h2>Watchlist</h2>
      @for (row of rows$ | async; track row.symbol) {
        <div class="row" [class.flash-up]="row.flash === 'up'"
             [class.flash-down]="row.flash === 'down'">
          <span class="sym">{{ row.symbol }}</span>
          <app-sparkline class="spark" [points]="row.sparkline" />
          <span class="px num">{{ row.last.toFixed(2) }}</span>
          <span class="ch num" [class.up]="row.dayChangePct >= 0"
                [class.down]="row.dayChangePct < 0">{{ pct(row.dayChangePct) }}</span>
        </div>
      } @empty {
        <div class="row"><span class="sym">—</span></div>
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
      h2 {
        font-size: var(--ts-1);
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--n-5);
        padding: var(--sp-3) var(--sp-4);
        border-bottom: 1px solid var(--n-3);
      }
      .row {
        display: flex;
        align-items: center;
        gap: var(--sp-3);
        height: var(--h-row);
        padding: 0 var(--sp-4);
        border-bottom: 1px solid var(--n-3);
      }
      .row:last-child { border-bottom: 0; }
      .sym { width: 56px; font-weight: 600; }
      .spark { margin-left: auto; }
      /* Fixed widths, so a price crossing a digit boundary moves no column. */
      .px { width: var(--w-price); text-align: right; }
      .ch { width: var(--w-change); text-align: right; }
      .num { font-family: var(--font-num); font-variant-numeric: tabular-nums; }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }

      .row.flash-up { animation: flashUp var(--mo-flash) ease-out; }
      .row.flash-down { animation: flashDown var(--mo-flash) ease-out; }
      @keyframes flashUp {
        from { background: var(--sig-up-bg); }
        to { background: transparent; }
      }
      @keyframes flashDown {
        from { background: var(--sig-down-bg); }
        to { background: transparent; }
      }
      @media (prefers-reduced-motion: reduce) {
        .row.flash-up, .row.flash-down { animation: none; }
      }
    `,
  ],
})
export class WatchlistComponent {
  private readonly quotes = inject(QuoteService);
  private readonly portfolio = inject(PortfolioService);
  private readonly previous = new Map<string, number>();

  readonly pct = formatSignedPercent;

  /** Held symbols plus the extras. Never empty, even if the portfolio call fails. */
  private readonly symbols$ = this.portfolio.getPortfolio().pipe(
    map((p) => p.positions.map((position) => position.symbol)),
    catchError(() => of<string[]>([])),
    map((held) => Array.from(new Set([...held, ...WATCHLIST_EXTRAS]))),
    startWith(WATCHLIST_EXTRAS),
  );

  readonly rows$ = this.symbols$.pipe(
    switchMap((symbols) => this.quotes.quotes$(symbols)),
    map((quotes) => quotes.map((quote) => this.toRow(quote))),
  );

  private toRow(quote: Quote): Row {
    const before = this.previous.get(quote.symbol);
    this.previous.set(quote.symbol, quote.last);
    return {
      symbol: quote.symbol,
      last: quote.last,
      dayChangePct: quote.day_change_pct,
      sparkline: quote.sparkline,
      flash:
        before === undefined || before === quote.last
          ? null
          : quote.last > before
            ? 'up'
            : 'down',
    };
  }
}
