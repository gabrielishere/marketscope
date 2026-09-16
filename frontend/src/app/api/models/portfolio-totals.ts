/* tslint:disable */
/* eslint-disable */

/**
 * One set of figures — there is no FX rate, so there is nothing to sum across.
 */
export interface PortfolioTotals {

  /**
   * Uninvested cash balance.
   */
  cash: number;

  /**
   * Today's change in currency.
   */
  day_change: number;

  /**
   * Today's change as a percentage, per the day change % definition.
   */
  day_change_pct: number;

  /**
   * Total return in currency.
   */
  total_return: number;

  /**
   * Total return as a percentage.
   */
  total_return_pct: number;

  /**
   * Total portfolio value.
   */
  value: number;
}
