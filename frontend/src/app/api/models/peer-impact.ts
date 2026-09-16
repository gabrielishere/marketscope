/* tslint:disable */
/* eslint-disable */

/**
 * One same-sector peer's move since activation.
 *
 * A field of `SymbolImpact` rather than a second request: the impact panel ranks
 * same-sector instruments by impact, and without it that component would issue one
 * `/impact/{symbol}` call per peer.
 */
export interface PeerImpact {

  /**
   * The peer's move since activation, as a percentage.
   */
  move_pct: number;
  name: string;
  symbol: string;
}
