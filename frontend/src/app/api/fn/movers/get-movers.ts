/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { MoversResponse } from '../../models/movers-response';

export interface GetMovers$Params {
}

export function getMovers(http: HttpClient, rootUrl: string, params?: GetMovers$Params, context?: HttpContext): Observable<StrictHttpResponse<MoversResponse>> {
  const rb = new RequestBuilder(rootUrl, getMovers.PATH, 'get');
  if (params) {
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<MoversResponse>;
    })
  );
}

getMovers.PATH = '/movers';
