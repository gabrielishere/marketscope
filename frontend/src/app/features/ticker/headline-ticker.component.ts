import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';

import { ScenarioService } from '../../core/scenario.service';

/**
 * The headlines strip: how the demo explains itself.
 *
 * Prices moving is evidence; a headline saying *why* is the explanation, and it is the
 * part a non-technical audience actually reads. The baseline carries headlines like any
 * other scenario, so the strip is never empty and needs no special case.
 *
 * The headlines come from `GET /scenario` through the shared service, never from a copy
 * held here — a stale copy would caption the wrong event.
 */
@Component({
  selector: 'app-headline-ticker',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="ticker">
      @if (active$ | async; as active) {
        @for (headline of active.headlines; track headline; let first = $first) {
          @if (!first) { <span class="sep">•</span> }
          <span [class.lead]="first">{{ headline }}</span>
        }
      } @else {
        <span class="sep">Loading headlines…</span>
      }
    </div>
  `,
  styles: [
    `
      .ticker {
        display: flex;
        align-items: center;
        gap: var(--sp-4);
        height: 32px;
        padding: 0 var(--sp-5);
        overflow: hidden;
        white-space: nowrap;
        background: var(--n-0);
        border-bottom: 1px solid var(--n-3);
        font-size: var(--ts-2);
        color: var(--n-6);
      }
      /* Context, not a signal — so it carries none of the direction colours. */
      .lead { color: var(--n-7); font-weight: 600; }
      .sep { color: var(--n-4); }
    `,
  ],
})
export class HeadlineTickerComponent {
  readonly active$ = inject(ScenarioService).active$;
}
