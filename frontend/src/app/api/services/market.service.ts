/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { BaseService } from '../base-service';
import { ApiConfiguration } from '../api-configuration';
import { StrictHttpResponse } from '../strict-http-response';

import { Candle } from '../models/candle';
import { listCandles } from '../fn/market/list-candles';
import { ListCandles$Params } from '../fn/market/list-candles';
import { listQuotes } from '../fn/market/list-quotes';
import { ListQuotes$Params } from '../fn/market/list-quotes';
import { listSymbols } from '../fn/market/list-symbols';
import { ListSymbols$Params } from '../fn/market/list-symbols';
import { Quote } from '../models/quote';
import { SymbolMatch } from '../models/symbol-match';

@Injectable({ providedIn: 'root' })
export class MarketService extends BaseService {
  constructor(config: ApiConfiguration, http: HttpClient) {
    super(config, http);
  }

  /** Path part for operation `listSymbols()` */
  static readonly ListSymbolsPath = '/symbols';

  /**
   * Get Symbols.
   *
   * Instruments matching `q` on symbol or name, or the whole universe when it is empty.
   *
   * The match is a case-insensitive substring over both fields, so `oc` finds Occidental
   * by name and `XO` finds XOM by symbol, while a string in neither is absent from the
   * result rather than ranked low.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `listSymbols()` instead.
   *
   * This method doesn't expect any request body.
   */
  listSymbols$Response(params?: ListSymbols$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<SymbolMatch>>> {
    return listSymbols(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Symbols.
   *
   * Instruments matching `q` on symbol or name, or the whole universe when it is empty.
   *
   * The match is a case-insensitive substring over both fields, so `oc` finds Occidental
   * by name and `XO` finds XOM by symbol, while a string in neither is absent from the
   * result rather than ranked low.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `listSymbols$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  listSymbols(params?: ListSymbols$Params, context?: HttpContext): Observable<Array<SymbolMatch>> {
    return this.listSymbols$Response(params, context).pipe(
      map((r: StrictHttpResponse<Array<SymbolMatch>>): Array<SymbolMatch> => r.body)
    );
  }

  /** Path part for operation `listQuotes()` */
  static readonly ListQuotesPath = '/quotes';

  /**
   * Get Quotes.
   *
   * One quote per requested symbol, **in request order**.
   *
   * The client selects from this list positionally, so the order is the contract. An
   * unknown symbol is a 404 naming it rather than a silently shorter list, which would
   * misalign every subsequent entry.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `listQuotes()` instead.
   *
   * This method doesn't expect any request body.
   */
  listQuotes$Response(params: ListQuotes$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<Quote>>> {
    return listQuotes(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Quotes.
   *
   * One quote per requested symbol, **in request order**.
   *
   * The client selects from this list positionally, so the order is the contract. An
   * unknown symbol is a 404 naming it rather than a silently shorter list, which would
   * misalign every subsequent entry.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `listQuotes$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  listQuotes(params: ListQuotes$Params, context?: HttpContext): Observable<Array<Quote>> {
    return this.listQuotes$Response(params, context).pipe(
      map((r: StrictHttpResponse<Array<Quote>>): Array<Quote> => r.body)
    );
  }

  /** Path part for operation `listCandles()` */
  static readonly ListCandlesPath = '/candles/{symbol}';

  /**
   * Get Candles.
   *
   * The instrument's history aggregated into bars of the requested timeframe.
   *
   * Bars are grouped by tick index rather than by position, so a group is the same set
   * of ticks whatever the buffer happens to hold — and the open, high, low, close and
   * volume of a group are the first open, the highest high, the lowest low, the last
   * close and the summed volume of its constituents.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `listCandles()` instead.
   *
   * This method doesn't expect any request body.
   */
  listCandles$Response(params: ListCandles$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<Candle>>> {
    return listCandles(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Candles.
   *
   * The instrument's history aggregated into bars of the requested timeframe.
   *
   * Bars are grouped by tick index rather than by position, so a group is the same set
   * of ticks whatever the buffer happens to hold — and the open, high, low, close and
   * volume of a group are the first open, the highest high, the lowest low, the last
   * close and the summed volume of its constituents.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `listCandles$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  listCandles(params: ListCandles$Params, context?: HttpContext): Observable<Array<Candle>> {
    return this.listCandles$Response(params, context).pipe(
      map((r: StrictHttpResponse<Array<Candle>>): Array<Candle> => r.body)
    );
  }

}
