import { Injectable, inject } from '@angular/core';
import { Observable, Subject, merge, map, shareReplay, switchMap, timer } from 'rxjs';

import { MarketService } from '../api/services/market.service';
import { Quote } from '../api/models/quote';
import { SymbolMatch } from '../api/models/symbol-match';

/**
 * The single quote poll. **Every price on every surface comes through here.**
 *
 * **It polls the universe, not each subscriber's list.** The dashboard wants a handful
 * of symbols and the markets table wants all forty-five. A service that polled per
 * subscriber set would satisfy "one request per subscriber" and still issue two, so the
 * count would depend on which components happened to be mounted. Polling the whole
 * universe once and letting subscribers select from the result makes the request count a
 * property of this service alone.
 *
 * **One timer, multicast.** `shareReplay` is what makes the count independent of how many
 * components subscribe — a cold observable handed to six components issues six requests.
 * There is exactly one timer in the whole application: `tick$`, exported from here, is
 * what every other polled surface derives from. `quotes$` never calls the API.
 *
 * **`refreshNow()` exists for the demo.** A scenario selection has to show immediately;
 * waiting out the interval after a click reads as a broken application.
 */
@Injectable({ providedIn: 'root' })
export class QuoteService {
  private readonly market = inject(MarketService);

  /** The poll interval. Within the 2–3s the spec allows. */
  private static readonly POLL_INTERVAL_MS = 2500;

  /** Fires an off-schedule poll. Merged into the same stream as the timer. */
  private readonly refresh$ = new Subject<void>();

  /**
   * **The application's only clock.** Every polled surface derives from this — quotes,
   * movers, the detail series and the impact panel — so the whole app moves on one
   * cadence and a forced refresh reaches all of them together.
   *
   * `timer` rather than `interval` so the first emission is immediate: an application
   * that shows skeletons for the first two and a half seconds looks slow when it is not.
   */
  readonly tick$: Observable<unknown> = merge(
    timer(0, QuoteService.POLL_INTERVAL_MS),
    this.refresh$,
  ).pipe(shareReplay({ bufferSize: 1, refCount: false }));

  /**
   * The universe's symbols, fetched once. `listSymbols` with no query returns the whole
   * universe with its static metadata — the call the markets table also loads from, so
   * the metadata arrives once rather than on every poll.
   */
  private readonly symbols$: Observable<string[]> = this.market.listSymbols().pipe(
    map((entries: SymbolMatch[]) => entries.map((entry) => entry.symbol)),
    shareReplay({ bufferSize: 1, refCount: false }),
  );

  /** The universe's static metadata, fetched once and shared. */
  readonly universe$: Observable<SymbolMatch[]> = this.market
    .listSymbols()
    .pipe(shareReplay({ bufferSize: 1, refCount: false }));

  /**
   * The one polled stream: every symbol, once per interval, shared by every subscriber.
   *
   * `timer` rather than `interval` so the first quotes arrive immediately instead of one
   * interval after load — an application that shows skeletons for the first two and a
   * half seconds looks slow when it is not.
   */
  private readonly all$: Observable<Quote[]> = this.symbols$.pipe(
    switchMap((symbols) =>
      this.tick$.pipe(
        switchMap(() => this.market.listQuotes({ symbols: symbols.join(',') })),
      ),
    ),
    shareReplay({ bufferSize: 1, refCount: false }),
  );

  /** The single polled stream, every symbol. */
  allQuotes$(): Observable<Quote[]> {
    return this.all$;
  }

  /**
   * A selection over the one stream. **Never a request of its own** — this filters what
   * the poll already fetched, which is why mounting another component cannot add a call.
   */
  quotes$(symbols: string[]): Observable<Quote[]> {
    const wanted = new Set(symbols);
    return this.all$.pipe(map((quotes) => quotes.filter((q) => wanted.has(q.symbol))));
  }

  /** Poll now rather than at the next tick of the timer. */
  refreshNow(): void {
    this.refresh$.next();
  }
}
