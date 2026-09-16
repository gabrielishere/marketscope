/**
 * The shared number formatters, so no component formats a figure its own way.
 *
 * Two rules matter here and both are visual:
 *
 * * **Percentages are always signed**, using U+2212 MINUS SIGN and not a hyphen. A
 *   hyphen is narrower than a plus in most faces, so a column of mixed signs shifts by a
 *   fraction of a character as values cross zero. U+2212 is designed to match the plus.
 * * **Decimal places are carried on the instrument**, never inferred from the value. A
 *   price that gains or loses a decimal as it moves changes its own column width.
 */

/** U+2212 MINUS SIGN. Not a hyphen — see the module note. */
const MINUS = '−';

/** A price at the instrument's own fixed precision. */
export function formatPrice(value: number, dp: number): string {
  return withMinus(value.toFixed(dp));
}

/** A holding size. Fractional quantities are legitimate, so two places always show. */
export function formatQuantity(value: number): string {
  return withMinus(value.toFixed(2));
}

/** A percentage, always signed: `+1.24%` / `−1.24%`. */
export function formatSignedPercent(value: number): string {
  const sign = value < 0 ? MINUS : '+';
  return `${sign}${Math.abs(value).toFixed(2)}%`;
}

/** A currency figure, always signed, for a change or a return. */
export function formatSignedCurrency(value: number): string {
  const sign = value < 0 ? MINUS : '+';
  return `${sign}$${Math.abs(value).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/** A currency figure with no forced sign, for a total. */
export function formatCurrency(value: number): string {
  return `$${value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/** A volume, abbreviated so the column stays narrow. */
export function formatVolume(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toFixed(0);
}

function withMinus(text: string): string {
  return text.startsWith('-') ? MINUS + text.slice(1) : text;
}
