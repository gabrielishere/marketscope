import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { combineLatest, map } from 'rxjs';

import { QuoteService } from '../../core/quote.service';
import { MoversService } from '../../api/services/movers.service';
import { formatSignedPercent } from '../../core/format';
import { MarketRowComponent } from './market-row.component';

interface Row {
  symbol: string;
  name: string;
  decimals: number;
  last: number;
  dayChangePct: number;
  sessionVolume: number;
}

interface Group {
  sector: string;
  aggregate: number;
  rows: Row[];
}

/**
 * The full universe, grouped by sector — the surface the factor model is visible on.
 *
 * Under an oil spike a producer gains while an airline suffers. Scattered through a flat
 * list that is invisible; grouped, with energy rising above travel as the shock lands, it
 * needs no explanation. **The group order is the demo**, so it is recomputed from the
 * aggregate on every poll.
 *
 * **Static metadata comes from one `GET /symbols` at load.** Name, sector and decimals do
 * not change between ticks, and refetching forty-five of them twice a second would be
 * pure waste. The poll carries prices only.
 *
 * **`OnPush` with `trackBy` on the symbol** is what stops forty-five rows rebuilding
 * every poll — which would reset the scroll position and make the one surface that most
 * needs to look solid look broken.
 */
@Component({
  selector: 'app-markets',
  standalone: true,
  imports: [AsyncPipe, MarketRowComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="pane">
      <table class="mkt">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Name</th>
            <th class="col-price">Last</th>
            <th class="col-change" aria-sort="descending">Day %</th>
            <th class="col-vol">Volume</th>
          </tr>
        </thead>
        <tbody>
          @for (group of groups$ | async; track group.sector) {
            <tr class="sector-head">
              <td colspan="3">{{ group.sector }}</td>
              <td class="agg num" [class.up]="group.aggregate >= 0"
                  [class.down]="group.aggregate < 0">{{ pct(group.aggregate) }}</td>
              <td></td>
            </tr>
            @for (row of group.rows; track row.symbol) {
              <tr app-market-row [symbol]="row.symbol" [name]="row.name" [last]="row.last"
                  [decimals]="row.decimals" [dayChangePct]="row.dayChangePct"
                  [sessionVolume]="row.sessionVolume"></tr>
            }
          }
        </tbody>
      </table>
    </div>
  `,
  styles: [
    `
      .pane {
        background: var(--n-1);
        border: 1px solid var(--n-3);
        border-radius: var(--r-2);
        /* Fixed height with the body scrolling inside, so the page does not grow and a
           poll cannot resize the pane under the reader's cursor. */
        height: calc(100vh - 180px);
        overflow: auto;
        margin: var(--sp-5);
      }
      .mkt { width: 100%; border-collapse: collapse; }
      thead th {
        position: sticky;
        top: 0;
        z-index: 2;
        background: var(--n-2);
        font-size: var(--ts-1);
        font-weight: 600;
        color: var(--n-5);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        text-align: right;
        padding: var(--sp-3) var(--sp-4);
        border-bottom: 1px solid var(--n-3);
        white-space: nowrap;
      }
      thead th:first-child, thead th:nth-child(2) { text-align: left; }
      thead th[aria-sort] { color: var(--n-7); }
      .sector-head td {
        position: sticky;
        top: 37px;
        z-index: 1;
        background: var(--n-2);
        font-size: var(--ts-2);
        font-weight: 600;
        padding: var(--sp-2) var(--sp-4);
        border-top: 1px solid var(--n-4);
        border-bottom: 1px solid var(--n-3);
      }
      .agg { text-align: right; font-family: var(--font-num); font-variant-numeric: tabular-nums; }
      .col-price { width: var(--w-price); }
      .col-change { width: var(--w-change); }
      .col-vol { width: var(--w-vol); }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }
    `,
  ],
})
export class MarketsComponent {
  private readonly quotes = inject(QuoteService);
  private readonly movers = inject(MoversService);
  readonly pct = formatSignedPercent;

  /** One `GET /symbols` at load for the static columns; the poll carries prices. */
  readonly groups$ = combineLatest([
    this.quotes.universe$,
    this.quotes.allQuotes$(),
  ]).pipe(
    map(([universe, quotes]) => {
      const meta = new Map(universe.map((entry) => [entry.symbol, entry]));
      const bySector = new Map<string, Row[]>();
      for (const quote of quotes) {
        const entry = meta.get(quote.symbol);
        if (!entry) continue;
        const row: Row = {
          symbol: quote.symbol,
          name: entry.name,
          decimals: entry.decimals,
          last: quote.last,
          dayChangePct: quote.day_change_pct,
          sessionVolume: 0,
        };
        const rows = bySector.get(entry.sector) ?? [];
        rows.push(row);
        bySector.set(entry.sector, rows);
      }
      const groups: Group[] = Array.from(bySector.entries()).map(([sector, rows]) => ({
        sector,
        aggregate: rows.reduce((sum, r) => sum + r.dayChangePct, 0) / (rows.length || 1),
        rows: rows.sort((a, b) => b.dayChangePct - a.dayChangePct),
      }));
      // Groups order by their aggregate: this is what puts energy above travel as an
      // oil shock lands, and it is the whole point of the surface.
      return groups.sort((a, b) => b.aggregate - a.aggregate);
    }),
  );
}
