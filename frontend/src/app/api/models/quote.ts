/* tslint:disable */
/* eslint-disable */

/**
 * One entry of the polled quote set: `GET /quotes?symbols=`.
 */
export interface Quote {

  /**
   * (close_latest / close_at_session_start - 1) * 100.
   */
  day_change_pct: number;

  /**
   * Latest close from the ring buffer.
   */
  last: number;

  /**
   * Recent closes, oldest first and the latest last, for the row sparkline. Prices, not returns; drawn on its own scale.
   */
  sparkline: Array<number>;

  /**
   * The instrument's ticker symbol.
   */
  symbol: string;
}
