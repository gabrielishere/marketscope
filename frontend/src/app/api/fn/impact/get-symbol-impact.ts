/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { SymbolImpact } from '../../models/symbol-impact';

export interface GetSymbolImpact$Params {
  symbol: string;
}

export function getSymbolImpact(http: HttpClient, rootUrl: string, params: GetSymbolImpact$Params, context?: HttpContext): Observable<StrictHttpResponse<SymbolImpact>> {
  const rb = new RequestBuilder(rootUrl, getSymbolImpact.PATH, 'get');
  if (params) {
    rb.path('symbol', params.symbol, {});
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<SymbolImpact>;
    })
  );
}

getSymbolImpact.PATH = '/impact/{symbol}';
