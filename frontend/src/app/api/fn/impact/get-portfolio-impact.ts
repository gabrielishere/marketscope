/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { PortfolioImpact } from '../../models/portfolio-impact';

export interface GetPortfolioImpact$Params {
}

export function getPortfolioImpact(http: HttpClient, rootUrl: string, params?: GetPortfolioImpact$Params, context?: HttpContext): Observable<StrictHttpResponse<PortfolioImpact>> {
  const rb = new RequestBuilder(rootUrl, getPortfolioImpact.PATH, 'get');
  if (params) {
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<PortfolioImpact>;
    })
  );
}

getPortfolioImpact.PATH = '/impact/portfolio';
