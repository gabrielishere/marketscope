import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AsyncPipe } from '@angular/common';

import { ScenarioService } from '../core/scenario.service';
import { HeadlineTickerComponent } from '../features/ticker/headline-ticker.component';

/**
 * The application shell: the toolbar, the two tabs, the active-scenario chip and the
 * headlines strip — all **outside** the `router-outlet`.
 *
 * That placement is structural, not stylistic. `Simulated feed` is required on every
 * view, and the chip and tabs must persist across both routes. Putting them here makes
 * it impossible for a route to render without them; putting them in each route would
 * make it a thing every route has to remember.
 */
@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, AsyncPipe, HeadlineTickerComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <header class="toolbar">
      <span class="brand">Marketscope</span>
      <nav class="tabs">
        <a class="tab" routerLink="/" routerLinkActive="active"
           [routerLinkActiveOptions]="{ exact: true }">Dashboard</a>
        <a class="tab" routerLink="/markets" routerLinkActive="active">Markets</a>
      </nav>
      <div class="toolbar-right">
        @if (active$ | async; as active) {
          <span class="chip" [class.baseline]="active.activated_at === null">
            {{ active.name }}
          </span>
        }
        <span class="sim">Simulated feed</span>
      </div>
    </header>

    <app-headline-ticker />

    <router-outlet />
  `,
  styles: [
    `
      .toolbar {
        display: flex;
        align-items: center;
        gap: var(--sp-5);
        height: 52px;
        padding: 0 var(--sp-5);
        background: var(--n-1);
        border-bottom: 1px solid var(--n-3);
        position: sticky;
        top: 0;
        z-index: 10;
      }
      .brand { font-size: var(--ts-4); font-weight: 600; letter-spacing: -0.01em; }
      .tabs { display: flex; gap: var(--sp-1); }
      .tab {
        padding: var(--sp-2) var(--sp-3);
        border-radius: var(--r-1);
        color: var(--n-6);
        font-size: var(--ts-3);
        font-weight: 500;
        text-decoration: none;
      }
      .tab.active { background: var(--n-2); color: var(--n-7); }
      .toolbar-right {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: var(--sp-3);
      }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-1) var(--sp-3);
        background: var(--sig-down-bg);
        color: var(--n-7);
        border: 1px solid var(--n-4);
        border-radius: var(--r-3);
        font-size: var(--ts-2);
        font-weight: 500;
      }
      .chip::before {
        content: '';
        width: var(--sp-2);
        height: var(--sp-2);
        border-radius: 50%;
        background: var(--sig-down);
      }
      /* At baseline the chip is quiet: nothing is happening, so nothing signals. */
      .chip.baseline { background: var(--n-2); }
      .chip.baseline::before { background: var(--n-5); }
      .sim { font-size: var(--ts-2); color: var(--n-5); }
    `,
  ],
})
export class ShellComponent {
  private readonly scenarios = inject(ScenarioService);

  /** The active scenario, for the chip. Shared with the selector and the ticker. */
  readonly active$ = this.scenarios.active$;
}
