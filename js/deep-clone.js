/**
 * Deep Clone
 * ---
 *
 * deep cloning an object/array via recursion.
 *
 * @param value - Value to be cloned
 * @return clone of `value`
 */
function deepClone (value) {
  const checkObjOrArr = (i) => {
    const isObjOrArr = i.constructor === Object || i.constructor === Array;
    return isObjOrArr;
  }

  const cloneValue = (i) => {
    try {
      switch (i.constructor) {
        case Date:
        case Map:
        case WeakMap:
        case Set:
        case WeakSet: {
          return new i.constructor(i);
        }
        default: {
          // if primitive, just return it
          return i;
        }
      }
    } catch (e) {
      console.log(e);
      return i;
    }
  }

  let clone;

  try {
    if (value.constructor === Object) {
      clone = { ...value };
      clone.constructor = value.constructor;
      Object.keys(clone).forEach((key) => {
        const isObjOrArr = checkObjOrArr(clone[key]);
        clone[key] = isObjOrArr ? deepClone(clone[key]) : cloneValue(clone[key]);
      });
    } else if (value.constructor === Array) {
      clone = [ ...value ];
      clone.constructor = value.constructor;
      for (let i = 0; i < clone.length; i++) {
        const isObjOrArr = checkObjOrArr(clone[i]);
        clone[i] = isObjOrArr ? deepClone(clone[i]) : cloneValue(clone[i]);
      }
    } else {
      return cloneValue(value);
    }

    return clone;
  } catch (e) {
    console.log(e);
    return value;
  }
};
