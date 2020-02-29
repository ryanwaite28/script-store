function permutateString(
  str,
  char,
  permChars
) {
  // if there are no question marks, return
  if (!str.includes('?')) {
    return [str];
  } else if (str === char) {
    return [...permChars];
  }

  const listOfPermutations = [];

  for (let permChar of permChars) {
    let newStr = str.replace(char, permChar);
    const stillHasCar = newStr.includes(char);
    if (stillHasCar) {
      const newPermList = permutateString(newStr, char, permChars);
      listOfPermutations.push(...newPermList);
    } else {
      listOfPermutations.push(newStr);
    }
  }

  return listOfPermutations;
}

const c = permutateString('0?0?', '?', ['a', 'b']);
console.log(c);
