import wx
from wx.lib.pubsub import pub
import sys

class Chatbot(wx.Frame):
    def __init__(self, parent, title):
        super(Chatbot, self).__init__(parent, title=title)
        pub.subscribe(self.chat, 'serial.data')

        self.SetBackgroundColour('white')

        # Settings panel
        self.settings_panel = wx.Panel(self)
        add_button = wx.Button(self.settings_panel, label='Add')
        add_button.Bind(wx.EVT_BUTTON, self.on_add)
        apply_button = wx.Button(self.settings_panel, label='Apply')
        apply_button.Bind(wx.EVT_BUTTON, self.on_apply)
        clear_button = wx.Button(self.settings_panel, label='Clear')
        clear_button.Bind(wx.EVT_BUTTON, self.on_clear)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add(add_button, 0 , wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.buttonSizer.Add(apply_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.buttonSizer.Add(clear_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
       
        self.settings_panel.SetSizer(self.buttonSizer)

        # Chatbot panel
        self.chatbot_panel = wx.Panel(self)
        self.chatbot_sizer = wx.BoxSizer(wx.VERTICAL)
        self.chatbot_panel.SetSizer(self.chatbot_sizer)

        # Main sizer
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.settings_panel)
        self.mainSizer.Add(self.chatbot_panel)
        self.SetSizerAndFit(self.mainSizer)

        self.sizerLst = []
        self.responses = {}

        self.Show()
        self.Bind(wx.EVT_CLOSE, self.on_close)


    def on_add(self, event):
        ''' Add new textboxes '''
        new_sizer = wx.BoxSizer(wx.HORIZONTAL)
        new_sizer.Add(wx.TextCtrl(self.chatbot_panel), 0, wx.ALL, 5)
        new_sizer.Add(wx.TextCtrl(self.chatbot_panel), 0, wx.ALL, 5)
        self.sizerLst.append(new_sizer)
        self.chatbot_sizer.Add(new_sizer)
        self.Layout()
        self.Fit()


    def on_apply(self, event):
        ''' Search through all of the textctrls and 
        generate a dict with corresponding I/O.'''
        for sizer in self.sizerLst:            
            vals = []
            for child in sizer.GetChildren():
                w = child.GetWindow()
                if isinstance(w, wx.TextCtrl):
                    vals.append(w.GetValue())

            if len(vals) == 2:
                self.responses[vals[0]] = vals[1]
            

    def on_clear(self, event):
        ''' Search through all of the textctrls and clear them. '''
        self.responses.clear()
        for i in range(len(self.sizerLst), 0, -1):
            self.chatbot_sizer.Hide(index=i-1)
            self.chatbot_sizer.Remove(index=i-1)
        self.sizerLst[:] = []
        self.Layout()
        self.Fit()


    def chat(self, data):
        r = data[1].decode(errors='ignore').strip()
        if r in self.responses:
            print(r, self.responses[r])
            s = self.responses[r]
            pub.sendMessage('module.send', data=s)


    def on_close(self, event):
        pub.unsubscribe(self.chat, 'serial.data')
        mod_refs = list(
            filter(lambda m: m.startswith('modules.chatbot'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()


def dispose():
    c.Close()

if __name__ == '__main__':
    app = wx.App()
    c = Chatbot(None, 'Chatbot')
    app.MainLoop()

else:
    c = Chatbot(None, 'Chatbot')