/* tslint:disable */
/* eslint-disable */
import { PortfolioTotals } from '../models/portfolio-totals';
import { Position } from '../models/position';

/**
 * `GET /portfolio`.
 */
export interface PortfolioResponse {
  positions: Array<Position>;
  totals: PortfolioTotals;
}
