#! /usr/bin/env python3
import wx
# from wx.lib.pubsub import pub
from pubsub import pub
import importlib
import queue
import sys

import gui
import communicator


class SerialMonitor(wx.App):
    ''' Entry point and central class ('context') for Plusterm '''

    def __init__(self):
        super(SerialMonitor, self).__init__()
        self.communicator = communicator.Communicator(self)

        # Subscribe to input from modules
        pub.subscribe(self.send_from_module, 'module.send')

    def OnInit(self):
        # Show the GUI
        self.sm_gui = gui.SerialMonitorGUI(
            None, title='Plusterm', context=self)
        self.SetTopWindow(self.sm_gui)
        self.sm_gui.Show()
        return True

    def connect_serial(self, **settings):
        ''' Instruct communicator to initialize a connection '''
        if self.communicator.connect(**settings):
            self.log_to_gui('Connection opened\n')

            stat = ''
            if settings['type'] == 'serial':
                stat = 'Open: {}, {}'.format(
                    settings['port'], settings['baudrate'])

            elif settings['type'] == 'socket':
                stat = 'Open: {}:{}'.format(
                    settings['host'], settings['port'])

            self.sm_gui.statusbar.SetStatusText(stat)
            return True
        return False

    def disconnect_serial(self):
        ''' Instruct communicator to disconnect connection '''
        if self.communicator.disconnect():
            try:
                self.log_to_gui('Connection closed\n')
                self.sm_gui.statusbar.SetStatusText('No connection open')
                return True

            except Exception as e:
                print(e)
                return False

        return False

    def send_serial(self, cmd):
        ''' Relay a message/command to send over the connection '''
        self.communicator.send_cmd(cmd)

    def log_to_gui(self, msg):
        ''' Pass the message to be logged in the GUI '''
        self.sm_gui.output(msg)

    def add_module(self, module):
        ''' Import a module '''
        if 'modules.' + module in sys.modules:
            importlib.reload(sys.modules['modules.' + module])
        else:
            importlib.import_module('modules.' + module)

    def remove_module(self, module):
        ''' "Unimport" a module '''
        mod_name = 'modules.' + module

        # try to call dispose() function in module
        if mod_name in sys.modules:
            m = sys.modules[mod_name]
            try:
                m.dispose()

            except AttributeError:
                pass

        # remove references from sys.modules
        mod_refs = list(filter(lambda m: m.startswith(mod_name), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]

    def send_from_module(self, data):
        # PubSub callback, topic module.send
        self.log_to_gui('module > ' + data + '\n')
        self.send_serial(data)

    def get_data(self):
        ''' Try to get data from queue '''
        try:
            data = self.communicator.get_data()
            if data is not None:
                pub.sendMessage('serial.data', data=data)

        except queue.Empty:
            pass

    def get_error(self):
        ''' Try to get error from queue '''
        try:
            err = self.communicator.get_error()
            if err is not None:
                pub.sendMessage('serial.error', data=err)

        except queue.Empty:
            pass


def main():
    SM = SerialMonitor()
    SM.MainLoop()


if __name__ == '__main__':
    main()
