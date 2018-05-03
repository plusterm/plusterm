import wx
# from wx.lib.pubsub import pub
from pubsub import pub
import exrex
import sys

''' Requires the "exrex" library. "python -m pip install exrex".

    This module uses a user defined regex to generate matching strings
    and allows the user to then spam said strings to hardware with a
    customizable frequency.
    '''


class RandomSpam(wx.Frame):
    def __init__(self, parent, title):
        super(RandomSpam, self).__init__(
            parent,
            title=title,
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        self.spamming = False
        self.delay = 0
        self.spam_timer = wx.Timer()
        self.spam_timer.Bind(wx.EVT_TIMER, self.spam)

        self.init_ui()

    def init_ui(self):
        text_panel = wx.Panel(self)
        text_sizer = wx.BoxSizer(wx.VERTICAL)

        delay_panel = wx.Panel(self)
        delay_sizer = wx.BoxSizer(wx.HORIZONTAL)

        button_panel = wx.Panel(self)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        example = 'val1=-{0,1}[\d]{1,2}[VAΩ](, val2=-{0,1}[\d]([VAΩ]|Hz)){0,1}'
        self.regex_tb = wx.TextCtrl(
            text_panel,
            size=(425, 22),
            value=example)
        regex_font = wx.Font(
            10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.regex_tb.SetFont(regex_font)

        self.preview_st = wx.StaticText(
            text_panel,
            label='Preview: ' + exrex.getone(example))

        text_sizer.Add(self.regex_tb)
        text_sizer.Add(self.preview_st, 0, wx.TOP, 7)
        text_sizer.AddSpacer(5)

        self.delay_tc = wx.TextCtrl(
            delay_panel,
            size=(40, 20))
        self.delay_tc.SetValue('0')

        delay_st = wx.StaticText(
            delay_panel,
            label='  Delay in milliseconds')

        delay_sizer.Add(self.delay_tc, 0, wx.ALIGN_CENTER_VERTICAL)
        delay_sizer.Add(delay_st, 0, wx.ALIGN_CENTER_VERTICAL)

        self.preview_button = wx.Button(
            button_panel,
            label='Preview',
            size=(210, 25))
        self.preview_button.Bind(wx.EVT_BUTTON, self.on_preview_button)

        self.spam_button = wx.Button(
            button_panel,
            label='Spam',
            size=(215, 25))
        self.spam_button.Bind(wx.EVT_BUTTON, self.on_spam_button)

        button_sizer.Add(self.preview_button)
        button_sizer.Add(self.spam_button)

        text_panel.SetSizer(text_sizer)
        delay_panel.SetSizer(delay_sizer)
        button_panel.SetSizer(button_sizer)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(text_panel, 0, wx.EXPAND | wx.ALL, 7)
        main_sizer.Add(delay_panel, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT, 7)
        main_sizer.Add(button_panel, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT, 5)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.SetSizer(main_sizer)
        self.Fit()
        self.SetMinSize(self.GetBestSize())
        self.SetMaxSize(self.GetBestSize())
        self.SetBackgroundColour('lightgray')
        self.Centre()

        self.Show(True)

    def spam(self, event):
        try:
            message = exrex.getone(self.regex_tb.GetValue())
            pub.sendMessage('module.send', data=message)
        except Exception:
            self.preview_st.SetLabel('Invalid regex.')
            self.spamming = False
            self.spam_button.SetLabel(self.button_label)

    def on_spam_button(self, event):
        try:
            self.delay = int(self.delay_tc.GetValue())
        except Exception:
            print('weird delay?')
        # print(self.delay)
        if not self.spamming:
            self.spamming = True
            if self.delay > 0:
                self.spam_timer.Start(self.delay)
            else:
                self.spam_timer.Start(0)
        else:
            self.spamming = False
            self.spam_timer.Stop()

        self.button_label = 'Spam' if not self.spamming else 'Stop'
        self.spam_button.SetLabel(self.button_label)

    def on_preview_button(self, event):
        preview = ""
        try:
            preview = exrex.getone(self.regex_tb.GetValue())
            self.preview_st.SetLabel('Preview: ' + preview)
        except Exception:
            self.preview_st.SetLabel('Invalid regex.')

    def on_close(self, event):
        self.spam_timer.Stop()
        mod_refs = list(
            filter(lambda m: m.startswith('modules.random_spam'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()


def dispose():
    RS.Close()


if __name__ == '__main__':
    app = wx.App()
    RS = RandomSpam(None, 'Random spam')
    app.MainLoop()
else:
    RS = RandomSpam(None, 'Random spam')
