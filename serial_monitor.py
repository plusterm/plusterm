from tkinter import *

import serial
from serial.tools import list_ports

import matplotlib.pyplot as plt

import queue
import re

from com_reader import ComReaderThread


class SerialMonitor:
	'''
	The GUI for the serial monitor. 
	'''
	def __init__(self, master):
		self.master = master
		master.title("Serial Monitor")
		master.protocol('WM_DELETE_WINDOW', self.onQuit)
		master.resizable(0,0)
	
		self.portVar = StringVar()
		self.baudVar = StringVar()
		self.plotVar = BooleanVar()
		self.zVar = BooleanVar()

		self.zVar.set(False)
		self.plotVar.set(False)
		self.portVar.set('Custom')
		self.baudVar.set('Custom')

		self.plt = plt		
		self.ser = serial.Serial()		

		self.threadq = queue.Queue()
		self.readThread = ComReaderThread(self.ser, self.threadq)

		self.cmdList = list()

		self.portChoices = self.getPorts()
		self.baudratesList = [50, 75, 110, 134, 150, 200, 300, 600, 
							1200, 1800, 2400, 4800, 9600, 19200, 38400, 
							57600, 115200, 'Custom']


		#### GUI elements

		# Connection settings
		settingsFrame = Frame(master)
		self.portLabel = Label(settingsFrame, text='Device')
		self.popupMenuPort = OptionMenu(settingsFrame, self.portVar, *self.portChoices)
		self.customPortEntry = Entry(settingsFrame, width=10)
		self.baudLabel = Label(settingsFrame, text='Baudrate')
		self.popupMenuBaud = OptionMenu(settingsFrame, self.baudVar, *self.baudratesList)
		self.customBaudEntry = Entry(settingsFrame, width=10)
		self.connectBtn = Button(settingsFrame, text='Connect', command=self.connectSerial)

		self.portLabel.pack(side='left')
		self.popupMenuPort.pack(side='left')
		self.customPortEntry.pack(side='left')
		self.baudLabel.pack(side='left')
		self.popupMenuBaud.pack(side='left')
		self.customBaudEntry.pack(side='left')
		self.connectBtn.pack(side='right')
		settingsFrame.grid(row=0, column=0, sticky=NSEW)

		# Output
		outputFrame = Frame(master)
		self.scrollbar = Scrollbar(outputFrame)
		self.textOutput = Text(outputFrame, height=30, width=70, takefocus=0, 
			yscrollcommand=self.scrollbar.set, relief=SUNKEN)
		self.scrollbar.config(command=self.textOutput.yview)

		self.textOutput.pack(side='left', fill=BOTH, expand=YES)
		self.scrollbar.pack(side='right', fill=Y)
		outputFrame.grid(row=1, column=0, sticky=NSEW)

		# Input
		inputFrame = Frame(master)
		self.inputEntry = Entry(inputFrame, width=40)
		self.inputEntry.bind('<Return>', self.onEnter)
		self.inputEntry.bind('<Up>', self.onUpArrow)
		self.inputEntry.bind('<Down>', self.onDownArrow)

		self.sendBtn = Button(inputFrame, text='Send', command=self.sendCmd)
		self.clearBtn = Button(inputFrame, text='Clear', command=self.clearOutput)

		# Check if user wants a plot of the serial data
		self.plotCheck = Checkbutton(inputFrame, text='Plot', onvalue=True, offvalue=False, 
			variable=self.plotVar, command=self.setupPlot)

		# repeat a command
		self.zCheck = Checkbutton(inputFrame, text='Repeat:', onvalue=True, offvalue=False, 
			variable=self.zVar, command=self.zMode)
		self.repeatEntry = Entry(inputFrame, width=10)

		self.inputEntry.pack(side='left')
		self.sendBtn.pack(side='left')
		self.clearBtn.pack(side='left')
		self.repeatEntry.pack(side='right')
		self.zCheck.pack(side='right')
		self.plotCheck.pack(side='right')
		inputFrame.grid(row=2, column=0, sticky=NSEW)

	# lists all the available devices connected to the computer
	def getPorts(self):
		port_list = list_ports.comports()
		ports = [port.device for port in port_list]

		ports.append('Custom')

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
			if self.portVar.get() == 'Custom':
				self.ser.port = self.customPortEntry.get()
			else:
				self.ser.port = self.portVar.get()

			if self.baudVar.get() == 'Custom':
				self.ser.baudrate = float(self.customBaudEntry.get())
			else:
				self.ser.baudrate = float(self.baudVar.get())

			self.ser.timeout = 0 # Non-blocking
			self.ser.writeTimeout = 0 # Non-blocking

			# open port with settings and start reading
			self.ser.open()
			self.textOutput.insert('end', 'Connected to {}, {}\n'
				.format(self.ser.port, self.ser.baudrate))
			
			self.readThread = ComReaderThread(self.ser, self.threadq)
			self.readThread.start()
			self.master.after(10, self.listenComThread)

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))


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
			self.inputEntry.insert('end', self.cmdList[self.cmdPointer])

		except:
			pass

	# sends command when enter is pressed
	def onEnter(self, event):
		self.sendCmd()

	def sendCmd(self):
		try:
			cmd = self.inputEntry.get()
			self.ser.write(cmd.encode())

			localEcho = '> ' + cmd + '\n'
			self.textOutput.insert('end', localEcho)

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))

		finally:
			# Clear the entry widget
			self.inputEntry.delete(0, 'end')
			self.cmdList.append(cmd)

			# only save the 10 latest commands
			if len(self.cmdList) > 10:
				self.cmdList.pop(0)

			self.cmdPointer = len(self.cmdList)
					
	def zMode(self):
		try:
			inp = self.repeatEntry.get().split(',')

			if len(inp) == 1:	
				self.ser.write(inp[0].encode())
				timer = 500

			elif len(inp) == 2:
				self.ser.write(inp[0].encode())
				timer = int(inp[1])

			# repeat
			if self.zVar.get() == True:
				self.master.after(timer, self.zMode)

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))


	def setupPlot(self):
		if self.plotVar.get() == True:
			self.plt.ion()
			self.fig, (self.ax1, self.ax2) = self.plt.subplots(2,1)
			self.ax1.grid(True)	
			self.ax2.grid(True)

		else:
			self.plt.ioff()
			#self.plt.close()

	def livePlot(self, data=None):
		''' 
		Experimental. Matches the serial output string with a regex. 
		If data read from serial is 1 numerical value, plot it on 
		the y-axis with a timestamp on the x-axis.
		If 2 numerical values are read, plot them (x,y) = (value1,value2).
		Each alternative gets its own subplot.
		Data from thread is a tuple (timestamp, data)
		'''
		try:
			numericData = re.findall("-?\d*\.\d+|-?\d+", data[1].decode())

			if len(numericData) == 1:
				self.ax1.plot(data[0], float(numericData[0]), 'b.')		
								
			elif len(numericData) == 2:
				self.ax2.plot(float(numericData[0]), float(numericData[1]), 'r.')

			else:
				pass

		except:
			# If something went wrong, do nothing
			pass


def main():
	root = Tk()
	app = SerialMonitor(root)
	root.mainloop()

if __name__ == '__main__':
	main()