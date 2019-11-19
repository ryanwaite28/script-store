/**
 * 
 * @param p = starting number
 * @param n = weeks
 * @param t = time in years
 * @param r = rate
 * @param di = decrease or increase. `true` = increase; `false` = decrease
 * @param f = format to 2 decimal places, default is `true`
 */
function expChg(p, n, t, r, di = true, f = true) {
  const answer = di 
    ? p * ((1 + (r / n)) ** (n * t))
    : p * ((1 - (r / n)) ** (n * t));

  return f
    ? Math.round(answer * 100) / 100
    : answer;
}