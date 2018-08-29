Array.prototype.sortBy = function(property, direction) {
  let tempArray = this;
  tempArray.sort(function(a, b){
    var x = a[property].toLowerCase();
    var y = b[property].toLowerCase();
    let value = direction && String(direction) || "asc";
    switch(value) {
      case "asc":
        // asc
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;

      case "desc":
        // desc
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;

      default:
        // asc
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;
    }
  });
  return tempArray;
}
