(function(){

  // inspired by:
  // https://www.npmjs.com/package/idb
  // https://github.com/jakearchibald/idb

  

  window.indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;

  if(!window.indexedDB) {
    console.log('indexedDB not supported...');
    return;
  }
  else {
    // console.log('indexed DB is supported!');
  }

  const uniqueValue = function() {
    return String(Date.now()) +
	    Math.random().toString(36).substr(2, 34) +
	    Math.random().toString(36).substr(2, 34) +
	    Math.random().toString(36).substr(2, 34)
  }

  window.uniqueValue = uniqueValue;

  const STORE = function(db, storeName) {
    let self = this;
    self.get_store = function(){
      var transaction = db.transaction([storeName]);
      return transaction.objectStore(storeName);
    }
    self.get_all = function() {
      return new Promise(function(resolve, reject){
        var transaction = db.transaction([storeName]);
        var objectStore = transaction.objectStore(storeName);
        var request = objectStore.getAll();
        request.error = function(event) { return reject(event); }
        request.onsuccess = function(event) { return resolve(event.target.result); }
      });
    }
    self.create = function(data) {
      return new Promise(function(resolve, reject){
        var transaction = db.transaction([storeName], "readwrite");
        var objectStore = transaction.objectStore(storeName);
        transaction.onerror = function(event) {
          console.log(event);
          return reject('could not create', event);
        };
        transaction.oncomplete = function(event) {
          return resolve();
        };
        if(!data.id || data.id.constructor !== String) { data.id = uniqueValue() }
        var request = objectStore.add(data);
        request.onsuccess = function(event) {};
      });
    }
    self.read = function(key) {
      return new Promise(function(resolve, reject){
        var transaction = db.transaction([storeName]);
        var objectStore = transaction.objectStore(storeName);
        var request = objectStore.get(key);
        request.error = function(event) { return reject(event); }
        request.onsuccess = function(event) { return resolve(event.target.result); }
      });
    }
    self.update = function(key, data) {
      return new Promise(function(resolve, reject){
        var transaction = db.transaction([storeName], "readwrite");
        var objectStore = transaction.objectStore(storeName);
        var request = objectStore.get(key);
        request.error = function(event) { return reject(event); }
        request.onsuccess = function(event) {
          if(data.id) { delete data.id }
          var updates = Object.assign({}, event.target.result, data);
          var requestUpdate = objectStore.put(updates);
          requestUpdate.onerror = function(event) {
            return reject(event);
          };
          requestUpdate.onsuccess = function(event) {
            return resolve(event);
          };
        }
      });
    }
    self.destroy = function(key) {
      return new Promise(function(resolve, reject){
        var transaction = db.transaction([storeName], "readwrite");
        var objectStore = transaction.objectStore(storeName);
        var request = objectStore.delete(key);
        request.error = function(event) { return reject(event); }
        request.onsuccess = function(event) { return resolve(); }
      });
    }
  }

  const DB = function(db) {
    let self = this;
    self.get_db = function(){ return db; }
    self.stores = function(storeName) {
      if(!db.objectStoreNames.contains(storeName)) {
        let error_msg = 'this store does not exist in current database version: ' + storeName;
        console.log(error_msg);
        throw new Error(error_msg);
        return;
      }
      return new STORE(db, storeName);
    }
  }

  //

  window.IDB = function(db_name, version, callback){
    let self = this;
    return new Promise(function(resolve, reject){
      let resolved = false;
      self.request = window.indexedDB.open(db_name, version);
      self.request.onupgradeneeded = function(event) {
        var db = event.target.result;
        if(callback && callback.constructor === Function) { callback(event) }
        if(resolved == true) { return; }
        resolved = true;
        resolve(new DB(db));
      };
      self.request.onerror = function(event) {
        reject(event);
      };
      request.onsuccess = function(event) {
        var db = event.target.result;
        if(resolved == true) { return; }
        resolved = true;
        resolve(new DB(db));
      };
    });
  }
})()



/* --- Example --- */



var names_db = IDB('names_db', 1, function(event){
  var db = event.target.result;
   var objectStore = db.createObjectStore('names', {keyPath: 'id'});
   objectStore.createIndex("name", "name", { unique: false });
});

function create_person(data) {
  return new Promise(function(resolve, reject){
    names_db.then(function(db){
      db.stores('names').create(data)
      .then(function(){
        console.log('added!');
        return resolve();
      })
      .catch(function(e){
        console.log('error', e);
        return reject(e);
      });
    });
  });
}

function get_person(key) {
  return new Promise(function(resolve, reject){
    names_db.then(function(db){
      db.stores('names').read(key)
      .then(function(data){
        console.log('read!');
        return resolve(data);
      })
      .catch(function(e){
        console.log('error', e);
        return reject(e);
      });
    });
  });
}

function get_all_people() {
  return new Promise(function(resolve, reject){
    names_db.then(function(db){
      db.stores('names').get_all()
      .then(function(data){
        console.log('read all!');
        return resolve(data);
      })
      .catch(function(e){
        console.log('error', e);
        return reject(e);
      });
    });
  });
}

function update_person(key, data) {
  return new Promise(function(resolve, reject){
    names_db.then(function(db){
      db.stores('names').update(key, data)
      .then(function(){
        console.log('updated!');
        return resolve();
      })
      .catch(function(e){
        console.log('error', e);
        return reject(e);
      });
    });
  });
}

function delete_person(key) {
  return new Promise(function(resolve, reject){
    names_db.then(function(db){
      db.stores('names').destroy(key)
      .then(function(){
        console.log('deleted!');
        return resolve();
      })
      .catch(function(e){
        console.log('error', e);
        return reject(e);
      });
    });
  });
}
