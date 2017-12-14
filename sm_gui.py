from tkinter import *
from tkinter.filedialog import askopenfile


from communicator import getPorts

class sm_gui(object):
	"""docstring for sm_gui"""
	def __init__(self,master,context):
		self.context=context
		self.master = master
		master.title("Serial Monitor")
		master.protocol('WM_DELETE_WINDOW', self.context.onQuit)
		master.resizable(0,0)
	
		self.portVar = StringVar()
		self.baudVar = StringVar()
		self.plotVar = BooleanVar()
		self.repeatVar = BooleanVar()

		self.portVar.set('Custom')
		self.baudVar.set('Custom')
		self.repeatVar.set(False)
		self.plotVar.set(False)

		self.cmdList = list()

		self.portChoices = getPorts()
		self.baudratesList = [50, 75, 110, 134, 150, 200, 300, 600, 
							1200, 1800, 2400, 4800, 9600, 19200, 38400, 
							57600, 115200, 'Custom']

		self.menu = Menu(master)
		self.master.config(menu=self.menu)

		self.file = Menu(self.menu, tearoff=0)
		self.file.add_command(label = 'Quit', underline=0, command=self.context.onQuit)
		self.menu.add_cascade(label = 'File', underline=0, menu=self.file)

		self.script = Menu(self.menu, tearoff=0)
		self.script.add_command(label = 'Run', underline=0, command=self.openScriptFile)
		self.menu.add_cascade(label = 'Script', underline=0, menu=self.script)

		# Connection settings
		settingsFrame = Frame(master)
		self.portLabel = Label(settingsFrame, text='Device:')
		self.popupMenuPort = OptionMenu(settingsFrame, self.portVar, *self.portChoices)
		self.customPortEntry = Entry(settingsFrame, width=10)
		self.baudLabel = Label(settingsFrame, text='     Baudrate:')
		self.popupMenuBaud = OptionMenu(settingsFrame, self.baudVar, *self.baudratesList)
		self.customBaudEntry = Entry(settingsFrame, width=10)
		self.connectBtn = Button(settingsFrame, text='Open', command=self.connect)
		self.disconnectBtn = Button(settingsFrame, text='Close', command=self.disconnect)

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
			variable=self.plotVar, command=self.context.setupPlot)

		# Repeat commanda
		self.repeatCheck = Checkbutton(inputFrame, text='Repeat:', onvalue=True, offvalue=False, 
			variable=self.repeatVar, command=self.repeatMode)
		self.repeatEntry = Entry(inputFrame, width=10)

		self.inputEntry.pack(side='left')
		self.sendBtn.pack(side='left')
		self.clearBtn.pack(side='left')
		self.repeatEntry.pack(side='right', padx=17, ipadx=0)
		self.repeatCheck.pack(side='right')
		self.plotCheck.pack(side='left')
		inputFrame.grid(row=2, column=0, sticky=NSEW)

	def logoutput(self,data):
		self.textOutput.insert('end', data)
		self.textOutput.see('end')	#	scroll down to last entry

	def clearOutput(self):
		# clears the output text widget
		self.textOutput.delete(1.0, 'end')

	def clearinputentry(self):
		# Clear the entry widget, add save the last command
		self.inputEntry.delete(0, 'end')

	def savecommand(self,cmd):
		self.cmdList.append(cmd)

		# only save the 10 latest commands
		if len(self.cmdList) > 10:
			self.cmdList.pop(0)

		self.cmdPointer = len(self.cmdList)
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
		self.context.sendCmd(cmd)


	def onSendClick(self):
		cmd = self.inputEntry.get()
		self.context.sendCmd(cmd)
					

	def repeatMode(self):
		# Repeat sends a command, by default evey 500 ms
		# Specify time limit with a comma, e.g. 'c, 100' in ms
		try:
			inp = self.repeatEntry.get().split(',')

			if len(inp) == 1:
				self.context.sendCmd(inp[0])
				timer = 500

			elif len(inp) == 2:
				self.context.sendCmd(inp[0])

				if int(inp[1]) <= 0:
					timer = 500
				else:
					timer = int(inp[1])

			# repeat
			if self.repeatVar.get() == True:
				try:
					self.master.after(timer, self.repeatMode)
				except:
					pass

		except Exception as e:
			self.logoutput('{}\n'.format(e))

	def listenComThread(self):
		self.context.getdata()
		# check again (unless program is quitting)
		try:
			self.master.after(10, self.listenComThread)	
		except:
			pass

	def connect(self):
		self.context.connectSerial()
		self.master.after(100,self.listenComThread)

	def disconnect(self):
		self.context.disconnectSerial()

	def openScriptFile(self):
		file = askopenfile(filetypes =(("Text File", "*.txt"),("All Files","*.*")),
							title = "Choose a file")
		try:
			f = open(file.name, 'r')
			text = f.read()
			f.close()
			self.context.sendScript(text)
				
		except Exception as e:
			self.logoutput('{}\n'.format(e))
