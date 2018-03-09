Array.prototype.removeDuplicates = function() {
  var old_list = this;
  var new_list = [];

  old_list.forEach(function(value) {
    if(new_list.indexOf(value) === -1) {
      new_list.push(value);
    }
  });

  return new_list;
}
