import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { switchMap } from 'rxjs';

import { ImpactService } from '../../api/services/impact.service';
import { QuoteService } from '../../core/quote.service';
import { formatSignedPercent } from '../../core/format';
import { PeerComparisonComponent } from './peer-comparison.component';

/** The collapsed view shows at most this many bars. Capped here, not by short data. */
const MAX_BARS = 3;

/**
 * Why it moved — plain language first, the full attribution behind a disclosure.
 *
 * **The default view is for someone who does not know what a beta is.** An exposure value
 * like `oil beta -0.9` appearing in the collapsed panel is the specific failure O18 names,
 * so nothing here binds `exposure` outside the `<details>` block.
 *
 * The sentences arrive pre-written from the backend, one per factor, carrying no beta and
 * no jargon. This component renders them; it does not compose its own.
 */
@Component({
  selector: 'app-impact-panel',
  standalone: true,
  imports: [AsyncPipe, PeerComparisonComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="panel">
      <h2>Why it moved</h2>
      @if (impact$ | async; as impact) {
        <div class="head">
          <span class="move num" [class.up]="impact.move_pct >= 0"
                [class.down]="impact.move_pct < 0">{{ pct(impact.move_pct) }}</span>
          <span class="sym">{{ impact.symbol }}</span>
        </div>

        <!-- Plain language. No exposure value is bound anywhere in this block. -->
        <ul class="sentences">
          @for (row of impact.contributions.slice(0, MAX_BARS); track row.factor) {
            <li>{{ row.sentence }}</li>
          }
        </ul>

        <div class="bars">
          @for (row of impact.contributions.slice(0, MAX_BARS); track row.factor) {
            <div class="bar">
              <span class="bl">{{ label(row.factor) }}</span>
              <span class="track">
                <span class="fill" [class.pos]="row.contribution >= 0"
                      [class.neg]="row.contribution < 0"
                      [style.width.%]="width(row.contribution, impact.contributions)"></span>
              </span>
            </div>
          }
        </div>

        <details class="detail">
          <summary>Full attribution</summary>
          <table class="attrib">
            <tr><th>Factor</th><th>Exposure</th><th>Factor move</th><th>Contribution</th></tr>
            @for (row of impact.contributions; track row.factor) {
              <tr>
                <td>{{ label(row.factor) }}</td>
                <td class="num">{{ row.exposure.toFixed(1) }}</td>
                <td class="num">{{ pct(row.factor_move_pct) }}</td>
                <td class="num" [class.up]="row.contribution >= 0"
                    [class.down]="row.contribution < 0">{{ pct(row.contribution * 100) }}</td>
              </tr>
            }
            <tr>
              <td>Specific to this company</td><td class="num">—</td><td class="num">—</td>
              <td class="num">{{ pct(impact.residual * 100) }}</td>
            </tr>
          </table>
        </details>

        <app-peer-comparison [peers]="impact.peers" />
      } @else {
        <div class="head"><span class="sym">Loading attribution…</span></div>
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
      .head {
        display: flex;
        align-items: baseline;
        gap: var(--sp-3);
        padding: var(--sp-4) var(--sp-4) var(--sp-3);
      }
      .move {
        font-size: var(--ts-6);
        font-family: var(--font-num);
        font-variant-numeric: tabular-nums;
      }
      .sym { color: var(--n-6); font-size: var(--ts-3); }
      .sentences { display: grid; gap: var(--sp-2); padding: 0 var(--sp-4) var(--sp-3); }
      .sentences li { list-style: none; font-size: var(--ts-3); color: var(--n-6); }
      .bars { display: grid; gap: var(--sp-2); padding: 0 var(--sp-4) var(--sp-4); }
      .bar {
        display: grid;
        grid-template-columns: 72px 1fr;
        align-items: center;
        gap: var(--sp-3);
      }
      .bl { font-size: var(--ts-2); color: var(--n-5); }
      .track {
        height: var(--sp-2);
        background: var(--n-2);
        border-radius: var(--r-1);
        position: relative;
      }
      .fill { position: absolute; top: 0; bottom: 0; border-radius: var(--r-1); }
      .fill.pos { left: 50%; background: var(--sig-up); }
      .fill.neg { right: 50%; background: var(--sig-down); }
      .detail { border-top: 1px solid var(--n-3); }
      .detail summary {
        padding: var(--sp-3) var(--sp-4);
        cursor: pointer;
        font-size: var(--ts-2);
        color: var(--n-6);
      }
      .attrib { width: 100%; border-collapse: collapse; }
      .attrib th, .attrib td {
        padding: var(--sp-2) var(--sp-4);
        font-size: var(--ts-2);
        border-top: 1px solid var(--n-3);
        text-align: right;
      }
      .attrib th:first-child, .attrib td:first-child {
        text-align: left;
        color: var(--n-6);
      }
      .num { font-family: var(--font-num); font-variant-numeric: tabular-nums; }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }
    `,
  ],
})
export class ImpactPanelComponent {
  private readonly api = inject(ImpactService);
  readonly MAX_BARS = MAX_BARS;
  readonly pct = formatSignedPercent;

  readonly impact$ = inject(QuoteService).tick$.pipe(
    switchMap(() => this.api.getSymbolImpact({ symbol: 'XOM' })),
  );

  label(factor: string): string {
    const labels: Record<string, string> = {
      market: 'Market',
      rates: 'Rates',
      oil: 'Oil',
      usd: 'USD',
      credit: 'Credit',
    };
    return labels[factor] ?? factor;
  }

  /** Half-width bars diverging from a centre line, scaled to the largest contribution. */
  width(value: number, all: { contribution: number }[]): number {
    const largest = Math.max(...all.map((row) => Math.abs(row.contribution)), 1e-9);
    return (Math.abs(value) / largest) * 48;
  }
}
