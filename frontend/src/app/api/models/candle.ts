/* tslint:disable */
/* eslint-disable */

/**
 * One aggregated bar of the chart series: `GET /candles/{symbol}?tf=`.
 */
export interface Candle {
  close: number;
  high: number;
  low: number;
  open: number;

  /**
   * Tick index of the bar's first constituent tick.
   */
  t: number;
  volume: number;
}
