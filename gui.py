import wx
from wx.lib.pubsub import pub
import os
import sys
import communicator

import wx.lib.inspection

class SerialMonitorGUI(wx.Frame):   
    def __init__(self, parent, title, context):
        super(SerialMonitorGUI, self).__init__(parent, title=title)

        self.SetBackgroundColour('white')
        wx.lib.inspection.InspectionTool().Show()

        # Set the context, i.e. SerialMonitor() instance
        self.context = context

        baudrates_choices = ['50', '75', '110', '134', '150', '200', '300', '600', 
                            '1200', '1800', '2400', '4800', '9600', '19200', '38400', 
                            '57600', '115200']

        device_choices = communicator.getPorts()

        ### Menubar
        menubar = wx.MenuBar()
        self.modules_menu = wx.Menu()

        module_files = [f for f in os.listdir('./modules') if f not in ['__pycache__', '__init__.py']]
        for file in module_files:
            self.modules_menu.Append(wx.ID_ANY, file, kind=wx.ITEM_CHECK)

        menubar.Append(self.modules_menu, '&Modules')
        self.SetMenuBar(menubar)

        ### Widgets and Panels
        panel = wx.Panel(self)
        port_label = wx.StaticText(panel, label=' Device:    ')
        baud_label = wx.StaticText(panel, label=' Baudrate:    ')
        self.port_combobox = wx.ComboBox(panel, choices=device_choices)
        self.baud_combobox = wx.ComboBox(panel, choices=baudrates_choices)
        connect_button = wx.Button(panel, label='Open')
        disconnect_button = wx.Button(panel, label='Close')
        
        self.output_text = wx.TextCtrl(panel, size=[500,300], style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.input_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)

        send_button = wx.Button(panel, label='Send')
        clear_button = wx.Button(panel, label='Clear')

        topSizer = wx.BoxSizer(wx.VERTICAL)
        connectionSizer = wx.BoxSizer(wx.HORIZONTAL)
        outputSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputSizer = wx.BoxSizer(wx.HORIZONTAL)

        connectionSizer.Add(port_label, 0, 0, 0)
        connectionSizer.Add(self.port_combobox, 0, 0, 0)
        connectionSizer.Add(baud_label, 0, 0, 0)
        connectionSizer.Add(self.baud_combobox, 0, 0, 0)
        connectionSizer.Add(connect_button, 0, 0, 0)
        connectionSizer.Add(disconnect_button, 0, 0, 0)

        outputSizer.Add(self.output_text, 1, wx.EXPAND, 0)

        inputSizer.Add(self.input_text, 0, 0, 0)
        inputSizer.Add(send_button, 0, 0, 0)
        inputSizer.Add(clear_button, 0, 0, 0)

        topSizer.Add(connectionSizer)
        topSizer.Add(outputSizer, 1, wx.EXPAND)
        topSizer.Add(inputSizer)

        panel.SetSizer(topSizer)
        topSizer.Fit(self)
        self.SetMinSize(self.GetSize())
        
        ### Bindings
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.input_text.Bind(wx.EVT_TEXT_ENTER, self.on_enter_send)
        connect_button.Bind(wx.EVT_BUTTON, self.connect_serial)
        disconnect_button.Bind(wx.EVT_BUTTON, self.disconnect_serial)
        send_button.Bind(wx.EVT_BUTTON, self.on_send)
        clear_button.Bind(wx.EVT_BUTTON, self.clear_output)     
        self.modules_menu.Bind(wx.EVT_MENU, self.on_checked_module)
        self.Bind(wx.EVT_MENU_OPEN, self.on_open_menu)

        # Subscribe to data
        pub.subscribe(self.received_data, 'serial.data')
        pub.subscribe(self.recieved_error, 'serial.error')
        self.timer = wx.Timer(self)


    def on_quit(self, event):
        del self.timer
        self.context.disconnect_serial()
        pub.unsubscribe(self.received_data, 'serial.data')
        event.Skip()


    def on_enter_send(self, event):
        self.on_send(wx.EVT_BUTTON)


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
        self.output('> ' + cmd + '\n')
        self.context.send_serial(cmd)
        self.input_text.Clear()


    def check_for_serialdata(self, event):
        self.context.get_data()
        self.context.get_error()        


    def received_data(self, data):
        msg = data[1].decode(errors='replace')
        self.output(msg)


    def recieved_error(self, data):
        err = data[1]
        self.output(err)

    
    def output(self, msg):
        self.output_text.AppendText(msg)


    def clear_output(self, event):
        self.output_text.Clear()


    def on_open_menu(self, event):
        for mod in self.modules_menu.GetMenuItems():
            m = 'modules.' + mod.GetLabel()
            if m in sys.modules:
                mod.Check(check=True)
            else:
                mod.Check(check=False)


    def on_checked_module(self, event):
        items = self.modules_menu.GetMenuItems()
        for i in items:
            if i.IsChecked():
                self.context.add_module(i.GetLabel())

            elif not i.IsChecked():
                self.context.remove_module(i.GetLabel())