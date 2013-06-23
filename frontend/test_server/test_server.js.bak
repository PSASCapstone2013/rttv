var WebSocketServer = require('ws').Server;
var wss = new WebSocketServer({port: 8080});
var connected = 0;

wss.on('connection', function(ws) {
	var id = setInterval(function() {
		var currentdate = new Date();
		var time = currentdate.getHours() + ":"  
			+ currentdate.getMinutes() + ":" 
			+ currentdate.getSeconds();
		
		var tojson = {};
		tojson.time = time;
		tojson.locked = 1;
		tojson.ready = 1;
		tojson.Latitude = Math.random()*100;
		tojson.Longitude = Math.random()*100;
		tojson.Height = Math.random()*1000;
		tojson.NavMode = 2;
		tojson.NumOfSats = 9;
		tojson.AccelerometerX = Math.random()*50;
		tojson.AccelerometerY = Math.random()*50;
		tojson.AccelerometerZ = Math.random()*50;
		tojson.AccelerometerMag = Math.sqrt(Math.pow(tojson.AccelerometerX,2)+Math.pow(tojson.AccelerometerY,2)+Math.pow(tojson.AccelerometerZ,2));
		
		ws.send(JSON.stringify(tojson), function() { /* ignore errors */ });
	}, 100);
	ws.on('message', function(message) {
		console.log('server received: %s', message);
	});
	console.log('opened connection: '+ws.fd);
	connected++;
	ws.send('server connected'+connected);
});

wss.on('close', function() {
	console.log('stopping client interval');
	console.log('closed connection: '+ws.id);
	connected--;
	clearInterval(id);
});
