import { ChangeDetectionStrategy, Component, Input, computed, signal } from '@angular/core';

/**
 * A row sparkline: recent closes drawn on their own scale.
 *
 * **The box never resizes.** The viewBox is fixed and the series is normalised into it,
 * so a redraw every poll changes the path and nothing else. A sparkline that rescaled its
 * own element would move the column beside it twice a second.
 */
@Component({
  selector: 'app-sparkline',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <svg class="spark" viewBox="0 0 56 18" fill="none" preserveAspectRatio="none">
      <path [attr.d]="path()" [attr.stroke]="stroke()" stroke-width="1.5" />
    </svg>
  `,
  styles: [
    `
      .spark { width: 56px; height: 18px; display: block; }
    `,
  ],
})
export class SparklineComponent {
  private readonly series = signal<number[]>([]);

  @Input({ required: true }) set points(value: number[]) {
    this.series.set(value ?? []);
  }

  /** Green when the window closed above where it opened, red below, neutral flat. */
  readonly stroke = computed(() => {
    const points = this.series();
    if (points.length < 2) return 'var(--n-5)';
    const delta = points[points.length - 1] - points[0];
    if (delta > 0) return 'var(--sig-up)';
    if (delta < 0) return 'var(--sig-down)';
    return 'var(--n-5)';
  });

  readonly path = computed(() => {
    const points = this.series();
    if (points.length < 2) return '';
    const low = Math.min(...points);
    const high = Math.max(...points);
    const span = high - low || 1;
    const step = 56 / (points.length - 1);
    return points
      .map((value, index) => {
        const x = (index * step).toFixed(2);
        // 1..17 rather than 0..18, so the stroke is not clipped at the extremes.
        const y = (17 - ((value - low) / span) * 16).toFixed(2);
        return `${index === 0 ? 'M' : 'L'}${x} ${y}`;
      })
      .join(' ');
  });
}
