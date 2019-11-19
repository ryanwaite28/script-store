/**
 * Get initial value
 * ---
 * * Formula
 * ---
 * A = Pe^rt -or- A = P * e^(r * t)
 *
 * STEPS:
 * - first, divide both sides by e^rt
 * - now, P = A / e^rt
 * - return the new value
 *
 * @param {number} a = the future/end value
 * @param {number} r = the rate
 * @param {float/decimal} t = the time in years
 * @return {number} the initial value
 */
function getInitialValue(a, r, t) {
  const e = Math.E;
  const ert = (e ** (r * t))
  const newA = a / ert;
  return newA;
}