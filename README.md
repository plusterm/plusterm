# PlusTerm

PlusTerm is a Scriptable Serial Terminal

Made by hardware developers for hardware developers.

## Principles of Plusterm:
* Basic serial monitor/terminal  
* Scriptable via Python
* Graphing with regex interpeter
* Automatic reconnection

## Description
NOTE: This (wx-pubsub) is the actively maintained branch. 

### Pre-requisites
The basic pre-requisites to run PlusTerm, are
* python (developed with v3.6)
* wxpython (developed with v4.0.0b2)
* pypubsub (developed with v4.0.0)
* pyserial (developed with v3.4)

For plotting, you will also need 
* matplotlib (developed with v2.1.0)

Other modules might depend on additional libraries.

The entry-point to run the application is serial_monitor.py.

### Operation

For connecting, there are a few options. A quick-style (8N1) connect is available in the main window. For more options, go to File > Connection. Here is also an option to initialize an arbitrary (but basic) socket connection. 
In File > History, a list of successful connections will be saved. To reconnect with the settings saved, just click the desired entry.
On the bottom of the main window, you can type, choose whether you want to send a linebreak, and then press either `Enter` or `Send` button, to send to the device. Up arrow will recover the last sent command. The Clear button will clear the output textarea.

PlusTerm, when connected, will start a thread that continously reads from the serial port, and put the data in queues, when encountering newline '\n' (currently a big limitation, so keep this in mind). PlusTerm will periodically try to retrieve from these queues. The pubsub module will finally broadcast the data to the rest of the application. The published message is always a tuple: (timestamp, data), where timestamp is relative to epoch (i.e. absolute time when first byte in data was read), and data is a Python bytestring.

Because of the pubsub backend, it makes it easy to add functionality to PlusTerm (hence the 'Scriptable via Python' principle). All that needs to be done, is place your script in a subfolder in the Modules folder, with an `__init__.py`. The script itself, basically only has two mandatory pre-requisites: a pubsub subscription to a topic ('serial.data' is most likely the relevant one, although 'serial.error' is also available), and a callback function for when receiving messages. Additionally, PlusTerm itself is subscribed to 'module.send', making it possible to automate sending anything to the connection from the module itself (without typing it into the GUI). To tell PlusTerm to import the script, click the script name, in the Modules menu drop down. A few modules are already present, so please have a look there. When unticking the module, PlusTerm will try to run a dispose() function in the loaded script, where it's possible to put any extra code that should be run when "unloading" the script.