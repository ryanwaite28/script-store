/**
 * Accumulated Sum
 * ---
 * Given an array of numbers, return a new array where each index
 * is the sum of that number and every number before it in the array.
 * Example:
 * - [1, 2, 3, 4, 5] -> [1, 3, 6, 10, 15]
 *
 * @param {int[]} arr list of integers/numbers
 * @returns {int[]} list of accumulated sum array
 */

function accumulatedSum(arr) {
  const tempArr = [];
  let prevVal = 0;
  for (let i = 0; i < arr.length; i++) {
	  let currentVal = prevVal + arr[i];
	  tempArr.push(currentVal);
    prevVal = currentVal;
  }
  return tempArr;
}