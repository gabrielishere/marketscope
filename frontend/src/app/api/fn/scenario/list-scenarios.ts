/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { ScenarioSummary } from '../../models/scenario-summary';

export interface ListScenarios$Params {
}

export function listScenarios(http: HttpClient, rootUrl: string, params?: ListScenarios$Params, context?: HttpContext): Observable<StrictHttpResponse<Array<ScenarioSummary>>> {
  const rb = new RequestBuilder(rootUrl, listScenarios.PATH, 'get');
  if (params) {
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<Array<ScenarioSummary>>;
    })
  );
}

listScenarios.PATH = '/scenarios';
