const rotateList = (arr, dir) => {
  const dirIsValid = dir === 'right' || dir === 'left';
  let direction = dirIsValid ? dir : 'right';
  const goRight = direction === 'right';

  if (!arr) {
    return;
  } else if (!arr.length) {
    return;
  } else if (arr.length === 1) {
    return [...arr];
  }

  const copyArr = [...arr];
  const tempArr = [];
  const item = goRight
    ? copyArr.pop()
    : copyArr.shift();

  goRight
    ? tempArr.push.call(tempArr, item, ...copyArr)
    : tempArr.push.call(tempArr, ...copyArr, item);

  return tempArr;
};