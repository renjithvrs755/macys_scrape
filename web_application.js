var express = require('express');
var app = express();
var MongoClient = require('mongodb').MongoClient;
var url = 'mongodb://localhost:27017/scrape_data';


app.route('/').get(function(req, res)
{
	MongoClient.connect(url, function(err, db) {
  if (err) throw err;
  //retrieving all the documents from the specified collection
  db.collection("Data_Collection").find().toArray(function(err, result) {
    if (err) throw err;
    //response header changint to application/json for retun the data as a list of json objects
    res.setHeader('Content-Type', 'application/json');
    //sending the results to the browser
    res.send(result);
    db.close();
  });
  });

});

var server = app.listen(3000, function() {}); 