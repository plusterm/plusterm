import wx
from wx.lib.pubsub import pub
import os
import sys
import communicator
import serial

import wx.lib.inspection

class ConnectionSettingsDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):

        self.gui = kwargs['gui']
        del kwargs['gui']
        wx.Dialog.__init__(self, *args, **kwargs)

        baudrates_choices = ['50', '75', '110', '134', 
            '150', '200', '300', '600',  '1200', '1800', 
            '2400', '4800', '9600', '19200', '38400', 
            '57600', '115200']

        device_choices = communicator.getPorts()

        bytesize_choices = ['5', '6', '7', '8']
        parity_choices = ['None', 'Even', 'Odd', 'Mark', 'Space']
        stopbits_choices = ['1', '1.5', '2']

        ser_panel = wx.Panel(self)
        port_label = wx.StaticText(ser_panel, label='Device:')
        baud_label = wx.StaticText(ser_panel, label='Baudrate:')
        bytesize_label = wx.StaticText(ser_panel, label='Bytesize:')
        parity_label = wx.StaticText(ser_panel, label='Parity:')
        stopb_label = wx.StaticText(ser_panel, label='Stopbits:')
        self.port_cb = wx.ComboBox(ser_panel, choices=device_choices)
        self.baud_cb = wx.ComboBox(ser_panel, choices=baudrates_choices)
        self.bytesize_cb = wx.ComboBox(ser_panel, choices=bytesize_choices)
        self.parity_cb = wx.ComboBox(ser_panel, choices=parity_choices)
        self.stopb_cb = wx.ComboBox(ser_panel, choices=stopbits_choices)
        connect_button = wx.Button(ser_panel, label='Open')

        ser_conn_sizer = wx.GridBagSizer(vgap=5, hgap=5)
        ser_conn_sizer.Add(port_label, pos=(0,0))
        ser_conn_sizer.Add(self.port_cb, pos=(0,1))

        ser_conn_sizer.Add(baud_label, pos=(1,0))
        ser_conn_sizer.Add(self.baud_cb, pos=(1,1))

        ser_conn_sizer.Add(bytesize_label, pos=(2,0))
        ser_conn_sizer.Add(self.bytesize_cb, pos=(2,1))

        ser_conn_sizer.Add(parity_label, pos=(3,0))
        ser_conn_sizer.Add(self.parity_cb, pos=(3,1))

        ser_conn_sizer.Add(stopb_label, pos=(4,0))
        ser_conn_sizer.Add(self.stopb_cb, pos=(4,1))

        ser_conn_sizer.Add(connect_button, pos=(5,0))

        ser_panel.SetSizerAndFit(ser_conn_sizer)

        connect_button.Bind(wx.EVT_BUTTON, self.connect_serial)
        self.Bind(wx.EVT_CLOSE, self.on_close)


    def on_close(self, event):
        self.Destroy()


    def connect_serial(self, event):
        port = self.port_cb.GetValue()
        baudrate = self.baud_cb.GetValue()
        bytesize = self.bytesize_cb.GetValue()
        parity = self.parity_cb.GetValue()
        stopbits = self.stopb_cb.GetValue()

        bytesize_dict = {
            '': serial.EIGHTBITS,
            '5': serial.FIVEBITS,
            '6': serial.SIXBITS,
            '7': serial.SEVENBITS,
            '8': serial.EIGHTBITS
        }

        parity_dict = {
            '': serial.PARITY_NONE,
            'None': serial.PARITY_NONE,
            'Even': serial.PARITY_EVEN,
            'Odd': serial.PARITY_ODD,
            'Mark': serial.PARITY_MARK,
            'Space': serial.PARITY_SPACE
        } 

        stopb_dict = {
            '': serial.STOPBITS_ONE,
            '1': serial.STOPBITS_ONE,
            '1.5': serial.STOPBITS_ONE_POINT_FIVE,
            '2': serial.STOPBITS_TWO
        }
        
        conn = self.gui.connect_serial_adv(
            port=port, 
            baudrate=baudrate,
            bytesize=bytesize_dict[bytesize],
            parity=parity_dict[parity],
            stopbits=stopb_dict[stopbits]
        )

        if conn:
            self.Destroy()


