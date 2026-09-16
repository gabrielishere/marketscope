import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { formatSignedPercent, formatVolume } from '../../core/format';

/** One instrument's row. `OnPush` so a poll re-renders only the rows that changed. */
@Component({
  selector: 'tr[app-market-row]',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <td class="sym">{{ symbol }}</td>
    <td class="name">{{ name }}</td>
    <td class="num col-price">{{ last.toFixed(decimals) }}</td>
    <td class="num col-change" [class.up]="dayChangePct >= 0" [class.down]="dayChangePct < 0">
      {{ pct(dayChangePct) }}
    </td>
    <td class="num col-vol">{{ vol(sessionVolume) }}</td>
  `,
  styles: [
    `
      :host { display: table-row; }
      td {
        height: var(--h-row);
        padding: 0 var(--sp-4);
        border-bottom: 1px solid var(--n-3);
        text-align: right;
        white-space: nowrap;
      }
      td.sym, td.name { text-align: left; }
      .sym { font-weight: 600; }
      .name { color: var(--n-6); }
      .num { font-family: var(--font-num); font-variant-numeric: tabular-nums; }
      .col-price { width: var(--w-price); }
      .col-change { width: var(--w-change); }
      .col-vol { width: var(--w-vol); }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }
    `,
  ],
})
export class MarketRowComponent {
  @Input({ required: true }) symbol = '';
  @Input({ required: true }) name = '';
  @Input({ required: true }) last = 0;
  @Input({ required: true }) decimals = 2;
  @Input({ required: true }) dayChangePct = 0;
  @Input({ required: true }) sessionVolume = 0;
  readonly pct = formatSignedPercent;
  readonly vol = formatVolume;
}
