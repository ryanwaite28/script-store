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
  if (!str) {
    console.warn('str has no value...');
    return [];
  }
  if (typeof(str) !== 'string') {
    console.warn('str argument is not of type "string"...');
    return [];
  }
  if (!char) {
    console.warn('char has no value...');
    return [];
  }
  if (!permChars) {
    console.warn('permChars has no value...');
    return [];
  }
  if (!permChars.length) {
    console.warn('permChars has no items...');
    return [];
  }

  const strDoesNotHaveChar = !str.includes(char);
  if (strDoesNotHaveChar) {
    console.warn('str does not have characters to permutate...');
    return [str];
  } else if (str === char) {
    console.warn('str is same as character to convert; return given permutations...');
    return [...permChars];
  }
  const charIsPermutation = permChars.includes(char);
  if (charIsPermutation) {
    console.warn('the char to be replaced cannot also be a permutation, otherwise an infinite loop would occur...');
    return [];
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
