/* tslint:disable */
/* eslint-disable */
import { Mover } from '../models/mover';

/**
 * `GET /movers`. The API's ordering is the contract; the client re-sorts nothing.
 */
export interface MoversResponse {

  /**
   * Descending by day change %.
   */
  gainers: Array<Mover>;

  /**
   * Ascending by day change %.
   */
  losers: Array<Mover>;

  /**
   * Descending by session volume.
   */
  most_active: Array<Mover>;
}
