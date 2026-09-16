/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpContext, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { StrictHttpResponse } from '../../strict-http-response';
import { RequestBuilder } from '../../request-builder';

import { ActivateScenarioRequest } from '../../models/activate-scenario-request';
import { ActiveScenario } from '../../models/active-scenario';

export interface ActivateScenario$Params {
      body: ActivateScenarioRequest
}

export function activateScenario(http: HttpClient, rootUrl: string, params: ActivateScenario$Params, context?: HttpContext): Observable<StrictHttpResponse<ActiveScenario>> {
  const rb = new RequestBuilder(rootUrl, activateScenario.PATH, 'post');
  if (params) {
    rb.body(params.body, 'application/json');
  }

  return http.request(
    rb.build({ responseType: 'json', accept: 'application/json', context })
  ).pipe(
    filter((r: any): r is HttpResponse<any> => r instanceof HttpResponse),
    map((r: HttpResponse<any>) => {
      return r as StrictHttpResponse<ActiveScenario>;
    })
  );
}

activateScenario.PATH = '/scenario';
