var template = require('../views/template-main');  
var mongo_data = require('../models/mongo-data'); 
var Client = require('node-rest-client').Client;
var api_connect = require('../controllers/api_connect');
var $ = require('jquery');
var http = require('http');


exports.get = function(req, res) {  


  mongo_data.ads_all_similar(function(err, ads_all_similar) {
    
    console.log("Upeaaaaa: " + ads_all_similar.all_avisos.length);
    // console.log(ads_all_similar.all_avisos.length);


    if (!err) {

      lis = api_connect.loopArray(ads_all_similar.all_avisos, res);

       console.log('lisssssssssssss');
       console.log(lis);

      // for (i=0;i<arr.length;i++){
      //   console.log(arr[i].avisos);
      // }

      
      console.log("done_console")

      // res.writeHead(200, {
      //   'Content-Type': 'text/html'
      // });
      
      

      


          // var html = '';

          // for(y=0; y < ads_all_similar.all_avisos[i].avisos.length) {
          //   id_aviso = ads_all_similar.all_avisos[i].avisos[y]
            
          //   var options = {
          //       host: 'apim01.imovelweb.com.br',
          //       // port: 80,
          //       path: '/interface/buscador/ver/'+id_aviso,
          //       headers: {"uuid":"4788865e3938759052311306ca032077",}
          //   };

          //   http.get(options, function(res) {
              
          //     res.setEncoding('utf8');
              
          //     res.on('data', function(dados) {
          //         // collect the data chunks to the variable named "html"
          //         console.log("############");
          //         console.log(dados.fotos);
          //         // html += dados;
          //     }).on('end', function() {
          //         // the whole of webpage data has been collected. parsing time!
          //         // var title = $(html).find('title').text();
          //         console.log("acabou");
          //      }).on('error', function(e) {
          //       console.log("Got error: " + e.message);
          //     });
          // });
          // }


      // var client = new Client();
 
      // // set content-type header and data as json in args parameter 
      // args ={
      //   headers:{"uuid":"4788865e3938759052311306ca032077"} // request headers 
      // };
 
 
      // client.get("http://apim01.imovelweb.com.br/interface/buscador/ver/2922547503", args, 
      //             function(data, response){
      //             // parsed response body as js object 
      //             console.log(data);
      //             // raw response 
      //             console.log(response);
      // });
       
       
      // registering remote methods 
      // client.registerMethod("jsonMethod", "http://apim01.imovelweb.com.br/interface/buscador/ver/2922547503", "GET");
       
      // client.methods.jsonMethod(args,function(data,response){
      //     // parsed response body as js object 
      //     console.log(data);
      //     // raw response 
      //     console.log(response);
      // });

      
    } else {
      res.writeHead(200, {
        'Content-Type': 'text/html'
      });
      res.write(template.build("Oh dear", "Database error", "<p>Error details: " + err + "</p>"));
      res.end();
    }
  });

};