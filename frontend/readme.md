#Front-end

The front-end portion of the Real Time Telemetry Visualizer allows the user to view the data being sent by the rocket on their browser in real time.  It is easily configurable through a yaml text file.

When opened in a browser it initialized a WebSocket connection with the Back-ends client.py.  The Back-end then begins sending JSON objects containing the data it has received from the rocket to the Front-end.  It is then parsed and the data that you have specified in your config yml file is displayed.

## Usage

As long as the rocket is sending data and the Back-end server is running the user simply needs to open the html file in their browser to start seeing data.  Currently there are two html files at the root of the frontend folder:
* client.html which displays a mix of GPS and ADIS data that was requested for the prototype
* adis.html which displays all ADIS data

## Widgets

The widgets are what we use to display the data.  Currently there are three types of widgets available:
* Text is used to simply display the numbers in plain text
* LineGraph displays a value in a line graph
* Gauge displays a value in a graphical gauge

## Layout

Currently the layout of the widgets on the page are handled by the grid layout library scripts/masonry.pkgd.min.js (http://masonry.desandro.com/).  It attemps to place the widgets in the optimal position based on available vertical space.  The colors and margins of the layout are specified in css/masonry.css.

## Configuration

You are able to specify what widgets you want to see and what data those widgets contain by editing a yaml file.  The existing config files are in the configs subfolder.

### Text Example
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

* id:  This will identify the widget and be displayed as the header
* type:	Specifies that it's a Text widget
* width:	Width of widget
* height:	Height of widget
* controls:	Add each value you'd like to view in the widget
  * label:	This will be the label displayed for the value
  * source:	Specifies the value to be displayed.  Entered in the form of "packet fieldID"."value to display" 
  					Adding the suffix .Max or .Min to any value will give you the maximum or minimum value over time.
						Adding the suffix .Neg to any value will negate the incoming value.
  * units:	Specifies what units you'd like the value to be diplayed in.  The default units are MKS.
  					See scripts/quantities.js for all possible units and unit conversions

### LineGraph Example
    - id: Z-Roll
      type: LineGraph
      width: 600
      height: 320
      maxDataSize: 200
      controls:
        - label: Z Roll
          source: ADIS.GyroscopeX
          units: deg/sec

* type:	Specifies that it's a LineGraph
* maxDataSize:	Specifies how many data points will remain displayed on screen at any time
								Use Number.MAX_VALUE to keep all data displayed
* controls:	The LineGraph & Gauge widgets can only accept one value

## Unit conversion

All data being sent by the Back-end is in MKS units.  To handle converting units we use the library js-quantities (https://github.com/gentooboontoo/js-quantities).  The library contains a list of all the available units and their aliases and is located at scripts/quantities.js.  If you try to use a unit or unit conversion not supported your data will not display.
Right now the Back-end does not send the units in the JSON object so the units for each field are kept in the file scripts/units.js.  If the units sent by the backend change or additional data is send that file will need to be updated.
