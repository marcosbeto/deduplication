var http_IP = '127.0.0.1';  
var http_port = 8000;  
var http = require('http');  
var server = http.createServer(function(req, res) {  
  require('./router').get(req, res);
  // res.writeHead(200, {'Content-Type': 'text/plain'});
  // res.write("fuck");
  
}); // end server() 
server.listen(http_port, http_IP);  
console.log('listening to http://' + http_IP + ':' + http_port);  