import { ChangeDetectionStrategy, Component, Input, computed, signal } from '@angular/core';

import { Candle } from '../../api/models/candle';

/**
 * The price series, and the labelled marker at the scenario's activation tick.
 *
 * **The marker is the demo's visual payoff.** It is where an audience sees the world
 * event land and the line change direction. It is driven by `activatedAt` being non-null
 * — the server's activation tick — and not by a scenario being *selected* in a dropdown.
 * Those are different states, and only the first has a tick to draw at.
 *
 * Drawn as inline SVG. No charting library: no UI or styling package is permitted, and a
 * line with a rule on it does not need one.
 */
@Component({
  selector: 'app-chart',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <svg class="chart" viewBox="0 0 600 190" preserveAspectRatio="none">
      <line x1="0" y1="150" x2="600" y2="150" stroke="var(--n-3)" />
      <line x1="0" y1="100" x2="600" y2="100" stroke="var(--n-3)" />
      <line x1="0" y1="50" x2="600" y2="50" stroke="var(--n-3)" />
      <path [attr.d]="path()" fill="none" [attr.stroke]="stroke()" stroke-width="2" />
      @if (markerX() !== null) {
        <line [attr.x1]="markerX()" y1="8" [attr.x2]="markerX()" y2="182"
              stroke="var(--n-6)" stroke-width="1" stroke-dasharray="3 3" />
        <text [attr.x]="labelX()" y="20" fill="var(--n-6)" class="marker-label">
          {{ markerLabel }}
        </text>
      }
    </svg>
  `,
  styles: [
    `
      .chart { display: block; width: 100%; height: 190px; }
      .marker-label { font-size: var(--ts-1); font-family: var(--font); }
    `,
  ],
})
export class ChartComponent {
  private readonly series = signal<Candle[]>([]);
  private readonly activated = signal<number | null>(null);

  @Input({ required: true }) set candles(value: Candle[]) {
    this.series.set(value ?? []);
  }

  /** The server's activation tick. Null at baseline, and then no marker is drawn. */
  @Input() set activatedAt(value: number | null | undefined) {
    this.activated.set(value ?? null);
  }

  @Input() markerLabel = 'Scenario activated';

  readonly stroke = computed(() => {
    const candles = this.series();
    if (candles.length < 2) return 'var(--n-5)';
    const delta = candles[candles.length - 1].close - candles[0].open;
    return delta >= 0 ? 'var(--sig-up)' : 'var(--sig-down)';
  });

  readonly path = computed(() => {
    const candles = this.series();
    if (candles.length < 2) return '';
    const closes = candles.map((c) => c.close);
    const low = Math.min(...closes);
    const high = Math.max(...closes);
    const span = high - low || 1;
    const step = 600 / (candles.length - 1);
    return candles
      .map((candle, index) => {
        const x = (index * step).toFixed(2);
        const y = (180 - ((candle.close - low) / span) * 168).toFixed(2);
        return `${index === 0 ? 'M' : 'L'}${x} ${y}`;
      })
      .join(' ');
  });

  /** Where the activation tick falls along the drawn window, or null if outside it. */
  readonly markerX = computed(() => {
    const at = this.activated();
    const candles = this.series();
    if (at === null || candles.length < 2) return null;
    const first = candles[0].t;
    const last = candles[candles.length - 1].t;
    if (at < first || at > last) return null;
    return (((at - first) / (last - first)) * 600).toFixed(2);
  });

  readonly labelX = computed(() => {
    const x = this.markerX();
    return x === null ? null : Math.min(Number(x) + 8, 500).toFixed(2);
  });
}
