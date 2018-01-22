from wx.lib.pubsub import pub

def handle_data(data):
	print(data)

pub.subscribe(handle_data, 'serial.data')