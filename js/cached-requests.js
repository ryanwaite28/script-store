/**
 * Cached Requests
 * ---
 * @param {*} url 
 * @param {*} callback 
 * @param {*} responseType 
 */

const request = (url, callback, responseType = 'json') => {
  const validResponseTypes = [
    'json',
    'text',
    'blob',
  ];
  const isValidResponseType = validResponseTypes.includes(responseType);
  if (!isValidResponseType) {
    throw new Error('invalid/unknown response type...');
  }
  fetch(url)
    .then(response => response[responseType]())
    .then(data => {
      callback(data);
    })
    .catch(error => {
      console.log(error);
      throw error;
    });
}

const cachedRequest = (() => {
  const cacheMap = new Map();
  
  const fn = (url, callback, responseType = 'json') => {
    const requested = cacheMap.get(url);
    if (requested) {
      console.log('already requested: ' + url, requested);
      return callback(requested);
    }  else {
      console.log('requesting: ' + url);
      request(url, (response) => {
        console.log('caching: ' + url, response);
        cacheMap.set(url, response);
        callback(response);
      }, responseType)
    }
  };
  return fn;
})();

/**
 * Example
 */
cachedRequest('https://rmw-world-news.herokuapp.com/api/posts/random', (response) => {
  console.log(response);
});