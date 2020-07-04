/**
 * Compound Interest Formula
 * ---
 * Calculates the compound interest over time.
 * 
 * @param {number} p principal amount
 * @param {number} r interest (float)
 * @param {number} n times compounded in a given period
 * @param {number} t number of periods (days, weeks, months, years, etc.)
 * @return {number} the total value 
 */
const ci = (p, r, n, t) => p * ((1 + (r/n)) ** (n * t));