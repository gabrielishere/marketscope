/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { SymbolMatch } from '../../models/symbol-match';

export interface ListSymbols$Params {

/**
 * Partial symbol or name; empty returns all.
 */
  q?: string;
}

export function listSymbols(http: HttpClient, rootUrl: string, params?: ListSymbols$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<SymbolMatch>>> {
  const rb = new RequestBuilder(rootUrl, listSymbols.PATH, 'get');
  if (params) {
    rb.query('q', params.q, {});
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<Array<SymbolMatch>>;
    })
  );
}

listSymbols.PATH = '/symbols';
