/* tslint:disable */
/* eslint-disable */

/**
 * One entry of the symbol list: `GET /symbols?q=`.
 *
 * With `q` omitted or empty this carries the static metadata the markets table
 * loads once at load rather than on every poll.
 */
export interface SymbolMatch {

  /**
   * Constant across the universe; the UI has a symbol to render.
   */
  currency: string;

  /**
   * Fixed decimal places for this instrument's price, never inferred.
   */
  decimals: number;
  name: string;
  sector: string;
  symbol: string;
}
