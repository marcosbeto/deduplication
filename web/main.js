var template = require('views/template-main');  

// var template = require('../views/template-main');  
// var mongo_data = require('../model/mongo-data');  
exports.get = function(req, res) {  


	var res1 = res
	var mongodb = require('mongodb');
  
	//We need to work with "MongoClient" interface in order to connect to a mongodb server.
	var MongoClient = mongodb.MongoClient;

	// Connection URL. This is where your mongodb server is running.
	var url = 'mongodb://localhost:27017/deduplication';

	var arrays = []

	// Use connect method to connect to the Server
	MongoClient.connect(url, function (err, db) {
	  if (err) {
	    console.log('Unable to connect to the mongoDB server. Error:', err);
	  } else {
	    //HURRAY!! We are connected. :)
	    console.log('Connection established to', url);
	  }
	    // Get the documents collection
	    var collection = db.collection('ads_all_similar');

	    // all_duplicateds = colect.find();
	    // console.log(all_duplicateds);


	    var cursor = collection.find();

	    collection.find().toArray(function(err, items) {
	        db.close();
	        console.log("tamare");
	        res.write("lenga56s");
	        arrays.push(items);
	    });

	});

	console.log(arrays.length);

	for (var i = 0; i < arrays.length; i++) {
	    console.log(arrays[i]);
	    //Do something
	}

	
  	res.end();
};

// //We need to work with "MongoClient" interface in order to connect to a mongodb server.
// var MongoClient = mongodb.MongoClient;

// // Connection URL. This is where your mongodb server is running.
// var url = 'mongodb://localhost:27017/deduplication';

// // Use connect method to connect to the Server
// MongoClient.connect(url, function (err, db) {
//   if (err) {
//     console.log('Unable to connect to the mongoDB server. Error:', err);
//   } else {
//     //HURRAY!! We are connected. :)
//     console.log('Connection established to', url);

//     // Get the documents collection
//     var collection = db.collection('ads_all_similar');

//     // all_duplicateds = colect.find();
//     // console.log(all_duplicateds);



//     //We have a cursor now with our find criteria
//     var cursor = collection.find();

//     collection.find().toArray(function(err, items) {
//         db.close();
//         console.log(items);
//     });

//  //    collection.find(function(err, cursor){
// 	//     cursor.toArray(callback);
// 	//     db.close();
// 	// });

//  //    cursor.each(function (err, doc) {
//  //      if (err) {
//  //        console.log(err);
//  //      } else {
//  //        console.log('Fetched:', doc);
//  //      }
//  //    });
    
//  //    db.close();

//     //Create some users
//     // var user1 = {name: 'modulus admin', age: 42, roles: ['admin', 'moderator', 'user']};
//     // var user2 = {name: 'modulus user', age: 22, roles: ['user']};
//     // var user3 = {name: 'modulus super admin', age: 92, roles: ['super-admin', 'admin', 'moderator', 'user']};

//     // Insert some users
//     // collection.insert([user1, user2, user3], function (err, result) {
//     //   if (err) {
//     //     console.log("###### Erro ######");
//     //     // console.log(err);
//     //   } else {
//     //     console.log('Inserted %d documents into the "users" collection. The documents inserted with "_id" are:', result.length, result);
//     //   }
//     //   //Close connection
//     //   
//     // });
//   }
// });