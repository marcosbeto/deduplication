var template = require('/views/template-main');  
var $ = require('jquery');
var http = require('http');


exports.connect_to_api = function(msg,callback) {  
	console.log("opa");
	callback();
};

var x = 0;
var k = 0;
var all_avisos = [];
var number_avisos = 0;
var all_duplicateds = "";
var all_duplicateds_li = "";

var arrayzao = [];

// TRANSFORMAR ARRAY EM UM ARRAY COM TODOS


exports.loopArray = function(arr, res) {

	exports.customAlert(res, arr[x].avisos[k], function(){

		if(arr[x]!=undefined && arr[x]!=null && k<arr[x].avisos.length-1) {
			k++;
			
		} else {
			k =0;
			all_duplicateds_li = all_duplicateds_li + "<li>" + all_duplicateds + "</li>"
			x++;
		}

		if(x<arr.length){
			exports.loopArray(arr, res);
		}

	});

	res.writeHead(200, {
        'Content-Type': 'text/html'
      });


	// console.log(all_duplicateds_li);

	res.write(template.build(all_duplicateds_li));

	// res.write(all_duplicateds);
	res.end();

	return arr;
}

exports.customAlert = function(res, aviso, callback) {
 
	// console.log(aviso.id_aviso);

	all_duplicateds = "";

	var options = {
      host: 'apim01.imovelweb.com.br',
      // port: 80,
      path: '/interface/buscador/ver/'+aviso.id_aviso,
      headers: {"uuid":"4788865e3938759052311306ca032077",}
    };
    
    // console.log(options.host + options.path);

	if(aviso!=undefined && aviso!=null) { 
		
		http.get(options, function(res) {
          var data = '';
          // res.setEncoding('utf8');
          res.on('data', function(dados) {
              // collect the data chunks to the variable named "html"
              data += dados

          }).on('end', function() {
              // the whole of webpage data has been collected. parsing time!
              dados_json = JSON.parse(data);

              if(dados_json.data!=null) {
              	
                aviso.url = dados_json.data.url;
                all_duplicateds = all_duplicateds + "<a href='" + dados_json.data.url + "'>"+ aviso.id_aviso + "</a>, ";  
                // all_avisos.push({"":""})
                number_avisos++;
                console.log(number_avisos);
                // all_duplicateds = "<li>" + all_duplicateds + "</li>"
                // console.log(all_duplicateds);
                // console.log("acabou");
              }
              callback();

           }).on('error', function(e) {
            console.log("Got error: " + e.message);
          });
    	});
	} else {
		callback();
	}

	// all_duplicateds = all_duplicateds + "<a href='" + dados_json.data.url + "'>"+ all[i].avisos[k] + "</a>, ";  


	// all_duplicateds = "<li>" + all_duplicateds + "</li>"

    // console.log('msg');
    // console.log(x);
    // do callback when ready

}