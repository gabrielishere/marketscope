/* tslint:disable */
/* eslint-disable */

/**
 * One factor's share of a move since activation.
 */
export interface FactorContribution {

  /**
   * Log-space contribution since activation: beta * factor move.
   */
  contribution: number;

  /**
   * The instrument's beta to this factor. Expanded detail only.
   */
  exposure: number;
  factor: string;

  /**
   * The factor's own cumulative move since activation, as a percentage.
   */
  factor_move_pct: number;

  /**
   * One plain-language sentence, carrying no beta and no exposure value.
   */
  sentence: string;
}
