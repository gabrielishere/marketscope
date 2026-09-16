/* tslint:disable */
/* eslint-disable */
import { FactorContribution } from '../models/factor-contribution';
import { PeerImpact } from '../models/peer-impact';

/**
 * `GET /impact/{symbol}` — the move since activation and what drove it.
 */
export interface SymbolImpact {

  /**
   * Ordered by descending absolute contribution.
   */
  contributions: Array<FactorContribution>;

  /**
   * log(close_now / close_at_activation). The contributions plus the residual reconcile with this to within 1e-6.
   */
  log_return: number;

  /**
   * Headline move since activation: (close_now / close_at_activation - 1) * 100.
   */
  move_pct: number;

  /**
   * Same-sector peers, ranked by descending absolute move_pct. A field rather than a second request.
   */
  peers: Array<PeerImpact>;

  /**
   * Impact on the holding in currency terms; null when the symbol is not held. Always present.
   */
  position_impact: (number | null);

  /**
   * The idiosyncratic term, in log space.
   */
  residual: number;
  symbol: string;
}
