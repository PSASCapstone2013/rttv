How To Run the Server:
----------------------
On the command line:

    sqlite3 rocket.sqlite < make_db.in
    python server.py "" 12345 testfile.txt &

1. `""` - host address. Leave this as-is.
2. `12345` - the port number (this can be anything we want).
9. `testfile.txt` - output file name (can be anything we want; probably should be a date/time stamp).



For the Front End:
-------------------
Make `getlastpacket.php` executable.
Put `getlastpacket.php` in the HTML directory.
Make an Ajax call to the URL of the `getlastpacket.php` file. This will return a JSON string.

Update: 
in client.py
    - Count_mess: the rate of transmitting message to the client's browser ( currently setting = 1000)
    - for GPS, MPL3, MPU9 message: skip only send every 1000th message to the client's browser
    - for ADIS message: average 1000 message, then send to the client's browser

