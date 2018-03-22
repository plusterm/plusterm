import wx
from wx.lib.pubsub import pub
import os
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
        port_label = wx.StaticText(panel, label='Device:')
        baud_label = wx.StaticText(panel, label='Baudrate')
        self.port_combobox = wx.ComboBox(panel, choices=device_choices)
        self.baud_combobox = wx.ComboBox(panel, choices=baudrates_choices)
        connect_button = wx.Button(panel, label='Open')
        disconnect_button = wx.Button(panel, label='Close')
        
        self.output_text = wx.TextCtrl(panel, size=(500,400), style=wx.TE_READONLY | wx.TE_MULTILINE)
        
        self.input_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        send_button = wx.Button(panel, label='Send')
        clear_button = wx.Button(panel, label='Clear')

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        box = wx.BoxSizer()

        sizer.Add(port_label, pos=(0,0))
        sizer.Add(self.port_combobox, pos=(0,1))
        sizer.Add(baud_label, pos=(0,2))
        sizer.Add(self.baud_combobox, pos=(0,3))
        sizer.Add(connect_button, pos=(0,9))
        sizer.Add(disconnect_button, pos=(0,10))

        sizer.Add(self.output_text, pos=(1,0), span=(1,20))

        sizer.Add(self.input_text, pos=(2,0))
        sizer.Add(send_button, pos=(2,1))
        sizer.Add(clear_button, pos=(2,2))

        box.Add(panel)

        panel.SetSizerAndFit(sizer)
        self.SetSizerAndFit(box)


        ### Bindings
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.input_text.Bind(wx.EVT_TEXT_ENTER, self.on_enter_send)
        connect_button.Bind(wx.EVT_BUTTON, self.connect_serial)
        disconnect_button.Bind(wx.EVT_BUTTON, self.disconnect_serial)
        send_button.Bind(wx.EVT_BUTTON, self.on_send)
        clear_button.Bind(wx.EVT_BUTTON, self.clear_output)     
        self.modules_menu.Bind(wx.EVT_MENU, self.on_checked_module)

        # Subscribe to data
        pub.subscribe(self.received_data, 'serial.data')
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