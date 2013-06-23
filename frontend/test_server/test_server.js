var WebSocketServer = require('ws').Server;
var wss = new WebSocketServer({port: 8080});
var connected = 0;

wss.on('connection', function(ws) {
	var id = setInterval(function() {
		var tojson = {};
		var currentdate = new Date();
		
		if (currentdate.getMilliseconds()%2 == 0){
			tojson.fieldID = 'GPS\x01';
			tojson.AgeOfDiff = Math.round(Math.random()*100);
			tojson.ExtendedAgeOfDiff = Math.round(Math.random()*100000);
			tojson.GPSTimeOfWeek = Math.random()*100000;
			tojson.GPSWeek = Math.round(Math.random()*100000);
			tojson.Height = Math.random()*10000;
			tojson.Latitude = Math.random()*100;
			tojson.Longitude = Math.random()*100;
			tojson.NavMode = Math.round(Math.random()*10);
			tojson.NumOfSats = Math.round(Math.random()*10);
			tojson.StdDevResid = Math.random()*100;
			tojson.timestamp = Math.round(Math.random()*100000000);
			tojson.VEast = Math.random()*100;
			tojson.VNorth = Math.random()*100;
			tojson.Vup = Math.random()*1000;
		}
		else {
			tojson.fieldID = 'ADIS';
			tojson.AccelerometerX = Math.round(Math.random()*70000);
			tojson.AccelerometerY = Math.round(Math.random()*70000);
			tojson.AccelerometerZ = Math.round(Math.random()*70000);
			tojson.AccelerometerMagn = Math.sqrt(Math.pow(tojson.AccelerometerX,2)+Math.pow(tojson.AccelerometerY,2)+Math.pow(tojson.AccelerometerZ,2));
			tojson.AuxiliaryADC = Math.round(Math.random()*1000);
			tojson.GyroscopeMagn = Math.random()*100000;
			tojson.GyroscopeX = Math.round(Math.random()*100000);
			tojson.GyroscopeY = Math.round(Math.random()*100000);
			tojson.GyroscopeZ = Math.round(Math.random()*100000);
			tojson.MagnetometerMagn = Math.random()*100000;
			tojson.MagnetometerX = Math.round(Math.random()*100000);
			tojson.MagnetometerY = Math.round(Math.random()*100000);
			tojson.MagnetometerZ = Math.round(Math.random()*100000);
			tojson.PowerSupply = Math.round(Math.random()*10000);
			tojson.Temperature = Math.round(Math.random()*10000);
			tojson.timestamp = Math.round(Math.random()*100000000);
		}

		ws.send(JSON.stringify(tojson), function() { /* ignore errors */ });
	}, 9);
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
