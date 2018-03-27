import wx
from wx.lib.pubsub import pub
import sys

class Chatbot(wx.Frame):
    def __init__(self, parent, title):
        super(Chatbot, self).__init__(parent, title=title)
        pub.subscribe(self.chat, 'serial.data')

        self.chatbot_panel = wx.Panel(self)
        add_button = wx.Button(self.chatbot_panel, label='Add')
        add_button.Bind(wx.EVT_BUTTON, self.on_add)
        apply_button = wx.Button(self.chatbot_panel, label='Apply')
        apply_button.Bind(wx.EVT_BUTTON, self.on_apply)
        clear_button = wx.Button(self.chatbot_panel, label='Clear')
        clear_button.Bind(wx.EVT_BUTTON, self.on_clear)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add(add_button, 0 , wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.buttonSizer.Add(apply_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.buttonSizer.Add(clear_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.mainSizer.Add(self.buttonSizer)

        self.sizerDict = {}
        self.nbrOfTextSizers = 0

        self.testDict = {}
        self.first = True

        self.chatbot_panel.SetSizer(self.mainSizer)

        self.Show()
        self.Bind(wx.EVT_CLOSE, self.on_close)

    #Here we generate new sizers and add textctrls to them.
    #It looks like hot garbage but I haven't figured out a better way to do it yet.
    def on_add(self, event):        
        self.sizerDict["io_box_sizer{0}".format(self.nbrOfTextSizers)] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerDict['io_box_sizer' + str(self.nbrOfTextSizers)].Add(wx.TextCtrl(self.chatbot_panel), 0, wx.ALL, 5)
        self.sizerDict['io_box_sizer' + str(self.nbrOfTextSizers)].Add(wx.TextCtrl(self.chatbot_panel), 0, wx.ALL, 5)
        self.mainSizer.Add(self.sizerDict['io_box_sizer' + str(self.nbrOfTextSizers)])
        self.nbrOfTextSizers += 1
        self.mainSizer.Layout()
        print(self.mainSizer.GetChildren())

    #Search through all of the textctrls and generate a dict with corresponding I/O.
    def on_apply(self, event):
        self.testDict.clear()
        for k, v in self.sizerDict.items():
            sizerContent = v.GetChildren()
            self.first = True
            for content in sizerContent:
                element = content.GetWindow()
                if isinstance(element, wx.TextCtrl) & self.first:
                    #print("input: " + element.GetValue())
                    dictinput = element.GetValue()
                    self.first = False
                elif isinstance(element, wx.TextCtrl) & self.first is False:
                    #print("output: " + element.GetValue())
                    dictoutput = element.GetValue()
                    self.testDict[dictinput] = dictoutput
        for key, value in self.testDict.items():
            print(key, value)


    # Search through all of the textctrls and clear them.
    def on_clear(self, event):
        #print("nbr: {}".format(self.nbrOfTextSizers))
        for i in range(self.nbrOfTextSizers, 0, -1):
            print(i)
            self.mainSizer.Hide(index=i)
            self.mainSizer.Remove(index=i)

        self.sizerDict.clear()
        self.nbrOfTextSizers = 0
        print(self.mainSizer.GetChildren())
        self.mainSizer.Layout()

        '''
        for k, v in self.sizerDict.items():
            sizerContent = v.GetChildren()
            for content in sizerContent:
                element = content.GetWindow()
                if isinstance(element, wx.TextCtrl):
                    element.Clear()
        '''
    def chat(self, data):
        #print(data[1].decode(errors='ignore'))
        r = data[1].decode(errors='ignore').strip()
        if r in self.testDict:
            print(r, self.testDict[r])
            s = self.testDict[r]
            pub.sendMessage('module.send', data=s)


    def on_close(self, event):
        del sys.modules['modules.chatbot']
        pub.unsubscribe(self.chat, 'serial.data')
        event.Skip()

c = Chatbot(None, 'Chatbot')

def on_untick():
    c.Close()