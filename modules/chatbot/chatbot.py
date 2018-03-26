import wx
from wx.lib.pubsub import pub
import sys

class Chatbot(wx.Frame):
    def __init__(self, parent, title):
        super(Chatbot, self).__init__(parent, title=title)
        #pub.subscribe(self.show_data, 'serial.data')

        self.chatbot_panel = wx.Panel(self)
        add_button = wx.Button(self.chatbot_panel, label='Add')
        add_button.Bind(wx.EVT_BUTTON, self.on_add)
        apply_button = wx.Button(self.chatbot_panel, label='Apply')
        apply_button.Bind(wx.EVT_BUTTON, self.on_apply)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add(add_button, 0 , wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.buttonSizer.Add(apply_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.mainSizer.Add(self.buttonSizer)

        self.sizerDict = {}
        self.nbrOfTextSizers = 0

        self.chatbot_panel.SetSizer(self.mainSizer)

        self.Show()
        self.Bind(wx.EVT_CLOSE, self.on_close)


    def on_add(self, event):        
        self.sizerDict["io_text_sizer{0}".format(self.nbrOfTextSizers)] = wx.BoxSizer(wx.HORIZONTAL)
        #print(self.sizerDict['hSizer' + str(self.nbrOfTextSizers)])
        self.sizerDict['io_text_sizer' + str(self.nbrOfTextSizers)].Add(wx.TextCtrl(self.chatbot_panel), 0, wx.ALL, 5)
        self.sizerDict['io_text_sizer' + str(self.nbrOfTextSizers)].Add(wx.TextCtrl(self.chatbot_panel), 0, wx.ALL, 5)
        self.mainSizer.Add(self.sizerDict['io_text_sizer' + str(self.nbrOfTextSizers)])
        self.nbrOfTextSizers += 1
        self.mainSizer.Layout()

    def on_apply(self, event):
        for k, v in self.sizerDict.items():
            children = v.GetChildren()
            for child in children:
                widget = child.GetWindow()
                if isinstance(widget, wx.TextCtrl):
                    print(widget.GetValue())

    def on_close(self, event):
        del sys.modules['modules.chatbot']
        #pub.unsubscribe(self.show_data, 'serial.data')
        event.Skip()

c = Chatbot(None, 'Chatbot')

def on_untick():
    c.Close()