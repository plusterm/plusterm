import wx
# from wx.lib.pubsub import pub
from pubsub import pub
import os
import sys
import communicator

# For GUI debugging
import wx.lib.inspection


class ConnectionSettingsDialog(wx.Dialog):
    ''' A dialog for more advanced connection settings '''

    def __init__(self, *args, **kwargs):
        # Extract and remove gui kw before calling Dialog constructor
        self.gui = kwargs['gui']
        del kwargs['gui']

        super(ConnectionSettingsDialog, self).__init__(*args, **kwargs)

        baudrates_choices = [
            '50', '75', '110', '134',
            '150', '200', '300', '600', '1200', '1800',
            '2400', '4800', '9600', '19200', '38400',
            '57600', '115200']

        device_choices = communicator.getPorts()

        bytesize_choices = ['5', '6', '7', '8']
        parity_choices = ['None', 'Even', 'Odd', 'Mark', 'Space']
        stopbits_choices = ['1', '1.5', '2']

        # Connection type panel
        conn_t_panel = wx.Panel(self)
        conn_choices = ['Serial', 'Socket']
        self.c_type_rb = wx.RadioBox(
            conn_t_panel, label="Connection type", choices=conn_choices)

        conn_t_sizer = wx.BoxSizer()
        conn_t_sizer.Add(self.c_type_rb)
        conn_t_panel.SetSizerAndFit(conn_t_sizer)

        # Serial Panel
        self.ser_panel = wx.Panel(self)
        port_label = wx.StaticText(self.ser_panel, label='Device:')
        baud_label = wx.StaticText(self.ser_panel, label='Baudrate:')
        bytesize_label = wx.StaticText(self.ser_panel, label='Bytesize:')
        parity_label = wx.StaticText(self.ser_panel, label='Parity:')
        stopb_label = wx.StaticText(self.ser_panel, label='Stopbits:')
        self.port_cb = wx.ComboBox(self.ser_panel, choices=device_choices)
        self.baud_cb = wx.ComboBox(self.ser_panel, choices=baudrates_choices)
        self.bytesize_cb = wx.ComboBox(
            self.ser_panel, choices=bytesize_choices)
        self.parity_cb = wx.ComboBox(self.ser_panel, choices=parity_choices)
        self.stopb_cb = wx.ComboBox(self.ser_panel, choices=stopbits_choices)
        ser_conn_button = wx.Button(self.ser_panel, label='Open')

        ser_conn_sizer = wx.GridBagSizer(vgap=5, hgap=5)
        ser_conn_sizer.Add(port_label, pos=(0, 0))
        ser_conn_sizer.Add(self.port_cb, pos=(0, 1))
        ser_conn_sizer.Add(baud_label, pos=(1, 0))
        ser_conn_sizer.Add(self.baud_cb, pos=(1, 1))
        ser_conn_sizer.Add(bytesize_label, pos=(2, 0))
        ser_conn_sizer.Add(self.bytesize_cb, pos=(2, 1))
        ser_conn_sizer.Add(parity_label, pos=(3, 0))
        ser_conn_sizer.Add(self.parity_cb, pos=(3, 1))
        ser_conn_sizer.Add(stopb_label, pos=(4, 0))
        ser_conn_sizer.Add(self.stopb_cb, pos=(4, 1))
        ser_conn_sizer.Add(ser_conn_button, pos=(5, 0))

        self.ser_panel.SetSizerAndFit(ser_conn_sizer)

        # Socket panel
        self.sock_panel = wx.Panel(self)
        host_label = wx.StaticText(self.sock_panel, label='IP/Domain:')
        port_label = wx.StaticText(self.sock_panel, label='Port:')
        self.host_txt = wx.TextCtrl(self.sock_panel, size=(100, 23))
        self.port_txt = wx.TextCtrl(self.sock_panel, size=(100, 23))
        sock_conn_btn = wx.Button(self.sock_panel, label='Connect')

        sock_conn_sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sock_conn_sizer.Add(host_label, pos=(0, 0))
        sock_conn_sizer.Add(self.host_txt, pos=(0, 1))
        sock_conn_sizer.Add(port_label, pos=(1, 0))
        sock_conn_sizer.Add(self.port_txt, pos=(1, 1))
        sock_conn_sizer.Add(sock_conn_btn, pos=(2, 0))

        self.sock_panel.SetSizer(sock_conn_sizer)
        self.sock_panel.Hide()

        # Organize
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(conn_t_panel)
        top_sizer.Add(self.ser_panel, 1, wx.ALL | wx.EXPAND)
        top_sizer.Add(self.sock_panel, 1, wx.ALL | wx.EXPAND)
        self.SetSizerAndFit(top_sizer)

        # Bindings
        self.c_type_rb.Bind(wx.EVT_RADIOBOX, self.toggle_panel)
        ser_conn_button.Bind(wx.EVT_BUTTON, self.connect_serial)
        sock_conn_btn.Bind(wx.EVT_BUTTON, self.connect_socket)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        ''' Close event callback '''
        self.Destroy()

    def toggle_panel(self, event):
        ''' Toggling between connection type '''
        sel = self.c_type_rb.GetSelection()
        if sel == 0:
            self.ser_panel.Show()
            self.sock_panel.Hide()

        elif sel == 1:
            self.sock_panel.Show()
            self.ser_panel.Hide()

        self.Layout()
        self.Fit()

    def connect_socket(self, event):
        ''' Connect to socket callback '''
        c_type = 'socket'
        host = self.host_txt.GetValue()
        port = self.port_txt.GetValue()

        conn = self.gui.connect_socket(
            type=c_type, host=host, port=port)

        if conn:
            self.Destroy()

    def connect_serial(self, event):
        ''' Serial connection callback '''
        c_type = 'serial'
        port = self.port_cb.GetValue()
        baudrate = self.baud_cb.GetValue()
        bytesize = self.bytesize_cb.GetValue()
        parity = self.parity_cb.GetValue()
        stopbits = self.stopb_cb.GetValue()

        conn = self.gui.connect_serial_adv(
            type=c_type,
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits
        )

        if conn:
            self.Destroy()


