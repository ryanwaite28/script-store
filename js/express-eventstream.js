const Stream = function() {
  var self = this;

  // object literal of connections; IP addresses as the key
  self.connections = {};

  self.enable = function() {
    return function(req, res, next) {
      res.sseSetup = function() {
        res.writeHead(200, {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive'
        })
      }

      res.sseSend = function(id, event, data) {
        var stream = "id: " + String(id) + "\n" +
        "event: " + String(event) + "\n" +
        "data: " + JSON.stringify(data) +
        "\n\n";

        // console.log(id, event, data, stream);

        res.write(stream);
      }

      next()
    }
  }

  self.push_sse = function(id, type, obj) {
    Object.keys(self.connections).forEach(function(key){
      self.connections[key].sseSend(id, type, obj);
    });
  }.bind(self);

}

/*

  Usage:
  ---

  const express = require('express');
  const Stream = require('./express-eventstream');


  const app = express();
  const stream = new Stream();
  app.use(stream.enable());


  app.get('/stream', function(request, response) {
    response.sseSetup();
    var ip = String(request.ip);
    stream.connections[ip] = response;
    stream.push_sse(1, "opened", { msg: 'connection opened!' });
  });

  app.get('/test_route', function(request, response){
    stream.push_sse(2, "new_event", { event: true });
    return response.json({ msg: 'admit one' });
  });

*/

module.exports = Stream;
