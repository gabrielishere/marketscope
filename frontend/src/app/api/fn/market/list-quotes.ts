/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { Quote } from '../../models/quote';

export interface ListQuotes$Params {

/**
 * Comma-separated symbols, in the order wanted.
 */
  symbols: string;
}

export function listQuotes(http: HttpClient, rootUrl: string, params: ListQuotes$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<Quote>>> {
  const rb = new RequestBuilder(rootUrl, listQuotes.PATH, 'get');
  if (params) {
    rb.query('symbols', params.symbols, {});
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<Array<Quote>>;
    })
  );
}

listQuotes.PATH = '/quotes';
