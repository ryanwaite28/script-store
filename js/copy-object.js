/**
 * Check Primitive
 * ---
 *
 * Check if argument is a primitive by evaluating via `typeOf`.
 *
 * @param {*} obj
 * @returns {boolean}
 */

const checkPrimitive = (obj) => {
  if (obj === undefined) {
    console.warn(`'obj' argument was undefined; returning true...`);
    return true;
  }
  const objType = typeof(obj);
  const isPrimitive = (
    obj === null ||
    objType === 'boolean' ||
    objType === 'number' ||
    objType === 'bigint' ||
    objType === 'string' ||
    objType === 'symbol'
  );
  return isPrimitive;
};

/**
 * Copy Object
 * ---
 *
 * Deep copy object via recursion call.
 * - for primitives, just return the given argument.
 * - for Dates, call new Date instance with argument and return it
 * - for arrays, create new array and push recursive call for each item
 * - for object, create new object and set each key to recursive call
 *
 * @param {*} obj 
 * @returns {object}
 */
const copyObj = (obj) => {
  const isPrimitive = checkPrimitive(obj);
  if (isPrimitive) {
    return obj;
  }
  if (obj.constructor === Date) {
    return new Date(obj);
  }
  let copy;
  if (obj.constructor === Array) {
    copy = [];
    for (const item of obj) {
      const copyItem = copyObj(item);
      copy.push(copyItem);
    }
  } else if (obj.constructor === Object) {
    copy = {};
    const keys = Object.keys(obj);
    for (const key of keys) {
      const copyItem = copyObj(obj[key]);
      copy[key] = copyItem;
    }
  }

  return copy;
};
