import { ChangeDetectionStrategy, Component } from '@angular/core';

import { PortfolioSummaryComponent } from '../features/portfolio/portfolio-summary.component';
import { MacroStripComponent } from '../features/macro/macro-strip.component';
import { WatchlistComponent } from '../features/watchlist/watchlist.component';
import { MoversComponent } from '../features/movers/movers.component';
import { ScenarioSelectorComponent } from '../features/scenario/scenario-selector.component';
import { DetailComponent } from '../features/detail/detail.component';
import { ImpactPanelComponent } from '../features/impact/impact-panel.component';

/**
 * The dashboard composition. **Written once and not edited again** — each feature fills
 * its own file and nothing touches this one, so eight tasks do not queue behind a single
 * shared shell.
 *
 * The portfolio summary is first: it is the figure an audience reads before anything else.
 */
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    PortfolioSummaryComponent,
    MacroStripComponent,
    WatchlistComponent,
    MoversComponent,
    ScenarioSelectorComponent,
    DetailComponent,
    ImpactPanelComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <main class="view">
      <app-portfolio-summary />
      <app-macro-strip />
      <div class="cols">
        <div class="stack">
          <app-watchlist />
        </div>
        <div class="stack">
          <app-detail />
          <app-impact-panel />
        </div>
        <div class="stack">
          <app-scenario-selector />
          <app-movers />
        </div>
      </div>
    </main>
  `,
  styles: [
    `
      .view { padding: var(--sp-5); display: grid; gap: var(--sp-4); }
      .cols {
        display: grid;
        gap: var(--sp-4);
        grid-template-columns: 300px minmax(0, 1fr) 300px;
      }
      @media (max-width: 1100px) { .cols { grid-template-columns: 1fr; } }
      .stack { display: grid; gap: var(--sp-4); align-content: start; }
    `,
  ],
})
export class DashboardComponent {}
