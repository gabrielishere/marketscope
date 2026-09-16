import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { PeerImpact } from '../../api/models/peer-impact';
import { formatSignedPercent } from '../../core/format';

/**
 * Same-sector peers, ranked by impact.
 *
 * The list arrives as a **field on the impact response**, already ranked. It is not
 * fetched here: one `/impact/{symbol}` call per peer would turn a panel into a burst of
 * requests every time the selection changed.
 */
@Component({
  selector: 'app-peer-comparison',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="peers">
      <h4>Others in the sector</h4>
      @for (peer of peers; track peer.symbol) {
        <div class="peer">
          <span class="sym">{{ peer.symbol }}</span>
          <span class="name">{{ peer.name }}</span>
          <span class="num" [class.up]="peer.move_pct >= 0" [class.down]="peer.move_pct < 0">
            {{ pct(peer.move_pct) }}
          </span>
        </div>
      } @empty {
        <div class="peer"><span class="name">No peers in this sector.</span></div>
      }
    </div>
  `,
  styles: [
    `
      .peers { padding: 0 var(--sp-4) var(--sp-4); }
      h4 {
        font-size: var(--ts-1);
        color: var(--n-5);
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: var(--sp-3) 0 var(--sp-2);
      }
      .peer {
        display: flex;
        align-items: center;
        gap: var(--sp-3);
        height: var(--h-row);
      }
      .sym { width: 56px; font-weight: 600; font-size: var(--ts-2); }
      .name {
        color: var(--n-6);
        font-size: var(--ts-2);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .num {
        margin-left: auto;
        width: var(--w-change);
        text-align: right;
        font-family: var(--font-num);
        font-variant-numeric: tabular-nums;
        font-size: var(--ts-2);
      }
      .up { color: var(--sig-up); }
      .down { color: var(--sig-down); }
    `,
  ],
})
export class PeerComparisonComponent {
  @Input({ required: true }) peers: PeerImpact[] = [];
  readonly pct = formatSignedPercent;
}
