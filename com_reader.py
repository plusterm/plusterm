# from wx.lib.pubsub import pub
from pubsub import pub
import serial
import threading
import queue
import time


class ComReaderThread(threading.Thread):
    ''' 
    Creates a thread that continously reads from the serial connection
    Puts result as a tuple (timestamp, data) in a queue
    '''
    
    def __init__(self, ser, error_que):
        threading.Thread.__init__(self)
        self.ser = ser
        self.error_que = error_que

        self.alive = threading.Event()
        self.alive.set()

    def run(self):
        while self.alive.isSet():
            try:
                # data = self.ser.read()
                if self.ser.in_waiting > 0:
                    timestamp = time.time()

                    # read data until newline (x0A/10) 
                    # while data[-1] != 0x0A:
                    #     data += self.ser.read()
                    data = self.ser.readline()

                    pub.sendMessage('serial.data', data=(timestamp, data))

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

    def stop(self, timeout=0.5):
        self.alive.clear()
        threading.Thread.join(self, timeout)
