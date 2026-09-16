/* tslint:disable */
/* eslint-disable */

/**
 * One ranked row of `GET /movers`.
 */
export interface Mover {
  day_change_pct: number;
  last: number;

  /**
   * Sum of volume from session start to the latest bar.
   */
  session_volume: number;
  symbol: string;
}
