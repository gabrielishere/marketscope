/* tslint:disable */
/* eslint-disable */

/**
 * One tile of `GET /macro` — one instrument per factor, in factor order.
 */
export interface MacroDriver {
  day_change_pct: number;

  /**
   * The factor this driver carries unit exposure to.
   */
  factor: string;
  last: number;
  name: string;
  symbol: string;
}
