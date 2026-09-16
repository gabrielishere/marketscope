import { Routes } from '@angular/router';

/**
 * Two routes. The toolbar, its `Simulated feed` label and the scenario chip live in the
 * shell *outside* the outlet, so neither route can render without them.
 */
export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./dashboard/dashboard.component').then((m) => m.DashboardComponent),
  },
  {
    path: 'markets',
    loadComponent: () =>
      import('./features/markets/markets.component').then((m) => m.MarketsComponent),
  },
  { path: '**', redirectTo: '' },
];
