/* tslint:disable */
/* eslint-disable */
import { ScenarioId } from '../models/scenario-id';

/**
 * The body of `POST /scenario`. Typed to the enum, which is what makes a 422.
 */
export interface ActivateScenarioRequest {

  /**
   * An id the scenario library holds.
   */
  id: ScenarioId;
}
