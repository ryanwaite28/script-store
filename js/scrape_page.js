function scrape_page(url) {
  // using: http://multiverso.me/AllOrigins/
  return new Promise(function(resolve, reject){
    if(!jQuery){
      return reject({ error: true, message: 'jQuery is required for this function to work' });
    }

    if(url.substr(0,4) === 'http') {
      // cross-origin
      jQuery.getJSON('http://allorigins.me/get?url=' + encodeURIComponent(url) + '&callback=?', function(data){
        return resolve({ contents: data.contents });
      });
    }
    else {
      // same-origin
      jQuery.get(url, function(data){
        return resolve({ contents: data });
      });
    }
  });
}

/*

  Scrape a page for it's html
  ---

  example:

  scrape_page('http://www.google.com')
  .then(function(data){
    var html = data.contents;
  })

*/
