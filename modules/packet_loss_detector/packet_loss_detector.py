import wx
from wx.lib.pubsub import pub
import re
import binascii
import sys

''' Requires the "binascii" library. "python -m pip install binascii".

    This module is intended to detect communication issues between Plusterm
    and hardware. So far it only works as sort of a ping-pong scheme with an
    Arduino Uno that compares the data with a known crc32 checksum and returns
    if it failed or not, aswell as a new message to be compared in the module.
    The Arduino file used for the test is included in the "test-things" folder.
    The format of the expected Arduino response is "match|fail,pole".
    '''


class PacketLossDetector(wx.Frame):
    def __init__(self, parent, title):
        super(PacketLossDetector, self).__init__(parent, title=title)
        pub.subscribe(self.detector, 'serial.data')

        self.pld_regex = '(\w+)\,(\w+)'  # Format of expected response
        self.known_checksum = 0xfd6042e1  # CRC32 checksum for "pole"

        self.message = 'plus'  # The "ping message" sent to hardware
        self.match = 'match'  # Expected string before comma if message matched
        self.fail = 'fail'  # Expected string before comma if message failed

        self.detecting = False

        self.init_ui()

    def init_ui(self):
        text_panel = wx.Panel(self)
        text_sizer = wx.BoxSizer(wx.VERTICAL)

        button_panel = wx.Panel(self)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.in_error_st = wx.StaticText(
            text_panel,
            label='Errors in: 0 (0%)')

        self.out_error_st = wx.StaticText(
            text_panel,
            label='Errors out: 0 (0%)')

        self.tot_mess_st = wx.StaticText(
            text_panel,
            label='Amount of messages: 0')

        self.tot_error_st = wx.StaticText(
            text_panel,
            label='Error rate: 0%')

        text_sizer.Add(self.in_error_st)
        text_sizer.Add(self.out_error_st)
        text_sizer.Add(self.tot_mess_st)
        text_sizer.Add(self.tot_error_st, 0, wx.TOP, 5)

        self.detect_button = wx.Button(
            button_panel,
            label='Start',
            size=(170, 30))
        self.detect_button.Bind(wx.EVT_BUTTON, self.on_button)

        self.reset_button = wx.Button(
            button_panel,
            label='Reset',
            size=(100, 30))
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset)

        button_sizer.Add(self.detect_button)
        button_sizer.Add(self.reset_button)

        text_panel.SetSizer(text_sizer)
        button_panel.SetSizer(button_sizer)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(text_panel, 0, wx.EXPAND | wx.ALL, 7)
        main_sizer.Add(button_panel, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT, 5)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.SetSizer(main_sizer)
        self.Fit()
        self.SetMinSize(self.GetBestSize())
        self.SetMaxSize(self.GetBestSize())
        self.SetBackgroundColour('lightgray')
        self.Centre()

        self.on_reset(wx.EVT_BUTTON)
        self.Show(True)

    def on_reset(self, event):
        self.failed_in = 0
        self.failed_out = 0
        self.match_in = 0
        self.match_out = 0

        self.update_labels()

    def on_button(self, event):
        if not self.detecting:
            self.detecting = True
            pub.subscribe(self.detector, 'serial.data')
            self.ping()
        else:
            self.detecting = False
            pub.unsubscribe(self.detector, 'serial.data')

        self.button_label = 'Start' if not self.detecting else 'Stop'
        self.detect_button.SetLabel(self.button_label)

    def update_labels(self):
        self.tot_errors = self.failed_in + self.failed_out
        self.tot_messages = self.tot_errors + self.match_in + self.match_out

        if (self.tot_errors) > 0:
            self.in_error_st.SetLabel(
                'Errors in: {0} ({1}%)'.format(
                    self.failed_in,
                    round((self.failed_in / self.tot_errors) * 100, 1)))

            self.out_error_st.SetLabel(
                'Errors out: {0} ({1}%)'.format(
                    self.failed_out,
                    round((self.failed_out / self.tot_errors) * 100, 1)))

            self.tot_mess_st.SetLabel(
                'Amount of messages: {}'.format(self.tot_messages))

            self.tot_error_st.SetLabel(
                'Error rate: {}%'.format(
                    round((self.tot_errors / self.tot_messages) * 100), 1))
        else:
            self.in_error_st.SetLabel('Errors in: 0 (0%)')
            self.out_error_st.SetLabel('Errors out: 0 (0%)')
            self.tot_mess_st.SetLabel('Amount of messages: 0')
            self.tot_error_st.SetLabel('Error rate: 0%')

    def ping(self):
        pub.sendMessage('module.send', data=self.message)

    def detector(self, data):
        d = data[1].decode(errors='ignore').strip()
        groups = re.findall(self.pld_regex, d)
        failed_in_bool = False

        try:
            if groups[0][0] == self.match:
                self.match_out += 1
            elif groups[0][0] == self.fail:
                # print('out fail')
                self.failed_out += 1
            else:
                # print('Can''t determine if out failed')
                self.failed_in += 1
                failed_in_bool = True

            checksum = int(  # Calculate checksum using binascii
                hex(binascii.crc32(groups[0][1].encode()) & 0xffffffff), 16)

            if checksum == self.known_checksum:
                self.match_in += 1
            elif not failed_in_bool:
                # print('in fail')
                self.failed_in += 1
        except IndexError:
            # print('Regex failed, can''t determin if out failed')
            self.failed_in += 1
            failed_in_bool = True

        self.update_labels()
        self.ping()

    def on_close(self, event):
        pub.unsubscribe(self.detector, 'serial.data')
        mod_refs = list(
            filter(lambda m: m.startswith(
                'modules.packet_loss_detector'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()


def dispose():
    PLD.Close()


if __name__ == '__main__':
    app = wx.App()
    PLD = PacketLossDetector(None, 'Packet loss detector')
    app.MainLoop()
else:
    PLD = PacketLossDetector(None, 'Packet loss detector')
