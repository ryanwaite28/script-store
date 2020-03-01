/**
 * String permutation
 * ---
 *
 * Given a string, a target substring and a list of strings to replace with,
 * this function returns an array of all permutations.
 * 
 * Example:
 * - permutateString('0?1?', '?', ['0', '1']) → ['0010', '0011', '0110', '0111']
 *
 * @param {string} str 
 * @param {string} char 
 * @param {array} permChars 
 * @returns {array}
 */

function permutateString(
  str,
  char,
  permChars
) {
  // if there are no question marks, return
  const doesNotHaveChar = !str.includes(char);
  if (doesNotHaveChar) {
    return [str];
  } else if (str === char) {
    return [...permChars];
  }

  const listOfPermutations = [];

  for (let permChar of permChars) {
    let newStr = str.replace(char, permChar);
    const stillHasChar = newStr.includes(char);
    if (stillHasChar) {
      const newPermList = permutateString(newStr, char, permChars);
      listOfPermutations.push(...newPermList);
    } else {
      listOfPermutations.push(newStr);
    }
  }

  return listOfPermutations;
}

function testListUnique (list) {
  const map = new Map();
  for (const i of list) {
    const hasSeen = map.has(i);
    if (hasSeen) {
      return false;
    } else {
      map.set(i, i);
    }
  }
  return true;
}
