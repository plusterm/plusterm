# from wx.lib.pubsub import pub
from pubsub import pub


def handle_data(data):
    #m = 'rs'
    #pub.sendMessage('module.send', data=m)
    print(data[1].decode(errors='ignore'))

def dispose():
    pub.unsubscribe(handle_data, 'serial.data')


pub.subscribe(handle_data, 'serial.data')