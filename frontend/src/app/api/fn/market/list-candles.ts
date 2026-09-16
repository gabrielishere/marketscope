/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { Candle } from '../../models/candle';
import { Timeframe } from '../../models/timeframe';

export interface ListCandles$Params {
  symbol: string;

/**
 * Chart timeframe.
 */
  tf?: Timeframe;
}

export function listCandles(http: HttpClient, rootUrl: string, params: ListCandles$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<Candle>>> {
  const rb = new RequestBuilder(rootUrl, listCandles.PATH, 'get');
  if (params) {
    rb.path('symbol', params.symbol, {});
    rb.query('tf', params.tf, {});
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<Array<Candle>>;
    })
  );
}

listCandles.PATH = '/candles/{symbol}';
