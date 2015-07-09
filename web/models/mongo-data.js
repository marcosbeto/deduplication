var mongo = require('mongodb'),  
  Server = mongo.Server,
  Db = mongo.Db;
var server = new Server('localhost', 27017, {  
  auto_reconnect: true
});
var db = new Db('deduplication', server);  
var onErr = function(err, callback) {  
  db.close();
  callback(err);
};

exports.ads_all_similar = function(callback) {  
  db.open(function(err, db) {

    if (!err) {

      db.collection('ads_all_similar_use', function(err, collection) {

        if (!err) {
          collection.find({}).toArray(function(err, avisos) {

            if (!err) {

              var intCount = avisos.length;

              

              if (intCount > 0) {
                var ads_all_similar = "";
                for (var i = 0; i < intCount;) {

                  var need_to_add = false;

                  var ad_json = "";
                  
                  if(avisos[i].all_equals!=null && avisos[i].all_equals!=undefined && avisos[i].all_equals!='undefined') {
                    need_to_add = true;
                    for (var k =0;k<avisos[i].all_equals.length;k++) {
                      ad_json += '{"id_aviso":"' + avisos[i].all_equals[k] + '", "url":""}';  
                      if (k < avisos[i].all_equals.length-1) {
                        ad_json += ',';
                      }
                    }

                  ads_all_similar += '{"avisos":[' + ad_json + ']}';  
                  
                  }


                  
                  i = i + 1;

                  if (need_to_add && i < intCount) {
                    ads_all_similar += ',';
                  } else {
                    if (ads_all_similar.substring(ads_all_similar.length - 1, ads_all_similar.length) == ",") {
                      ads_all_similar = ads_all_similar.substring(0, ads_all_similar.length - 1);
                    }
                  }


                  
                }

                ads_all_similar = '{"all_avisos":[' + ads_all_similar + "]}"
                
                callback("",JSON.parse(ads_all_similar));
                console.log("db closed");
                db.close();

              }
            } else {
              onErr(err, callback);
            }
          }); //end collection.find 
        } else {
          onErr(err, callback);
        }
      }); //end db.collection
    } else {
      onErr(err, callback);
    }
  }); // end db.open
};