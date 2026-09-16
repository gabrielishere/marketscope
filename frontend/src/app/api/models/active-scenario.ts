/* tslint:disable */
/* eslint-disable */

/**
 * `GET /scenario` — the active scenario, its headlines and its activation tick.
 */
export interface ActiveScenario {

  /**
   * Tick index the active scenario was activated at; null at baseline. Always present.
   */
  activated_at: (number | null);

  /**
   * Two or three canned headlines.
   */
  headlines: Array<string>;
  id: string;
  name: string;
}
