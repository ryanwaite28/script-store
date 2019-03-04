/*

  https://github.com/ryanwaite28/script-store/blob/master/js/array-sortby.js
  https://ryanwaite28.github.io/script-store/js/array-sortby.js
  
  ---

  Example

  let people = [
    { name: 'John', age: 0 },
    { name: 'Jane', age: 0 },
  ];
  
  people.sortBy("name", "asc");

*/



Array.prototype.sortBy = function(property, direction, isDateString) {
  let tempArray = [...this];
  tempArray.sort(function(a, b){
    let x, y;
    if(isDateString === true) {
      x = new Date(a[property]);
      y = new Date(b[property]);
    } else {
      x = a[property].constructor === String && a[property].toLowerCase() || a[property];
      y = b[property].constructor === String && b[property].toLowerCase() || b[property];
    }
    let value = direction && String(direction) || "asc";
    switch(value) {
      case "asc":
        // asc
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;
      case "desc":
        // desc
        if (x > y) {return -1;}
        if (x < y) {return 1;}
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
