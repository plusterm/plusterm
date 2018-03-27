from wx.lib.pubsub import pub
import sys


def handle_data(data):
    #m = 'rs'
    #pub.sendMessage('module.send', data=m)
    print(data[1].decode(errors='ignore'))


def on_untick():
    pub.unsubscribe(handle_data, 'serial.data')


pub.subscribe(handle_data, 'serial.data')