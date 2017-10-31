from tkinter import *
import serial
from serial.tools import list_ports

# Get available ports
def getPorts():
	port_list = list_ports.comports()
	ports = [port.device for port in port_list]
	return ports

def connectSerial():
	try:
		# if port is already open, close it
		if ser.is_open:
			ser.close()

		ser.port = portVar.get()
		ser.baudrate = baudrateVar.get()
		ser.timeout = 0
		ser.writeTimeout = 0

		# Open port with settings and start reading
		ser.open()
		textOutputWidget.insert('end', 'Connected to {}, {}\n'.format(ser.port, ser.baudrate))
		readSerial()
	except Exception as e:
		textOutputWidget.insert('end', '{}\n'.format(e))

def clearOutput():
	textOutputWidget.delete(1.0, 'end')

# Reacts to 'enter' in input entry, and sends command 
def getInput(event):
	sendCmd()

# Sends a command
def sendCmd():
	try:
		command = inputEntry.get()
		ser.write(command.encode())
	except Exception as e:
		textOutputWidget.insert('end', '{}\n'.format(e))
	finally:
		inputEntry.delete(0, 'end')

def readSerial():
	try:
		serBuffer = ''
		while ser.inWaiting() > 0:
			c = ser.read().decode()
			serBuffer += c		
		textOutputWidget.insert('end', serBuffer)
	except Exception as e:
		textOutputWidget.insert('end', e)

	# Scroll down automatically
	# ISSUE: Locks the scrollbar, since readSerial() is called repeatedly
	textOutputWidget.see('end')
	root.after(10, readSerial)

# on change dropdown value
def change_port(*args):
    print('Port set to', portVar.get())

def change_baudrate(*args):
	print('Baudrate set to', baudrateVar.get())


# Initialize a serial connection
ser = serial.Serial()

# ==========
#    GUI
# ==========

# Setup root window
root = Tk()
root.title('Serial Monitor')

# Add a grid and frame
mainframe = Frame(root)
mainframe.grid(column=0, row=0, sticky=W)
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)

# Tkinter variables
portVar = StringVar(root)
baudrateVar = IntVar(root)

# Possible options
port_choices = getPorts()
baudrates_list = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

## Setup options
# Port
portVar.set(None)
popupMenuPort = OptionMenu(mainframe, portVar, *port_choices)

# Baudrate
baudrateVar.set(9600)
popupMenuBaud = OptionMenu(mainframe, baudrateVar, *baudrates_list)

# Display options on frame
Label(mainframe, text="Device:").grid(row = 0, column = 1)
popupMenuPort.grid(row = 0, column = 2)
Label(mainframe, text="Baudrate:").grid(row = 0, column = 3)
popupMenuBaud.grid(row = 0, column = 4)
connectBtn = Button(root, text='Connect', command=connectSerial)
connectBtn.grid(row=0, sticky=E)

# Text widget for serial output (with scrollbar)
scrollbar = Scrollbar(root)
scrollbar.grid(row=2, column=1, sticky=N+S)
textOutputWidget = Text(root, height=30, width=70, takefocus=0, yscrollcommand=scrollbar.set)
textOutputWidget.grid(row=2, column=0)
scrollbar.config(command=textOutputWidget)

# Entry for serial input
inputEntry = Entry(root, width=87, takefocus=1)
inputEntry.grid(row=3, column=0, sticky=W)
inputEntry.bind('<Return>', getInput)

# Clear button
clearBtn = Button(root, text='Clear', command=clearOutput)
clearBtn.grid(row=3, column=3, sticky=W)

# Send button
sendBtn = Button(root, text='Send', command=sendCmd)
sendBtn.grid(row=3, sticky=E)

portVar.trace('w', change_port)
baudrateVar.trace('w', change_baudrate)
root.mainloop()