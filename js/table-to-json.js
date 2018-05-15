function table_to_json(Table){

  NodeList.prototype[Symbol.iterator] = Array.prototype[Symbol.iterator];
  HTMLCollection.prototype[Symbol.iterator] = Array.prototype[Symbol.iterator];

  let list = [];
  let key_names = [];

  let table = Table && Table.nodeName && Table.nodeName === 'TABLE' ? Table : document.querySelectorAll('table')[0];

  let thead = table.tHead;
  if(!thead) {
    throw new Error('The selected table does not have a <thead> child...');
    return;
  }
  let thead_row = thead.rows[0];
  let thead_row_children = Array.from(thead_row.children);
  let tbody = table.tBodies[0];
  let tbody_rows = tbody.rows;

  for(let th of thead_row_children) {
    let display_name = th.innerText;
    let machine_name = th.innerText.replace(/[\\\/\&\(\)]/gi, '').replace(/[\s\-]/gi, '_').replace(/[\_]{2,}/gi, '_').toLowerCase();
    key_names.push({ display_name: display_name, machine_name: machine_name });
  }

  for(let tr of tbody_rows) {
    let td_len = tr.children.length;
    let data = {};
    for(let i = 0; i < td_len; i++) {
      let td = tr.children[i];
      let machine_name = key_names[i].machine_name;
      data[machine_name] = td.innerText;
    }
    list.push(data);
  }

  console.log(list);
  console.log(JSON.stringify({ list: list }));

}
