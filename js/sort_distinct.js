/*

  Filter/Sort an array of objects by a given key.
  ---

  This function returns an object with a property for every
  distinct value by the given key in the array of objects.
  Each property will be an array of all the objects with the same
  value by the given key.

  Example:

  var list = [
    {brand: 'a'},
    {brand: 'b'},
    {brand: 'c'}
  ];

  var sorted_brands = sort_distinct(list, 'brand');
  console.log(sorted_brands);

  output:

  >> {
  >>  'a': [{brand: 'a'}],
  >>  'b': [{brand: 'b'}],
  >>  'c': [{brand: 'c'}],
  >> }

*/

'use strict';

function sort_distinct(array, key) {
  if(!array || Array.isArray(array) === false) {
    console.log('array input: ', array);
    throw new Error('First parameter must be an array.');
    return;
  }
  if(!key || key.constructor !== String) {
    console.log('key input: ', key);
    throw new Error('Second parameter must be a string.');
    return;
  }

  var obj = {
    _stray: [] // a list for objects that don't have the given key.
  }

  array.forEach(function(item) {
    if(item[key] !== undefined){
      var value = item[key];
      if(obj[value] === undefined) {
        obj[value] = [];
        obj[value].push(item);
      }
      else {
        obj[value].push(item);
      }
    }
    else {
      obj['_stray'].push(item);
    }
  });

  return obj;
}
