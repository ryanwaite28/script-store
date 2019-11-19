/**
 * 
 * @param p = starting number
 * @param n = weeks
 * @param t = time in years
 * @param r = rate
 * @param di = decrease or increase. `true` = increase; `false` = decrease
 */
function expChg(p, n, t, r, di = true) {
  return di 
    ? p * ((1 + (r / n)) ** (n * t))
    : p * ((1 - (r / n)) ** (n * t));
}