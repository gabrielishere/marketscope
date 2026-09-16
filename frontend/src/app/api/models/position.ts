/* tslint:disable */
/* eslint-disable */

/**
 * One paper holding: an entry of `GET /portfolio`.
 */
export interface Position {

  /**
   * Average entry price.
   */
  avg_entry: number;

  /**
   * Position size is a float, never an integer.
   */
  quantity: number;
  symbol: string;

  /**
   * Unrealised profit and loss in the single currency.
   */
  unrealised_pnl: number;
}
