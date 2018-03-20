String.prototype.contains = function(value) {
  if(!value) {
    throw new Error('no value argument was given...');
    return;
  }
  if(value.constructor !== String) {
    console.log('value: ', value);
    throw new Error('the given value argument was not of type String...');
    return;
  }

  if(this.indexOf(value) !== -1) {
    var regexp = new RegExp( value, 'g', 'i' );
    return { resp: true, matches: this.match(regexp) };
  }
  else {
    return { resp: false, matches: null };
  }
}

/*

  Check if a string contains a substring.
  If so, return every match
  ---

  Example:

  var string = '1_hnuiorfgbvoisfbgv_1_NDOITNGIDnis_1';
  if(string.contains('1').resp === true) {
    console.log('contains!');
  }

*/
