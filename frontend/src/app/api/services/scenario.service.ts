/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { BaseService } from '../base-service';
import { ApiConfiguration } from '../api-configuration';
import { StrictHttpResponse } from '../strict-http-response';

import { activateScenario } from '../fn/scenario/activate-scenario';
import { ActivateScenario$Params } from '../fn/scenario/activate-scenario';
import { ActiveScenario } from '../models/active-scenario';
import { deactivateScenario } from '../fn/scenario/deactivate-scenario';
import { DeactivateScenario$Params } from '../fn/scenario/deactivate-scenario';
import { getActiveScenario } from '../fn/scenario/get-active-scenario';
import { GetActiveScenario$Params } from '../fn/scenario/get-active-scenario';
import { listScenarios } from '../fn/scenario/list-scenarios';
import { ListScenarios$Params } from '../fn/scenario/list-scenarios';
import { ScenarioSummary } from '../models/scenario-summary';

@Injectable({ providedIn: 'root' })
export class ScenarioService extends BaseService {
  constructor(config: ApiConfiguration, http: HttpClient) {
    super(config, http);
  }

  /** Path part for operation `listScenarios()` */
  static readonly ListScenariosPath = '/scenarios';

  /**
   * Get Scenarios.
   *
   * The library, in file order, which places the baseline first.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `listScenarios()` instead.
   *
   * This method doesn't expect any request body.
   */
  listScenarios$Response(params?: ListScenarios$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<ScenarioSummary>>> {
    return listScenarios(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Scenarios.
   *
   * The library, in file order, which places the baseline first.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `listScenarios$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  listScenarios(params?: ListScenarios$Params, context?: HttpContext): Observable<Array<ScenarioSummary>> {
    return this.listScenarios$Response(params, context).pipe(
      map((r: StrictHttpResponse<Array<ScenarioSummary>>): Array<ScenarioSummary> => r.body)
    );
  }

  /** Path part for operation `getActiveScenario()` */
  static readonly GetActiveScenarioPath = '/scenario';

  /**
   * Get Scenario.
   *
   * The active scenario, its headlines, and the tick it was activated at.
   *
   * `activated_at` is null at baseline. The headlines are served from here rather than
   * held in the client, so a scenario change reaches the ticker without a redeploy.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `getActiveScenario()` instead.
   *
   * This method doesn't expect any request body.
   */
  getActiveScenario$Response(params?: GetActiveScenario$Params, context?: HttpContext): Observable<StrictHttpResponse<ActiveScenario>> {
    return getActiveScenario(this.http, this.rootUrl, params, context);
  }

  /**
   * Get Scenario.
   *
   * The active scenario, its headlines, and the tick it was activated at.
   *
   * `activated_at` is null at baseline. The headlines are served from here rather than
   * held in the client, so a scenario change reaches the ticker without a redeploy.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `getActiveScenario$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  getActiveScenario(params?: GetActiveScenario$Params, context?: HttpContext): Observable<ActiveScenario> {
    return this.getActiveScenario$Response(params, context).pipe(
      map((r: StrictHttpResponse<ActiveScenario>): ActiveScenario => r.body)
    );
  }

  /** Path part for operation `activateScenario()` */
  static readonly ActivateScenarioPath = '/scenario';

  /**
   * Post Scenario.
   *
   * Make a scenario active from the next tick, stamping `activated_at`.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `activateScenario()` instead.
   *
   * This method sends `application/json` and handles request body of type `application/json`.
   */
  activateScenario$Response(params: ActivateScenario$Params, context?: HttpContext): Observable<StrictHttpResponse<ActiveScenario>> {
    return activateScenario(this.http, this.rootUrl, params, context);
  }

  /**
   * Post Scenario.
   *
   * Make a scenario active from the next tick, stamping `activated_at`.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `activateScenario$Response()` instead.
   *
   * This method sends `application/json` and handles request body of type `application/json`.
   */
  activateScenario(params: ActivateScenario$Params, context?: HttpContext): Observable<ActiveScenario> {
    return this.activateScenario$Response(params, context).pipe(
      map((r: StrictHttpResponse<ActiveScenario>): ActiveScenario => r.body)
    );
  }

  /** Path part for operation `deactivateScenario()` */
  static readonly DeactivateScenarioPath = '/scenario';

  /**
   * Delete Scenario.
   *
   * Return to baseline, clearing `activated_at`.
   *
   * The bars written while the scenario was active stay exactly as they are — going back
   * to normal is a change to what happens next, not an undo.
   *
   * This method provides access to the full `HttpResponse`, allowing access to response headers.
   * To access only the response body, use `deactivateScenario()` instead.
   *
   * This method doesn't expect any request body.
   */
  deactivateScenario$Response(params?: DeactivateScenario$Params, context?: HttpContext): Observable<StrictHttpResponse<ActiveScenario>> {
    return deactivateScenario(this.http, this.rootUrl, params, context);
  }

  /**
   * Delete Scenario.
   *
   * Return to baseline, clearing `activated_at`.
   *
   * The bars written while the scenario was active stay exactly as they are — going back
   * to normal is a change to what happens next, not an undo.
   *
   * This method provides access only to the response body.
   * To access the full response (for headers, for example), `deactivateScenario$Response()` instead.
   *
   * This method doesn't expect any request body.
   */
  deactivateScenario(params?: DeactivateScenario$Params, context?: HttpContext): Observable<ActiveScenario> {
    return this.deactivateScenario$Response(params, context).pipe(
      map((r: StrictHttpResponse<ActiveScenario>): ActiveScenario => r.body)
    );
  }

}
