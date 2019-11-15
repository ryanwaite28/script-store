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
function lcm(numList: number[] | Array<number>) {
  // first, sort the list
  numList.sort((a, b) => a - b);

  // use the smallest number to start
  const firstNum: number = numList[0];

  // check the smallest number against the rest.
  // we'll create a helper method for recursive calling
  const checkLCM = (n: number, list: number[]) => {
    for (let num of numList) {
      const thereIsARemainder: boolean = num % n !== 0;
      if (thereIsARemainder) {
        return checkLCM(n - 1, list);
      }
    }
    return n;
  }

  return checkLCM(firstNum, numList);
}