# PlusTerm

PlusTerm is a Scriptable Serial Terminal

Made by hardware developer for hardware devlopers.

## Principles of Plusterm:
* Basic serial monitor/terminal  
* Scriptable via Python
* Graphing with regex interpeter
* Automatic reconnection, to "lost" hardware

## Features

### Scriptability
* the "scriptability" is based on Dynamic loading of extending modules. On program (gui) start, all available modulenames are read from the "modules" folder and they are all given a row in the menu paired with a checkbox. checking one item in the list adds it to a list of active modules paired with the topic they are interested in and they then start receiveing data through a data delivery system similar to [pubsub](https://pypi.python.org/pypi/PyPubSub/3.3.0), but very lightweight and without blocking all threads. for this to work some requirements on the modules are needed. For details see the 'readme_module.txt'

### Automatic reconnection
* When the readerthread detects that the connection to the datasource is broken (e.g. USB-cord is cut or unplugged), instead of breaking out of the reading loop it goes into reconnection mode trying to reconnect until it succeds (in current state indefinitly). the readerthread then resumes reading data.

