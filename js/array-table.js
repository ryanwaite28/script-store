function array_to_table(array) {
  var headings = Object.keys(array[0]);

  var table = document.createElement('table');
  var thead = document.createElement('thead');
  var th_tr = document.createElement('tr');
  var tbody = document.createElement('tbody');

  headings.forEach(function(heading){
    var th = document.createElement('th');
    th.innerHTML = heading;
    th_tr.appendChild(th);
  });

  thead.appendChild(th_tr);

  array.forEach(function(obj){
    var tr = document.createElement('tr');
    headings.forEach(function(heading){
      var td = document.createElement('td');
      td.innerHTML = obj[heading] || '...';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);

  return table;

}