class SerialMonitorGUI(wx.Frame):   
    def __init__(self, parent, title, context):
        super(SerialMonitorGUI, self).__init__(parent, title=title)

        self.SetBackgroundColour('white')
        # wx.lib.inspection.InspectionTool().Show()

        # Set the context, i.e. SerialMonitor() instance
        self.context = context

        baudrates_choices = ['50', '75', '110', '134', '150', '200', '300', '600', 
                            '1200', '1800', '2400', '4800', '9600', '19200', '38400', 
                            '57600', '115200']

        device_choices = communicator.getPorts()

        ### Menubar
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        connect_menu_item = wx.MenuItem(
            file_menu, 
            wx.ID_OPEN, 
            text='&Connection Settings',
            kind=wx.ITEM_NORMAL)
        file_menu.Append(connect_menu_item)

        self.modules_menu = wx.Menu()
        module_files = [f for f in os.listdir('./modules') if f not in ['__pycache__', '__init__.py']]
        
        for file in module_files:
            self.modules_menu.Append(wx.ID_ANY, file, kind=wx.ITEM_CHECK)

        menubar.Append(file_menu, '&File')
        menubar.Append(self.modules_menu, '&Modules')
        self.SetMenuBar(menubar)

        ### Widgets and Panels
        panel = wx.Panel(self)
        port_label = wx.StaticText(panel, label='Device:')
        baud_label = wx.StaticText(panel, label='Baudrate:')
        self.port_combobox = wx.ComboBox(panel, choices=device_choices)
        self.baud_combobox = wx.ComboBox(panel, choices=baudrates_choices)
        connect_button = wx.Button(panel, label='Open')
        disconnect_button = wx.Button(panel, label='Close')
        
        self.output_text = wx.TextCtrl(panel, size=[600,300], style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.input_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)

        send_button = wx.Button(panel, label='Send')
        clear_button = wx.Button(panel, label='Clear')

        topSizer = wx.BoxSizer(wx.VERTICAL)
        connectionSizer = wx.BoxSizer(wx.HORIZONTAL)
        outputSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputSizer = wx.BoxSizer(wx.HORIZONTAL)

        connectionSizer.Add(port_label, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 7)
        connectionSizer.Add(self.port_combobox, 0, wx.RIGHT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 7)
        connectionSizer.Add(baud_label, 0, wx.RIGHT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 7)
        connectionSizer.Add(self.baud_combobox, 0, wx.RIGHT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 7)
        
        connectionSizer.AddStretchSpacer(1) 
        connectionSizer.Add(connect_button, 0, wx.ALIGN_LEFT, 10)
        connectionSizer.Add(disconnect_button, 0, wx.ALIGN_LEFT, 10)

        outputSizer.Add(self.output_text, 1, wx.EXPAND, 0)

        inputSizer.Add(self.input_text, 0, 0, 0)
        inputSizer.AddStretchSpacer(1)
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
        file_menu.Bind(wx.EVT_MENU, self.on_file_menu)   
        self.Bind(wx.EVT_MENU_OPEN, self.on_open_menu)
        self.modules_menu.Bind(wx.EVT_MENU, self.on_checked_module)

        # Subscribe to data
        pub.subscribe(self.received_data, 'serial.data')
        pub.subscribe(self.recieved_error, 'serial.error')

        # Create a timer
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

        conn = self.context.connect_serial(
                port=port, 
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE)

        # If connection is successful, start timer that checks for data
        if conn:
            self.Bind(wx.EVT_TIMER, self.check_for_serialdata)
            self.timer.Start()


    def connect_serial_adv(self, **settings):
        # If connection is successful, start timer that checks for data
        if self.context.connect_serial(**settings):    
            print('done')           
            self.Bind(wx.EVT_TIMER, self.check_for_serialdata)
            self.timer.Start()
            return True
        return False


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


    def on_file_menu(self, event):
        if event.GetId() == wx.ID_OPEN:
            settings = ConnectionSettingsDialog(
                None,  
                title='Connection',
                gui=self)
            settings.ShowModal()


    def on_open_menu(self, event):
        for mod in self.modules_menu.GetMenuItems():
            m = 'modules.' + mod.GetLabel()
            if m in sys.modules:
                mod.Check(check=True)
            else:
                mod.Check(check=False)


    def on_checked_module(self, event):
        ''' Checks which modules are checked or not
        Adds or remove modules'''
        for i in self.modules_menu.GetMenuItems():
            if i.IsChecked():
                self.context.add_module(i.GetLabel())

            elif not i.IsChecked():
                self.context.remove_module(i.GetLabel())