class SerialMonitorGUI(wx.Frame):
    ''' The main GUI class for Plusterm '''

    def __init__(self, parent, title, context):
        super(SerialMonitorGUI, self).__init__(parent, title=title)

        self.SetBackgroundColour('white')
        # wx.lib.inspection.InspectionTool().Show()

        # Set the context, i.e. SerialMonitor() instance
        self.context = context

        baudrates_choices = [
            '50', '75', '110', '134', '150', '200', '300', '600',
            '1200', '1800', '2400', '4800', '9600', '19200', '38400',
            '57600', '115200']

        device_choices = communicator.getPorts()

        le_choices = ['None', 'CR', 'LF', 'CR+LF']

        self.statusbar = wx.StatusBar(self)
        self.SetStatusBar(self.statusbar)
        self.statusbar.SetStatusText('No connection open')

        # Menubar
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        connect_menu_item = wx.MenuItem(
            file_menu,
            wx.ID_OPEN,
            text='&Connection',
            kind=wx.ITEM_NORMAL,
            helpString='Show advanced connection options')
        file_menu.Append(connect_menu_item)

        self.recent_connections = wx.Menu()
        file_menu.AppendSubMenu(self.recent_connections, text='&History')
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_CLOSE, '&Quit', helpString='Quit Plusterm')

        self.modules_menu = wx.Menu()
        mod_files = [f for f in os.listdir('./modules') if f != '__init__.py']

        for file in mod_files:
            self.modules_menu.Append(
                wx.ID_ANY, file, kind=wx.ITEM_CHECK, helpString='Load script')

        menubar.Append(file_menu, '&File')
        menubar.Append(self.modules_menu, '&Modules')
        self.SetMenuBar(menubar)

        # Widgets and Panels
        panel = wx.Panel(self)
        port_label = wx.StaticText(panel, label='Device:')
        baud_label = wx.StaticText(panel, label='Baudrate:')
        self.port_combobox = wx.ComboBox(panel, choices=device_choices)
        self.baud_combobox = wx.ComboBox(panel, choices=baudrates_choices)
        connect_button = wx.Button(panel, label='Open')
        disconnect_button = wx.Button(panel, label='Close')

        self.output_text = wx.TextCtrl(
            panel, size=(600, 280), style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.output_text.SetBackgroundColour('black')
        self.output_text.SetForegroundColour('white')

        term_font = wx.Font(
            10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.output_text.SetFont(term_font)

        self.input_text = wx.TextCtrl(
            panel, size=(250, 23), style=wx.TE_PROCESS_ENTER)

        self.line_end_combobox = wx.ComboBox(
            panel, choices=le_choices, style=wx.CB_READONLY)
        self.line_end_combobox.SetSelection(3)

        send_button = wx.Button(panel, label='Send')
        clear_button = wx.Button(panel, label='Clear')

        topSizer = wx.BoxSizer(wx.VERTICAL)
        connectionSizer = wx.BoxSizer(wx.HORIZONTAL)
        outputSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputSizer = wx.BoxSizer(wx.HORIZONTAL)

        connectionSizer.Add(
            port_label,
            0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 7)
        connectionSizer.Add(
            self.port_combobox, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 7)
        connectionSizer.Add(
            baud_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 7)
        connectionSizer.Add(
            self.baud_combobox, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 7)

        connectionSizer.AddStretchSpacer(1)
        connectionSizer.Add(connect_button, 0, wx.ALIGN_LEFT, 10)
        connectionSizer.Add(disconnect_button, 0, wx.ALIGN_LEFT, 10)

        outputSizer.Add(self.output_text, 1, wx.EXPAND, 0)

        inputSizer.Add(
            self.input_text, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        inputSizer.AddStretchSpacer(1)
        inputSizer.Add(
            self.line_end_combobox, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        inputSizer.AddStretchSpacer(1)
        inputSizer.Add(send_button, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        inputSizer.Add(clear_button, 0, wx.ALIGN_CENTRE_VERTICAL, 0)

        topSizer.Add(connectionSizer)
        topSizer.Add(outputSizer, 1, wx.ALL | wx.EXPAND)
        topSizer.Add(inputSizer)

        panel.SetSizer(topSizer)
        topSizer.Fit(self)
        self.SetMinSize(self.GetSize())

        # Bindings
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.input_text.Bind(wx.EVT_CHAR, self.on_char_input)
        connect_button.Bind(wx.EVT_BUTTON, self.connect_serial)
        disconnect_button.Bind(wx.EVT_BUTTON, self.disconnect_serial)
        self.line_end_combobox.Bind(wx.EVT_COMBOBOX, self.change_line_end)
        send_button.Bind(wx.EVT_BUTTON, self.on_send)
        clear_button.Bind(wx.EVT_BUTTON, self.clear_output)
        file_menu.Bind(wx.EVT_MENU, self.on_file_menu)
        self.recent_connections.Bind(wx.EVT_MENU, self.re_connect)
        self.Bind(wx.EVT_MENU_OPEN, self.on_open_menu)
        self.modules_menu.Bind(wx.EVT_MENU, self.on_checked_module)

        # Subscribe to data
        pub.subscribe(self.received_data, 'serial.data')
        pub.subscribe(self.received_error, 'serial.error')

        # Line ending when sending command
        self.line_ending = '\r\n'

        # last command, init to empty
        self.last_command = ''

        # Create a timer
        self.timer = wx.Timer(self)

        # Flag to keep track of whether a connection is open
        self.connected = False

    def on_quit(self, event):
        ''' Callback for close event '''
        if self.connected:
            discon = False
            while not discon:
                if self.context.disconnect_serial():
                    discon = True

        del self.timer
        pub.unsubscribe(self.received_data, 'serial.data')
        pub.unsubscribe(self.received_error, 'serial.error')

        for w in wx.GetTopLevelWindows():
            w.Destroy()

        event.Skip()

    def connect_serial(self, event):
        '''Quick connection from main gui '''
        port = self.port_combobox.GetValue()
        baudrate = self.baud_combobox.GetValue()

        if self.connected:
            return

        conn = self.context.connect_serial(
            type='serial',
            port=port,
            baudrate=baudrate,
            bytesize='8',
            parity='None',
            stopbits='1')

        settings = {
            'type': 'serial',
            'port': port,
            'baudrate': baudrate,
            'bytesize': '8',
            'parity': 'None',
            'stopbits': '1'}

        # If connection is successful, start timer that checks for data

        if conn:
            self.connected = True
            wx.CallAfter(self.after_connection, settings=settings)

        self.context.get_error()

    def connect_serial_adv(self, **settings):
        ''' Advanced connection from dialog '''
        if self.connected:
            return

        if self.context.connect_serial(**settings):
            self.connected = True
            wx.CallAfter(self.after_connection, settings=settings)
            return True

        self.context.get_error()
        return False

    def connect_socket(self, **settings):
        ''' Socket connection '''
        if self.connected:
            return

        if self.context.connect_serial(**settings):
            self.Bind(wx.EVT_TIMER, self.check_for_data)
            self.timer.Start()
            self.connected = True
            wx.CallAfter(self.after_connection, settings=settings)
            return True

        self.context.get_error()
        return False

    def after_connection(self, settings):
        ''' After successful connection, add to history in menubar '''
        menu_item = wx.MenuItem(
            self.recent_connections,
            wx.ID_ANY,
            text=str(settings),
            kind=wx.ITEM_NORMAL,
            helpString='Open a recent connection')
        self.recent_connections.Prepend(menu_item)

    def re_connect(self, event):
        item = self.GetMenuBar().FindItemById(event.GetId())
        conn_string = item.GetText()
        settings = eval(conn_string)

        if settings['type'] == 'serial':
            self.connect_serial_adv(**settings)

        elif settings['type'] == 'socket':
            self.connect_socket(**settings)

    def disconnect_serial(self, event):
        ''' Disconnect connection '''
        if self.context.disconnect_serial():
            self.connected = False

    def on_send(self, event):
        ''' Callback for clicking Send button '''
        cmd = self.input_text.GetValue()
        self.output('> ' + cmd + '\n')
        self.last_command = cmd
        self.context.send_serial(cmd)
        self.input_text.Clear()

    def change_line_end(self, event):
        sel = self.line_end_combobox.GetSelection()

        if sel == 0:
            self.line_ending = ''
        elif sel == 1:
            self.line_ending = '\r'
        elif sel == 2:
            self.line_ending = '\n'
        elif sel == 3:
            self.line_ending = '\r\n'

    def on_char_input(self, event):
        k = event.GetKeyCode()

        if k == 315:
            # on key up, show last command
            self.input_text.SetValue(self.last_command)
            return

        elif k == 13:
            # on enter, send command
            self.on_send(wx.EVT_BUTTON)
            return

        event.Skip()

    def check_for_data(self, event):
        ''' Timer event callback, checks periodically for
        data or errors '''
        if self.connected:
            self.context.get_data()
            self.context.get_error()

    def received_data(self, data):
        ''' Pubsub callback for serial.data '''
        try:
            msg = data[1].decode(errors='ignore')
            self.output(msg)

        except TypeError:
            pass

    def received_error(self, data):
        ''' Pubsub callback for serial.error '''
        try:
            err = data[1]
            self.output(err)

        except AttributeError:
            self.output(data)

    def output(self, msg):
        ''' Output to text widget in GUI '''
        self.output_text.AppendText(msg)

    def clear_output(self, event):
        ''' Clear button callback '''
        self.output_text.Clear()

    def on_file_menu(self, event):
        ''' File menu callback '''
        if event.GetId() == wx.ID_OPEN:
            settings = ConnectionSettingsDialog(
                None,
                title='Connection',
                gui=self)
            settings.ShowModal()
            del settings

        elif event.GetId() == wx.ID_CLOSE:
            self.on_quit(event)

    def on_open_menu(self, event):
        ''' When opening menu, check if modules are loaded '''
        for mod in self.modules_menu.GetMenuItems():
            m = 'modules.' + mod.GetLabel()
            if m in sys.modules:
                mod.Check(check=True)
            else:
                mod.Check(check=False)

    def on_checked_module(self, event):
        ''' When a module is checked import it, when unchecked remove it'''
        item = self.GetMenuBar().FindItemById(event.GetId())

        if item.IsChecked():
            self.context.add_module(item.GetText())

        elif not item.IsChecked():
            self.context.remove_module(item.GetText())
