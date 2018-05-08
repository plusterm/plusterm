import wx
# from wx.lib.pubsub import pub
from pubsub import pub
import sys
import re

import wx.lib.inspection

''' The Dynamic_GUI module lets a device send "GUI commands" to dynamically
    draw an interactable GUI.
    '''


class GUI_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(GUI_Panel, self).__init__(*args, **kwargs)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

    def add_button(self):
        name = d.name
        label = d.label

        _new_button = wx.Button(self, label=label)
        _new_button.myname = str(name)
        _new_button.Bind(wx.EVT_BUTTON, self.on_button_click, _new_button)

        self.main_sizer.Add(_new_button)
        self.Layout()

    def show_text(self):
        text = d.name

        _new_text = wx.StaticText(self, label=text)
        self.main_sizer.Add(_new_text)
        self.Layout()

    def on_button_click(self, event):
        ID = event.GetEventObject().myname
        message = 'GUI:event:{}:pressed'.format(ID)
        pub.sendMessage('module.send', data=message)


class Dynamic_GUI(wx.Frame):
    def __init__(self, parent, title):
        super(Dynamic_GUI, self).__init__(
            parent,
            title=title,
            style=wx.DEFAULT_FRAME_STYLE)  # ^ wx.RESIZE_BORDER
        pub.subscribe(self.interpret, 'serial.data')

        self.gui_regex = r'^GUI:(\w+)\(([a-zA-Z0-9\s_]+)(, ([a-zA-Z0-9\s_]+))*\)'
        # '^GUI:(\w+)\((\w+), (\w+)(, (\w+))?\)'

        self.init_ui()

    def init_ui(self):
        self.panel = GUI_Panel(self)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.SetBackgroundColour('lightgray')

        self.Centre()
        self.Show(True)
        wx.lib.inspection.InspectionTool().Show()

    def interpret(self, data):
        d = data[1].decode(errors='ignore').strip()
        # print(d)
        try:
            input_data = re.findall(self.gui_regex, d)
            print(input_data)
            self.command = input_data[0][0]

            self.name = input_data[0][1]  #  if len(input_data[0]) > 2 else ''
            self.label = input_data[0][3]  # if len(input_data[0]) > 2 else input_data[0][1]
            # print(self.label)
            # print(
            #     'Command: ' + self.command,
            #     '\nName: ' + self.name,
            #     '\nLabel: ' + self.label)

            if self.command == 'drawbutton':
                wx.CallAfter(self.panel.add_button)

            elif self.command == 'showtext':
                wx.CallAfter(self.panel.show_text)

        except Exception as e:
            print(e)
        finally:
            self.Update()
            return True

    def on_close(self, event):
        pub.unsubscribe(self.interpret, 'serial.data')
        mod_refs = list(
            filter(lambda m: m.startswith('modules.dynamic_gui'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()


def dispose():
    d.Close()


if __name__ == '__main__':
    app = wx.App()
    d = Dynamic_GUI(None, 'Dynamic GUI')
    app.MainLoop()

else:
    d = Dynamic_GUI(None, 'Dynamic GUI')
