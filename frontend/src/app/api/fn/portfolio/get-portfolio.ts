/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { PortfolioResponse } from '../../models/portfolio-response';

export interface GetPortfolio$Params {
}

export function getPortfolio(http: HttpClient, rootUrl: string, params?: GetPortfolio$Params, context?: HttpContext): Observable<StrictHttpResponse<PortfolioResponse>> {
  const rb = new RequestBuilder(rootUrl, getPortfolio.PATH, 'get');
  if (params) {
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<PortfolioResponse>;
    })
  );
}

getPortfolio.PATH = '/portfolio';
