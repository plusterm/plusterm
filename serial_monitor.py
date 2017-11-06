from tkinter import *
import serial
from serial.tools import list_ports
import matplotlib.pyplot as plt
import threading
import queue
import time
import re


class ComMonitorThread(threading.Thread):
	''' 
	Creates a thread that continously reads from the serial connection
	Puts the result in a queue.

	Input: a serial connection, and a queue instance
	Output: tuple (timestamp, data) into queue
	'''
	def __init__(self, ser, que):
		threading.Thread.__init__(self)
		self.ser = ser
		self.que = que

		self.alive = threading.Event()
		self.alive.set()

		# reset the timer
		startTime = time.clock()

	def run(self):
		while self.alive.isSet():

			# reads data until newline (x0A/10) 
			data = self.ser.read(1)
			if len(data) > 0:
				while data[-1] != 0x0A:
					data += self.ser.read(1)

				timestamp = time.clock()
				self.que.put((timestamp, data))
			
		# close the connection when alive event is cleared
		if self.ser:
			self.ser.close()

	def stop(self, timeout=None):
		self.alive.clear()
		threading.Thread.join(self, timeout)



class SerialMonitorGUI:
	'''
	The GUI for the serial monitor. 
	'''
	def __init__(self, master):
		self.master = master
		master.title("Serial Monitor")
		master.protocol('WM_DELETE_WINDOW', self.onQuit)
		master.resizable(0,0)
	
		self.portVar = StringVar()
		self.baudVar = IntVar()
		self.portVar.set(None)
		self.baudVar.set(9600)

		self.ser = serial.Serial()		

		self.threadq = queue.Queue()
		self.readThread = ComMonitorThread(self.ser, self.threadq)

		self.plt = plt
		self.cmdList = list()

		self.portChoices = self.getPorts()
		self.baudratesList = [50, 75, 110, 134, 150, 200, 300, 600, 
							1200, 1800, 2400, 4800, 9600, 19200, 38400, 
							57600, 115200]

		# Connection settings
		self.portLabel = Label(master, text='Device').grid(row=0, column=0)
		self.popupMenuPort = OptionMenu(master, self.portVar, *self.portChoices)
		self.popupMenuPort.grid(row=0, column=1)
		self.baudLabel = Label(master, text='Baudrate').grid(row=0, column=2)
		self.popupMenuBaud = OptionMenu(master, self.baudVar, *self.baudratesList)
		self.popupMenuBaud.grid(row=0, column=3)

		self.connectBtn = Button(master, text='Connect', command=self.connectSerial).grid(row=0, column=69)

		# Output
		self.scrollbar = Scrollbar(master)
		self.textOutput = Text(master, height=30, width=70, takefocus=0, yscrollcommand=self.scrollbar.set)
		self.scrollbar.config(command=self.textOutput.yview)
		self.textOutput.grid(row=2, column=0, columnspan=70, rowspan=30)
		self.scrollbar.grid(row=2, rowspan=30, column=70, sticky=N+S)

		# Input
		self.inputEntry = Entry(master, width=50, takefocus=1)
		self.inputEntry.grid(row=33, column=0, columnspan=5)
		self.inputEntry.bind('<Return>', self.onEnter)
		self.inputEntry.bind('<Up>', self.onUpArrow)
		self.inputEntry.bind('<Down>', self.onDownArrow)

		self.sendBtn = Button(master, text='Send', command=self.sendCmd)
		self.sendBtn.grid(row=33, column=6)
		self.clearBtn = Button(master, text='Clear', command=self.clearOutput)
		self.clearBtn.grid(row=33, column=7)

		# Check if user wants a plot of the serial data
		self.plotVar = BooleanVar()
		self.plotVar.set(False)
		self.plotCheck = Checkbutton(master, text='Plot', onvalue=True, offvalue=False, 
			variable=self.plotVar, command=self.livePlot)
		self.plotCheck.grid(row=33, column=9)

		# z-mode
		self.zVar = BooleanVar()
		self.zVar.set(False)
		self.zCheck = Checkbutton(master, text='Z-mode', onvalue=True, offvalue=False, 
			variable=self.zVar, command=self.zMode)
		self.zCheck.grid(row=33, column=10)

	# lists all the available devices connected to the computer
	def getPorts(self):
		port_list = list_ports.comports()
		ports = [port.device for port in port_list]
		return ports

	def connectSerial(self):
		try:
			# if port is open, close it
			if self.ser.is_open:
				self.ser.close()

			# kill thread if it's alive 
			if self.readThread.isAlive():
				self.readThread.stop(0.01)

			# Set the serial connection options
			self.ser.port = self.portVar.get()
			self.ser.baudrate = self.baudVar.get()
			self.ser.timeout = 0 # Non-blocking
			self.ser.writeTimeout = 0 # Non-blocking

			# open port with settings and start reading
			self.ser.open()
			self.textOutput.insert('end', 'Connected to {}, {}\n'.format(self.ser.port, self.ser.baudrate))
			
			self.readThread = ComMonitorThread(self.ser, self.threadq)
			self.readThread.start()
			self.master.after(10, self.listenComThread)

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))

	def zMode(self):		
		self.ser.write(b'z')

		if self.zVar.get() == True:
			self.master.after(1000, self.zMode)

	def listenComThread(self):
		try:
			result = self.threadq.get(False)
		except queue.Empty:
			pass
		else:
			self.textOutput.insert('end', result[1].decode())
			self.textOutput.see('end')

			# If checkbutton for plot is set, send data to plot function
			if self.plotVar.get() == True:
				self.livePlot(result)

		# check again
		self.master.after(10, self.listenComThread)	

	# When closing the window, close serial connection and stop thread
	def onQuit(self):
		if(self.readThread.isAlive()):
			self.readThread.stop(0.01)

		self.ser.close()
		self.master.destroy()

   	# clears the output text widget
	def clearOutput(self):
		self.textOutput.delete(1.0, 'end')

	# cycles previously entered commands
	def onUpArrow(self, event):		
		try:
			self.inputEntry.delete(0, 'end')
			self.cmdPointer -= 1

			if self.cmdPointer < 0:
				self.cmdPointer = 0
			self.inputEntry.insert('end', self.cmdList[self.cmdPointer])

		except:
			pass

	def onDownArrow(self, event):
		try:
			self.inputEntry.delete(0, 'end')
			self.cmdPointer += 1

			if self.cmdPointer == len(self.cmdList):
				self.cmdPointer = len(self.cmdList) - 1
	
			self.inputEntry.insert('end', self.cmdList[self.cmdPointer])

		except:
			pass

	# sends command when enter is pressed
	def onEnter(self, event):
		self.sendCmd()

	def sendCmd(self):
		try:
			command = self.inputEntry.get()
			self.ser.write(command.encode())

			localEcho = '> ' + command + '\n'
			self.textOutput.insert('end', localEcho)

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))

		finally:
			# Clear the entry widget
			self.inputEntry.delete(0, 'end')
			self.cmdList.append(command)

			# only save the 10 latest commands
			if len(self.cmdList) > 10:
				self.cmdList.pop(0)

			self.cmdPointer = len(self.cmdList)
					

	def livePlot(self, data=None):
		''' 
		Experimental. Matches the serial output string with a regex. 
		If data read from serial is 1 numerical value, plot it on 
		the y-axis with a timestamp on the x-axis.
		If 2 numerical values are read, plot them (x,y) = (value1,value2)
		Data from thread is a tuple (timestamp, data)
		'''
		self.plt.ion()
		try:
			numericData = re.findall("-?\d*\.\d+|-?\d+", data[1].decode())

			if len(numericData) == 2:				
				self.plt.plot(float(numericData[0]), float(numericData[1]), 'ro')

			elif len(numericData) == 1:
				self.plt.plot(data[0], float(numericData[0]), 'bo')

		except:
			# If something went wrong, do nothing
			pass


def main():
	root = Tk()
	gui = SerialMonitorGUI(root)
	root.mainloop()

if __name__ == '__main__':
	main()