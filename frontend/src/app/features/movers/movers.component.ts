import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { switchMap } from 'rxjs';

import { MoversService } from '../../api/services/movers.service';
import { QuoteService } from '../../core/quote.service';
import { formatSignedPercent, formatVolume } from '../../core/format';

/**
 * Gainers, losers and most active — the three lists that repopulate under a scenario.
 *
 * **The API's ordering is the contract and nothing here re-sorts it.** A component
 * applying its own sort would look right while the backend's ranking was wrong, which is
 * the one defect this surface exists to expose rather than hide.
 */
@Component({
  selector: 'app-movers',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="panel">
      <h2>Movers</h2>
      @if (movers$ | async; as movers) {
        <div class="group">
          <h3>Gainers</h3>
          @for (row of movers.gainers; track row.symbol) {
            <div class="row">
              <span class="sym">{{ row.symbol }}</span>
              <span class="px num">{{ row.last.toFixed(2) }}</span>
              <span class="ch num up">{{ pct(row.day_change_pct) }}</span>
            </div>
          }
        </div>
        <div class="group">
          <h3>Losers</h3>
          @for (row of movers.losers; track row.symbol) {
            <div class="row">
              <span class="sym">{{ row.symbol }}</span>
              <span class="px num">{{ row.last.toFixed(2) }}</span>
              <span class="ch num down">{{ pct(row.day_change_pct) }}</span>
            </div>
          }
        </div>
        <div class="group">
          <h3>Most active</h3>
          @for (row of movers.most_active; track row.symbol) {
            <div class="row">
              <span class="sym">{{ row.symbol }}</span>
              <span class="px num">{{ row.last.toFixed(2) }}</span>
              <span class="ch num vol">{{ volume(row.session_volume) }}</span>
            </div>
          }
        </div>
      } @else {
        <div class="group"><h3>Loading…</h3></div>
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
      .group + .group { border-top: 1px solid var(--n-3); }
      h3 {
        font-size: var(--ts-1);
        color: var(--n-5);
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: var(--sp-3) var(--sp-4) var(--sp-2);
      }
      .row {
        display: flex;
        align-items: center;
        gap: var(--sp-3);
        height: var(--h-row);
        padding: 0 var(--sp-4);
      }
      .sym { width: 56px; font-weight: 600; }
      .px { width: var(--w-price); text-align: right; margin-left: auto; }
      .ch { width: var(--w-change); text-align: right; }
      .num { font-family: var(--font-num); font-variant-numeric: tabular-nums; }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }
      .vol { color: var(--n-6); }
    `,
  ],
})
export class MoversComponent {
  private readonly api = inject(MoversService);
  readonly pct = formatSignedPercent;
  readonly volume = formatVolume;

  /** Re-read on the same cadence as the quote poll, so the lists move with the prices. */
  readonly movers$ = inject(QuoteService).tick$.pipe(
    switchMap(() => this.api.getMovers()),
  );
}
