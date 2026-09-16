/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { BaseService } from '../base-service';
import { ApiConfiguration } from '../api-configuration';
import { StrictHttpResponse } from '../strict-http-response';

import { getPortfolioImpact } from '../fn/impact/get-portfolio-impact';
import { GetPortfolioImpact$Params } from '../fn/impact/get-portfolio-impact';
import { getSymbolImpact } from '../fn/impact/get-symbol-impact';
import { GetSymbolImpact$Params } from '../fn/impact/get-symbol-impact';
import { PortfolioImpact } from '../models/portfolio-impact';
import { SymbolImpact } from '../models/symbol-impact';

@Injectable({ providedIn: 'root' })
export class ImpactService extends BaseService {
  constructor(config: ApiConfiguration, http: HttpClient) {
    super(config, http);
  }

  /** Path part for operation `getPortfolioImpact()` */
  static readonly GetPortfolioImpactPath = '/impact/portfolio';

  /**
   * Get Portfolio Impact.
   *
   * The same decomposition, one entry per holding, plus the book's total.
   *
   * **Declared before the symbol route.** See the module docstring.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `getPortfolioImpact()` instead.
   *
   * This method doesn't expect any request body.
   */
  getPortfolioImpact$Response(params?: GetPortfolioImpact$Params, context?: HttpContext): Observable<StrictHttpResponse<PortfolioImpact>> {
    return getPortfolioImpact(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Portfolio Impact.
   *
   * The same decomposition, one entry per holding, plus the book's total.
   *
   * **Declared before the symbol route.** See the module docstring.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `getPortfolioImpact$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  getPortfolioImpact(params?: GetPortfolioImpact$Params, context?: HttpContext): Observable<PortfolioImpact> {
    return this.getPortfolioImpact$Response(params, context).pipe(
      map((r: StrictHttpResponse<PortfolioImpact>): PortfolioImpact => r.body)
    );
  }

  /** Path part for operation `getSymbolImpact()` */
  static readonly GetSymbolImpactPath = '/impact/{symbol}';

  /**
   * Get Symbol Impact.
   *
   * The move since the window opened, what drove it, and same-sector peers.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `getSymbolImpact()` instead.
   *
   * This method doesn't expect any request body.
   */
  getSymbolImpact$Response(params: GetSymbolImpact$Params, context?: HttpContext): Observable<StrictHttpResponse<SymbolImpact>> {
    return getSymbolImpact(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Symbol Impact.
   *
   * The move since the window opened, what drove it, and same-sector peers.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `getSymbolImpact$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  getSymbolImpact(params: GetSymbolImpact$Params, context?: HttpContext): Observable<SymbolImpact> {
    return this.getSymbolImpact$Response(params, context).pipe(
      map((r: StrictHttpResponse<SymbolImpact>): SymbolImpact => r.body)
    );
  }

}
