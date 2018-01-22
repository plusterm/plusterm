import wx
from wx.lib.pubsub import pub
import os
import communicator

class SerialMonitorGUI(wx.Frame):	
	def __init__(self, parent, title, context):
		super(SerialMonitorGUI, self).__init__(parent, title=title)

		self.SetBackgroundColour('white')

		# Setr the context, i.e. SerialMonitor() instance
		self.context = context

		baudrates_choices = ['50', '75', '110', '134', '150', '200', '300', '600', 
							'1200', '1800', '2400', '4800', '9600', '19200', '38400', 
							'57600', '115200']


		device_choices = communicator.getPorts()

		### Widgets and Panels
		settingsPanel = wx.Panel(self)
		port_label = wx.StaticText(settingsPanel, label='Device:')
		baud_label = wx.StaticText(settingsPanel, label='Baudrate')
		self.port_combobox = wx.ComboBox(settingsPanel, choices=device_choices)
		self.baud_combobox = wx.ComboBox(settingsPanel, choices=baudrates_choices)
		connect_button = wx.Button(settingsPanel, label='Open')
		disconnect_button = wx.Button(settingsPanel, label='Close')

		outputPanel = wx.Panel(self)
		self.output_text = wx.TextCtrl(outputPanel, size=(300,500), style=wx.TE_MULTILINE)

		inputPanel = wx.Panel(self)
		self.input_text = wx.TextCtrl(inputPanel)
		send_button = wx.Button(inputPanel, label='Send')
		clear_button = wx.Button(inputPanel, label='Clear')

		### Sizers
		settings_sizer = wx.GridBagSizer(vgap=5, hgap=5)
		output_sizer = wx.BoxSizer()
		input_sizer = wx.GridBagSizer(vgap=5, hgap=5)
		main_sizer = wx.GridBagSizer(vgap=5, hgap=5)

		settings_sizer.Add(port_label, pos=(0,1))
		settings_sizer.Add(self.port_combobox, pos=(0,2))
		settings_sizer.Add(baud_label, pos=(0,3))
		settings_sizer.Add(self.baud_combobox, pos=(0,4))
		settings_sizer.Add(connect_button, pos=(0,9))
		settings_sizer.Add(disconnect_button, pos=(0,10))

		output_sizer.Add(self.output_text, 1, wx.EXPAND)

		input_sizer.Add(self.input_text, pos=(0,0))
		input_sizer.Add(send_button, pos=(0,1))
		input_sizer.Add(clear_button, pos=(0,2))

		main_sizer.Add(settings_sizer, pos=(0,0))
		main_sizer.Add(output_sizer, pos=(1,0), flag= wx.ALL | wx.EXPAND)
		main_sizer.AddGrowableCol(0)
		main_sizer.AddGrowableRow(1)
		main_sizer.Add(inputPanel, pos=(2,0))

		### Set sizers
		settingsPanel.SetSizerAndFit(settings_sizer)
		outputPanel.SetSizerAndFit(output_sizer)
		inputPanel.SetSizerAndFit(input_sizer)

		### Menubar
		menubar = wx.MenuBar()
		self.modules_menu = wx.Menu()

		module_files = [f for f in os.listdir('./modules') if f not in ['__pycache__', '__init__.py']]
		for file in module_files:
			self.modules_menu.Append(wx.ID_ANY, file, kind=wx.ITEM_CHECK)

		menubar.Append(self.modules_menu, '&Modules')
		self.SetMenuBar(menubar)

		### Bindings
		self.Bind(wx.EVT_CLOSE, self.on_quit)
		connect_button.Bind(wx.EVT_BUTTON, self.connect_serial)
		disconnect_button.Bind(wx.EVT_BUTTON, self.disconnect_serial)
		send_button.Bind(wx.EVT_BUTTON, self.on_send)
		clear_button.Bind(wx.EVT_BUTTON, self.clear_output)
		self.modules_menu.Bind(wx.EVT_MENU, self.on_checked_module)

		# Subscribe to data
		pub.subscribe(self.received_data, 'serial.data')

		# Size and show		
		self.timer = wx.Timer(self)
		self.SetSizerAndFit(main_sizer)
		self.Show()


	def on_quit(self, event):	
		self.context.on_quit()
		del self.timer
		event.Skip()


	def connect_serial(self, event):
		port = self.port_combobox.GetValue()
		baudrate = self.baud_combobox.GetValue()
		# If connection is successful, start timer that checks for data
		if self.context.connect_serial(port=port, baudrate=baudrate):				
			self.Bind(wx.EVT_TIMER, self.check_for_serialdata)
			self.timer.Start()	


	def disconnect_serial(self, event):
		self.context.disconnect_serial()


	def on_send(self, event):
		cmd = self.input_text.GetValue()
		self.context.send_serial(cmd)
		self.input_text.Clear()


	def check_for_serialdata(self, event):
		self.context.get_data()


	def received_data(self, data):
		msg = data[1].decode(errors='replace')
		self.output(msg)

	
	def output(self, msg):
		self.output_text.AppendText(msg)


	def clear_output(self, event):
		self.output_text.Clear()


	def on_checked_module(self, event):
		items = self.modules_menu.GetMenuItems()
		for i in items:
			if i.IsChecked():
				self.context.add_module(i.GetLabel())