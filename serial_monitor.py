from tkinter import *
import serial
from serial.tools import list_ports
import matplotlib.pyplot as plt

class SerialMonitorGUI:
	def __init__(self, master):
		self.master = master
		master.title("Serial Monitor")
	
		self.portVar = StringVar()
		self.baudVar = IntVar()
		self.portVar.set(None)
		self.baudVar.set(9600)

		self.ser = serial.Serial()
		self.plt = plt

		self.portChoices = self.GetPorts()
		self.baudratesList = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

		# Connection settings
		self.portLabel = Label(master, text='Device').grid(row=0, column=0)
		self.popupMenuPort = OptionMenu(master, self.portVar, *self.portChoices).grid(row=0, column=1)
		self.baudLabel = Label(master, text='Baudrate').grid(row=0, column=2)
		self.popupMenuBaud = OptionMenu(master, self.baudVar, *self.baudratesList).grid(row=0, column=3)
		self.connectBtn = Button(master, text='Connect', command=self.ConnectSerial).grid(row=0, column=69)

		# Output
		self.scrollbar = Scrollbar(master)
		self.textOutput = Text(master, height=30, width=70, takefocus=0, yscrollcommand=self.scrollbar.set)
		self.scrollbar.config(command=self.textOutput)
		self.textOutput.grid(row=2, column=0, columnspan=70, rowspan=30)
		self.scrollbar.grid(row=2, rowspan=30, column=70, sticky=N+S)

		# Input
		self.inputEntry = Entry(master, width=50, takefocus=1)
		self.inputEntry.grid(row=33, column=0, columnspan=5)
		self.inputEntry.bind('<Return>', self.GetInput)

		self.sendBtn = Button(master, text='Send', command=self.SendCmd)
		self.sendBtn.grid(row=33, column=6)
		self.clearBtn = Button(master, text='Clear', command=self.ClearOutput)
		self.clearBtn.grid(row=33, column=7)

		# Check if user wants a plot of the seral data
		self.plotVar = BooleanVar()
		self.plotVar.set(False)
		self.plotCheck = Checkbutton(master, text='Plot', onvalue=True, offvalue=False, variable=self.plotVar, command=self.LivePlot)
		self.plotCheck.grid(row=33, column=9)

	def GetPorts(self):
		port_list = list_ports.comports()
		ports = [port.device for port in port_list]
		return ports

	def ConnectSerial(self):
		try:
			# if port is open, close it
			if self.ser.is_open:
				self.ser.close()

			self.ser.port = self.portVar.get()
			self.ser.baudrate = self.baudVar.get()
			self.ser.timeout = 0
			self.ser.writeTimeout = 0

			# open port with settings and start reading
			self.ser.open()
			self.textOutput.insert('end', 'Connected to {}, {}\n'.format(self.ser.port, self.ser.baudrate))
			self.ReadSerial()

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))

	def ReadSerial(self):
		try:
			serBuffer = ''
			while self.ser.inWaiting() > 0:
				c = self.ser.read().decode()
				serBuffer += c
			self.textOutput.insert('end', serBuffer)

			# If checkbutton for plot is set, send data to plot function
			if self.plotVar.get() == True and serBuffer != '':
				self.LivePlot(serBuffer.strip())

		except Exception as e:
			self.textOutput.insert('end', e)

		self.master.after(10, self.ReadSerial)


	def GetInput(self, event):
		self.SendCmd()

	def SendCmd(self):
		try:
			command = self.inputEntry.get()
			self.ser.write(command.encode())

		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))

		finally:
			self.inputEntry.delete(0, 'end')

	def ClearOutput(self):
		self.textOutput.delete(1.0, 'end')

	def LivePlot(self, data=''):
		''' 
		Currently only works with 2 numerical comma separated values
		and with enough delay on the arduino 
		'''
		self.plt.ion()
		if data != '':
			x, y = map(float, data.split(','))		
			self.plt.plot(x, y, 'ko')

root = Tk()
gui = SerialMonitorGUI(root)
root.mainloop()