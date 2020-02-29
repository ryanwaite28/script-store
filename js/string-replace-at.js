const stringRelaceChar = (str, index, char) => {
  if (!str) {
    throw new Error('no string argument provided...');
  } else if (!index) {
    throw new Error('no index argument provided...');
  } else if (!char) {
    throw new Error('no char argument provided...');
  } else if (typeof(str) !== 'string') {
    throw new Error('str argument is not of type "string"...');
  } else if (typeof(index) !== 'number') {
    throw new Error('index argument is not of type "number"...');
  } else if (index < 0) {
    throw new Error('index argument is not a natural number...');
  } else if (index > (str.length - 1)) {
    throw new Error('index argument is out of str.length range...');
  }

  const newStr = str.substr(0, index) + char + str.substr(index + 1);
  return newStr;
}