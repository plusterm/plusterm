from tkinter import *
from tkinter.filedialog import askopenfile

import serial
from serial.tools import list_ports

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
style.use('bmh')

import queue
import re
import time

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

		self.portVar.set('Custom')
		self.baudVar.set('Custom')
		self.zVar.set(False)
		self.plotVar.set(False)

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
		
		menu = Menu(master)
		master.config(menu=menu)
		script = Menu(menu)

		script.add_command(label = 'Open', command=self.openScriptFile)
		menu.add_cascade(label = 'Run script', menu = script)

		# Connection settings
		settingsFrame = Frame(master)
		self.portLabel = Label(settingsFrame, text='Device:')
		self.popupMenuPort = OptionMenu(settingsFrame, self.portVar, *self.portChoices)
		self.customPortEntry = Entry(settingsFrame, width=10)
		self.baudLabel = Label(settingsFrame, text='     Baudrate:')
		self.popupMenuBaud = OptionMenu(settingsFrame, self.baudVar, *self.baudratesList)
		self.customBaudEntry = Entry(settingsFrame, width=10)
		self.connectBtn = Button(settingsFrame, text='Open', command=self.connectSerial)
		self.disconnectBtn = Button(settingsFrame, text='Close', command=self.disconnectSerial)

		self.portLabel.pack(side='left')
		self.popupMenuPort.pack(side='left')
		self.customPortEntry.pack(side='left')
		self.baudLabel.pack(side='left')
		self.popupMenuBaud.pack(side='left')
		self.customBaudEntry.pack(side='left')
		self.connectBtn.pack(side='right', padx=17)
		self.disconnectBtn.pack(side='right')
		settingsFrame.grid(row=0, column=0, sticky=NSEW)

		# Output
		outputFrame = Frame(master)
		self.scrollbar = Scrollbar(outputFrame)
		self.textOutput = Text(outputFrame, height=30, width=80, takefocus=0, 
			yscrollcommand=self.scrollbar.set, borderwidth=1, relief='sunken')
		self.scrollbar.config(command=self.textOutput.yview)

		self.textOutput.pack(side='left')
		self.scrollbar.pack(side='right', fill=Y)
		outputFrame.grid(row=1, column=0, sticky=NSEW)

		# Input
		inputFrame = Frame(master)
		self.inputEntry = Entry(inputFrame, width=50)
		self.inputEntry.bind('<Return>', self.onEnter)
		self.inputEntry.bind('<Up>', self.onUpArrow)
		self.inputEntry.bind('<Down>', self.onDownArrow)

		self.sendBtn = Button(inputFrame, text='Send', command=self.onSendClick)
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
		self.repeatEntry.pack(side='right', padx=17, ipadx=0)
		self.zCheck.pack(side='right')
		self.plotCheck.pack(side='left')
		inputFrame.grid(row=2, column=0, sticky=NSEW)


	def getPorts(self):
		# lists all the available devices connected to the computer
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

			self.ser.timeout = 0.01

			# open port with settings and start reading
			self.ser.open()
			self.textOutput.insert('end', 'Connected to {}, {}\n'
				.format(self.ser.port, self.ser.baudrate))
			
			self.readThread = ComReaderThread(self.ser, self.threadq)
			self.readThread.start()
			self.master.after(10, self.listenComThread)

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))

	def disconnectSerial(self):
		try:
			self.master.after_cancel(self.listenComThread)
			self.readThread.stop(0.01)
			self.ser.close()
			self.textOutput.insert('end', 'Port closed\n')
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

		# check again (unless program is quitting)
		try:
			self.master.after(5, self.listenComThread)	
		except:
			pass

	def onQuit(self):	
		# When closing the window, close serial connection and stop thread
		if self.readThread.isAlive():
			self.readThread.stop(0.01)

		if self.ser.is_open:
			self.master.after_cancel(self.listenComThread)
			self.ser.close()			

		self.master.quit()
		self.master.destroy()


	def clearOutput(self):
		# clears the output text widget
		self.textOutput.delete(1.0, 'end')


	def onUpArrow(self, event):
		# cycles previously entered commands
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


	def onEnter(self, event):
		# sends command when enter is pressed
		cmd = self.inputEntry.get()
		self.sendCmd(cmd)


	def onSendClick(self):
		cmd = self.inputEntry.get()
		self.sendCmd(cmd)
					

	def zMode(self):
		# Repeat sends a command, by default evey 500 ms
		# Specify time limit with a comma, e.g. 'c, 100'
		try:
			inp = self.repeatEntry.get().split(',')

			if len(inp) == 1:
				self.sendCmd(inp[0])
				timer = 500

			elif len(inp) == 2:
				self.sendCmd(inp[0])
				timer = int(inp[1])

			# repeat
			if self.zVar.get() == True:
				try:
					self.master.after(timer, self.zMode)
				except:
					pass

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))


	def sendCmd(self, cmd):
		try:
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


	def setupPlot(self):
		if self.plotVar.get() == True:
			self.plotFrame = Frame(self.master)
			clearPlotBtn = Button(self.plotFrame, text='Clear', command=self.clearPlot)
			clearPlotBtn.pack(pady=3)

			self.fig, (self.ax1, self.ax2) = self.plt.subplots(2,1)

			self.canvas = FigureCanvasTkAgg(self.fig, self.plotFrame)
			self.canvas.get_tk_widget().pack()

			toolbar = NavigationToolbar2TkAgg(self.canvas, self.plotFrame)
			toolbar.update()

			self.plotFrame.grid(column=1, row=0, rowspan=35)

			self.xValOne = []
			self.xValTwo = []
			self.yValOne = []
			self.yValTwo = []

		else:
			self.plotFrame.destroy()


	def livePlot(self, data=None):
		''' 
		Matches the serial output string with a regex. 
		If data read from serial is 1 numerical	value, plot it on the 
		y-axis with timestamp on the x-axis.
		If 2 numerical values are read, plot them (x,y) = (value1,value2).
		Data from thread is a tuple (timestamp, data)
		'''
		if data is not None:
			numericData = re.findall("-?\d*\.\d+|-?\d+", data[1].decode())
		
			if len(numericData) == 1:
				self.ax1.clear()		
				self.xValOne.append(float(data[0]))
				self.yValOne.append(float(numericData[0]))

				if len(self.xValOne) > 51:
					self.xValOne.pop(0)
					self.yValOne.pop(0)

				self.ax1.plot(self.xValOne, self.yValOne, '.-')

			elif len(numericData) == 2:
				self.ax2.clear()
				self.xValTwo.append(float(numericData[0]))
				self.yValTwo.append(float(numericData[1]))

				if len(self.xValTwo) > 51:
					self.xValTwo.pop(0)
					self.yValTwo.pop(0)

				self.ax2.plot(self.xValTwo, self.yValTwo, '.-')

			self.canvas.draw()


	def clearPlot(self):
		self.ax1.clear()
		self.ax2.clear()
		#self.canvas.draw()

	def openScriptFile(self):
		file = askopenfile(filetypes =(("Text File", "*.txt"),("All Files","*.*")),
							title = "Choose a file")
		try:			
			with open(file.name, 'r') as f:
				text = f.read()
				self.sendScript(text)
				
		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))


	def sendScript(self, text):
		'''
		Takes a comma separated text with commands to send to
		the serial device, with a small delay.

		Syntax:
		
		command[*int] - sends command int (optional) times, e.g. c, c*10
		sleep[float] - sleeps for float seconds, e.g. sleep1
		delay[float] - sets the delay time, float seconds, for sending
		'''

		delay = 0.05
		split_text = text.split(',')
		for line in split_text:

			if 'delay' in line:
				d = line.split('delay')
				delay = float(d[1])

			elif '*' in line:
				mult = line.split('*')
				for i in range(int(mult[1])):
					self.sendCmd(mult[0])
					self.master.update()
					time.sleep(delay)
					self.master.update()

			elif 'sleep' in line:
				sleep = line.split('sleep')
				self.master.update()
				time.sleep(float(sleep[1]))
				self.master.update()

			else:
				self.sendCmd(line)
				self.master.update()
				time.sleep(delay)
				self.master.update()


def main():
	root = Tk()
	app = SerialMonitor(root)

	root.mainloop()

if __name__ == '__main__':
	main()