## Front-end

The front-end portion of the Real Time Telemetry Visualizer allows the user to view the data being sent by the rocket on their browser in real time.  It is easily configurable through a yaml text file.

When opened in a browser it initializes a WebSocket connection with client.py, which then begins sending JSON objects containing the data it has received from the rocket to the front-end via websockets.  The packets are parsed and the data specified in the config ```.yml``` file is displayed.

### Usage

Once the rocket is sending data and the backend server is running, simply navigate to [http://localhost/8080](http://localhost/8080) to start seeing data.

#### Specifying the config file

client.html loads the config file specified by the URL query string paramater ```config```.

For example, ```http://localhost:8080/?config=test_config.yml``` would display data using the config file in ```static/config/test_config.yml```.

If no config file is specified in the URL, the default is is ```config.yml```.

Currently, there are two config files:
* **config.yml** (default) displays a mix of GPS and ADIS data that was requested for the prototype
* **adis_config.yml** displays all ADIS data

### Widgets

Widgets display data.  Currently there are three types of widgets available:
* **Text** is used to simply display the numbers in plain text
* **LineGraph** displays a value in a line graph
* **Gauge** displays a value in a graphical gauge

### Configuration

You are able to specify which widgets are displayed, what data they display and where they are oriented on the page by editing a yaml file.  The existing config files can be found in ```static/config/*.yml```.

#### Layout Example

A custom layout can be created by specifying columns and their widths.  In each widget you can then specify what column they will appear in.  You can also nest column layouts within other columns.  This layout method is achieved by nesting div elements and inserting the widgets into them in the order that they appear in the config file.  The colors and margins of the layout are specified in ```static/css/style.css```.

    - type: Layout
      columns:
        - id: column1
          width: 25%
        - id: column2
          width: 75%
          columns:
            - id: column2_a
              width: 100%
            - id: column2_b
              width: 50%
            - id: column2_c
              width: 50%

* **type**:	Specifies that it's the layout
* **id**:	Identifies each column, each widget will then specify what column they reside in using this id
* **width**:	Width of the column; can be specified in % or px

#### Text Widget Example
    - id: Example Text Widget
      type: Text
      width: 200
      height: 150
      column: column1
      controls:
        - label: X
          source: ADIS.AccelerometerX
          units: m/s^2
        - label: Lat
          source: GPS1.Latitude
          units: deg

* **id**:	This identifies the widget and will be displayed as the header
* **type**:	Specifies that it's a Text widget
* **width**:	Width of widget
* **height**:	Height of widget
* **column**:	Column widget will be placed in
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
      column: column2
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

### Packet Stats

```json
{
  'fieldID': 'Stats',
  'PacketsReceivedTotal': total packets received
  'PacketsLostTotal': total packets lost
  'PacketsReceivedRecently': number of packet received in a specific time interval
  'PacketsLostRecently': number of packet lost in a specific time interval
  'MostRecentTimestamp': timestamp of the latest packet received
  'TimeLastPacketReceived': time since last packet received, formate as hh:mm:ss:s
}
```

