from wx.lib.pubsub import pub
import serial
import threading
import queue
import time


class ComReaderThread(threading.Thread):
    ''' 
    Creates a thread that continously reads from the serial connection
    Puts result as a tuple (timestamp, data) in a queue
    '''
    
    def __init__(self, ser, data_que, error_que):
        threading.Thread.__init__(self)
        self.ser = ser
        self.data_que = data_que
        self.error_que = error_que

        self.alive = threading.Event()
        self.alive.set()


    def run(self):
        while self.alive.isSet():
            try:
                data = self.ser.read()
                if len(data) > 0:
                    timestamp = time.time()

                    # read data until newline (x0A/10) 
                    while data[-1] != 0x0A:
                        data += self.ser.read()

                    self.data_que.put((timestamp, data))
                    
            except serial.SerialException as e:
                reconnected=False
                print('Serial connection lost, trying to reconnect.')
                ts = time.time()
                self.error_que.put((ts, str(e)))
                while not reconnected and self.alive.isSet():
                    try:
                        # if ser still thinks it's open close it
                        if self.ser.is_open:
                            self.ser.close()
                        
                        self.ser.open()
                        
                    except Exception as e:  
                        # if reconnection failed let some time pass                 
                        time.sleep(0.1)

                    else:
                        reconnected=True    
                        print('Reconnected')            


    def stop(self, timeout=None):       
        self.alive.clear()
        threading.Thread.join(self, timeout)
