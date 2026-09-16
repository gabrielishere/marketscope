import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, shareReplay, switchMap, tap } from 'rxjs';

import { ScenarioService as ScenarioApi } from '../api/services/scenario.service';
import { ActiveScenario } from '../api/models/active-scenario';
import { ScenarioSummary } from '../api/models/scenario-summary';
import { ScenarioId } from '../api/models/scenario-id';
import { QuoteService } from './quote.service';

/**
 * The active scenario, shared by the toolbar chip, the selector and the headlines strip.
 *
 * **Nothing here holds a copy of a headline.** They come from `GET /scenario` on every
 * read, so a scenario edited in the backend's JSON reaches the ticker without a frontend
 * change — and a stale copy, which would caption the wrong event, is impossible.
 *
 * **Activation forces a quote refresh, in the POST's success path.** Refreshing beside
 * the POST rather than after it fetches quotes the server has not yet changed: the
 * audience clicks, nothing happens, and the market moves two seconds later. That reads as
 * a broken demo, and it is the reason `refreshNow()` is called in `tap` on the response
 * rather than alongside the call.
 */
@Injectable({ providedIn: 'root' })
export class ScenarioService {
  private readonly api = inject(ScenarioApi);
  private readonly quotes = inject(QuoteService);

  private readonly reload$ = new BehaviorSubject<void>(undefined);

  /** The library, for the dropdown. Fetched once. */
  readonly library$: Observable<ScenarioSummary[]> = this.api
    .listScenarios()
    .pipe(shareReplay({ bufferSize: 1, refCount: false }));

  /** The active scenario, its headlines and its activation tick. */
  readonly active$: Observable<ActiveScenario> = this.reload$.pipe(
    switchMap(() => this.api.getActiveScenario()),
    shareReplay({ bufferSize: 1, refCount: false }),
  );

  /** Activate a scenario, then refresh quotes — in that order. */
  activate(id: ScenarioId): Observable<ActiveScenario> {
    return this.api.activateScenario({ body: { id } }).pipe(
      tap(() => {
        this.reload$.next();
        this.quotes.refreshNow();
      }),
    );
  }

  /** Return to baseline, then refresh quotes — in that order. */
  reset(): Observable<ActiveScenario> {
    return this.api.deactivateScenario().pipe(
      tap(() => {
        this.reload$.next();
        this.quotes.refreshNow();
      }),
    );
  }
}
