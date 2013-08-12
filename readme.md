## Front-end

The front-end portion of the Real Time Telemetry Visualizer allows the user to view the data being sent by the rocket on their browser in real time.  It is easily configurable through a yaml text file.

When opened in a browser it initializes a WebSocket connection with client.py, which then begins sending JSON objects containing the data it has received from the rocket to the front-end via websockets.  The packets are parsed and the data specified in the config ```.yml``` file is displayed.

### Usage

Once the rocket is sending data and the backend server is running, simply navigate to [http://localhost/8080](http://localhost/8080) to start seeing data.

Currently there are two html files in the ```static``` resources directory:
* **client.html** displays a mix of GPS and ADIS data that was requested for the prototype
* **adis.html** displays all ADIS data

### Widgets

Widgets display data.  Currently there are three types of widgets available:
* **Text** is used to simply display the numbers in plain text
* **LineGraph** displays a value in a line graph
* **Gauge** displays a value in a graphical gauge

### Layout

Currently the widget layout on the page is handled by the grid layout library [masonry](http://masonry.desandro.com/).  It attemps to place the widgets in the optimal position based on available vertical space.  The colors and margins of the layout are specified in ```static/css/masonry.css```.

### Configuration

You are able to specify which widgets are displayed and which data those widgets display by editing a yaml file.  The existing config files can be found in ```static/config/*.yml```.

#### Text Widget Example
    - id: Example Text Widget
      type: Text
      width: 200
      height: 150
      controls:
        - label: X
          source: ADIS.AccelerometerX
          units: m/s^2
        - label: Lat
          source: "GPS\x01.Latitude"
          units: deg

* **id**:	This identifies the widget and will be displayed as the header
* **type**:	Specifies that it's a Text widget
* **width**:	Width of widget
* **height**:	Height of widget
* **controls**:	Add each value you'd like to view in the widget
  * **label**:	This will be the label displayed for the value
  * **source**:	Specifies the value to be displayed.  Entered in the form of ```[packet_field_ID].[value_to_display]```.
  					    Adding the suffix ```.Max``` or ```.Min``` to any value will give you the maximum or minimum value over time.  
						    Adding the suffix ```.Neg``` to any value will negate the incoming value.
  * **units**:	Specifies what units you'd like the value to be diplayed in.  The default units are MKS.  
  					See ```static/scripts/quantities.js``` for all possible units and unit conversions

#### LineGraph Widget Example
    - id: Z-Roll
      type: LineGraph
      width: 600
      height: 320
      maxDataSize: 200
      controls:
        - label: Z Roll
          source: ADIS.GyroscopeX
          units: deg/sec

* **type**:	Specifies that it's a LineGraph
* **maxDataSize**:	Specifies how many data points will remain displayed on screen at any time  
								Use ```Number.MAX_VALUE``` to keep all data displayed
* **controls**:	The LineGraph & Gauge widgets can only accept one value

### Unit conversion

All data being sent by the backend is in MKS units.  To handle converting units we use the library [js-quantities](https://github.com/gentooboontoo/js-quantities).  The library contains a list of all the available units and their aliases and is located at ```static/scripts/quantities.js```.  If you try to use a unit or unit conversion not supported your data will not display.
Right now the backend does not send the units in the JSON object so the incoming units for each field are kept in the file ```static/scripts/units.js```.  If the units sent by the backend changes or additional data added that file will need to be updated.


## JSON message format

### GPS

```json
{
  'fieldID': 4 bytes,
  'timestamp': 6 bytes,
  'AgeOfDiff': 1byte,
  'NumOfSats': 1byte,
  'GPSWeek': 2byte,
  'GPSTimeOfWeek': double,
  'Latitude': double,
  'Longitude': double,
  'Height': float,
  'VNorth': float,
  'VEast': float,
  'Vup': float,
  'StdDevResid': float,
  'NavMode': 2 bytes,
  'ExtendedAgeOfDiff': 2 bytes
}
```


### ADIS

```json
{                             
  'fieldID': 4 bytes,<br>
  'timestamp': 6 bytes,<br>
  'PowerSupply': 2 bytes,     volts (V)
  'GyroscopeX': 2 bytes,      degrees per second (deg/sec)
  'GyroscopeY': 2 bytes,      degrees per second (deg/sec)
  'GyroscopeZ': 2 bytes,      degrees per second (deg/sec)
  'GyroscopeMagn': float,     degrees per second (deg/sec)
  'AccelerometerX': 2 bytes,  meters per second squared (m/s^2)
  'AccelerometerY': 2 bytes,  meters per second squared (m/s^2)
  'AccelerometerZ': 2 bytes,  meters per second squared (m/s^2)
  'AccelerometerMagn': float, meters per second squared (m/s^2)
  'MagnetometerX': 2 bytes,   teslas (T)
  'MagnetometerY': 2 bytes,   teslas (T)
  'MagnetometerZ': 2 bytes,   teslas (T)
  'MagnetometerMagn': float,  teslas (T)
  'Temperature': 2 bytes,     Kelvin (K)
  'AuxiliaryADC': 2 bytes     volts (V)
}
```

### ERRO

```json
{
  'fieldID',
  'timestamp',
  'message': string
}
```

### MESG

```json
{
  'fieldID',
  'timestamp',
  'message': string
}
```

### Packet Analyze

```json
{
  'fieldID': 'Analyze',
  'PacketReceived':       number of packet received in a specific time interval
  'latestPacketReceived': timestamp of the latest packet received 
  'PacketLost':[]
}
```

#### PacketLost is a list of lost packet, each element has:

```json
{
  'From'      : time when we start loosing packets
  'To'        : time when we receive a new packet
  'PacketLost': Number of packets lost
}
```
