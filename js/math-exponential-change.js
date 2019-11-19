/**
 * 
 * @param p = starting number
 * @param n = weeks
 * @param t = time in years
 * @param r = rate
 * @param di = decrease or increase. `true` = increase; `false` = decrease
 * @param f = format to 2 decimal places, default is `true`
 * @param apy = APY (annual percentage yield) to 3 decimal places, default is `true`
 */
function expChg(p, n, t, r, di = true, f = true, apy = false) {
  const answer = di 
    ? p * ((1 + (r / n)) ** (n * t))
    : p * ((1 - (r / n)) ** (n * t));

  const formatted = f
    ? Math.round(answer * 100) / 100
    : answer;

  return apy
    ? { answer: formatted, apy: (((1 + (r / n)) ** n) - 1) * 100 }
    : formatted;
}