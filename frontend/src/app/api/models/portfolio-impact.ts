/* tslint:disable */
/* eslint-disable */
import { SymbolImpact } from '../models/symbol-impact';

/**
 * `GET /impact/portfolio` — the same decomposition, by holding.
 *
 * Never resolved as an instrument lookup for a symbol named `portfolio`.
 */
export interface PortfolioImpact {

  /**
   * One breakdown per held position.
   */
  holdings: Array<SymbolImpact>;

  /**
   * Total impact on the portfolio since activation, in currency.
   */
  total_impact: number;
}
