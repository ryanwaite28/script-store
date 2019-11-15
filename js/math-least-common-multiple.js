/**
 * Least Common Multiple
 * ---
 * find least common multiple of list of numbers
 * @example
 * - lcm([60, 72, 144]); // 12
 *
 * @param {number[]} numList List of numbers.
 * @return {number} number (least common multiple)
 */
function lcm(numList) {
  // first, sort the list
  numList.sort((a, b) => a - b);

  // use the smallest number to start
  const firstNum = numList[0];

  // check the smallest number against the numbers in the list.
  // we'll create a helper method for recursive calling.
  const checkLCM = (n, list) => {
    /**
     * if none of the numbers in the list has a remainder
     * after the division of `n`, then `n` is the
     * least common factor; return `n`.
     * 
     * if at least one of the numbers in the list has a remainder
     * after the division of `n` , then `n` cannot be
     * the least common multiple;
     * call `checkLCM` again with `n - 1`  recursively until
     * the least common multiple is found -- in worst case, would be 1.
     */
    for (let num of numList) {
      const thereIsARemainder = num % n !== 0;
      if (thereIsARemainder) {
        return checkLCM(n - 1, list);
      }
    }
    return n;
  }

  return checkLCM(firstNum, numList);
}