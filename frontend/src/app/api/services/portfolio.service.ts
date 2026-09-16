/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { BaseService } from '../base-service';
import { ApiConfiguration } from '../api-configuration';
import { StrictHttpResponse } from '../strict-http-response';

import { getPortfolio } from '../fn/portfolio/get-portfolio';
import { GetPortfolio$Params } from '../fn/portfolio/get-portfolio';
import { PortfolioResponse } from '../models/portfolio-response';

@Injectable({ providedIn: 'root' })
export class PortfolioService extends BaseService {
  constructor(config: ApiConfiguration, http: HttpClient) {
    super(config, http);
  }

  /** Path part for operation `getPortfolio()` */
  static readonly GetPortfolioPath = '/portfolio';

  /**
   * Get Portfolio.
   *
   * Every held position with its symbol, quantity and average entry, plus the totals.
   *
   * `unrealised_pnl` is computed here rather than stored, so it cannot go stale between
   * ticks: it is a function of the latest close, which moves every second.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `getPortfolio()` instead.
   *
   * This method doesn't expect any request body.
   */
  getPortfolio$Response(params?: GetPortfolio$Params, context?: HttpContext): Observable<StrictHttpResponse<PortfolioResponse>> {
    return getPortfolio(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Portfolio.
   *
   * Every held position with its symbol, quantity and average entry, plus the totals.
   *
   * `unrealised_pnl` is computed here rather than stored, so it cannot go stale between
   * ticks: it is a function of the latest close, which moves every second.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `getPortfolio$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  getPortfolio(params?: GetPortfolio$Params, context?: HttpContext): Observable<PortfolioResponse> {
    return this.getPortfolio$Response(params, context).pipe(
      map((r: StrictHttpResponse<PortfolioResponse>): PortfolioResponse => r.body)
    );
  }

}
