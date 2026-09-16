/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { BaseService } from '../base-service';
import { ApiConfiguration } from '../api-configuration';
import { StrictHttpResponse } from '../strict-http-response';

import { getMovers } from '../fn/movers/get-movers';
import { GetMovers$Params } from '../fn/movers/get-movers';
import { listMacroDrivers } from '../fn/movers/list-macro-drivers';
import { ListMacroDrivers$Params } from '../fn/movers/list-macro-drivers';
import { MacroDriver } from '../models/macro-driver';
import { MoversResponse } from '../models/movers-response';

@Injectable({ providedIn: 'root' })
export class MoversService extends BaseService {
  constructor(config: ApiConfiguration, http: HttpClient) {
    super(config, http);
  }

  /** Path part for operation `getMovers()` */
  static readonly GetMoversPath = '/movers';

  /**
   * Get Movers.
   *
   * Gainers, losers and most active, each already in the order it renders in.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `getMovers()` instead.
   *
   * This method doesn't expect any request body.
   */
  getMovers$Response(params?: GetMovers$Params, context?: HttpContext): Observable<StrictHttpResponse<MoversResponse>> {
    return getMovers(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Movers.
   *
   * Gainers, losers and most active, each already in the order it renders in.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `getMovers$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  getMovers(params?: GetMovers$Params, context?: HttpContext): Observable<MoversResponse> {
    return this.getMovers$Response(params, context).pipe(
      map((r: StrictHttpResponse<MoversResponse>): MoversResponse => r.body)
    );
  }

  /** Path part for operation `listMacroDrivers()` */
  static readonly ListMacroDriversPath = '/macro';

  /**
   * Get Macro.
   *
   * The five macro drivers, one per factor, in factor order.
   *
   * Ordered by iterating `FACTORS` rather than by filtering the universe, so the result
   * follows the factor order whatever order the data file happens to list them in.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `listMacroDrivers()` instead.
   *
   * This method doesn't expect any request body.
   */
  listMacroDrivers$Response(params?: ListMacroDrivers$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<MacroDriver>>> {
    return listMacroDrivers(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Macro.
   *
   * The five macro drivers, one per factor, in factor order.
   *
   * Ordered by iterating `FACTORS` rather than by filtering the universe, so the result
   * follows the factor order whatever order the data file happens to list them in.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `listMacroDrivers$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  listMacroDrivers(params?: ListMacroDrivers$Params, context?: HttpContext): Observable<Array<MacroDriver>> {
    return this.listMacroDrivers$Response(params, context).pipe(
      map((r: StrictHttpResponse<Array<MacroDriver>>): Array<MacroDriver> => r.body)
    );
  }

}
