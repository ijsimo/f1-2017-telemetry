#!/usr/bin/python3

import sys
import signal
import socket
import threading
import queue
import mysql.connector
import time
import calendar
import datetime
from struct import unpack
from struct import pack         

def dataintake():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 20777
    sock = socket.socket(socket.AF_INET, # Internet
                 socket.SOCK_DGRAM) # UDP
    sock.bind(("", UDP_PORT))
    sock.settimeout(0.1)
    global dp
    while runthreads:
        try:
            data, addr = sock.recvfrom(1237) # buffer size is 1024 bytes
            fmt = '=76f24b1f5b 9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b9f9b'
            telem = unpack(fmt, data)
            d = telem + addr
            #save current time and add to data logger global variable
            t = (datetime.datetime.now().strftime("%H:%M:%S"), )
            dp = d + t
        except socket.timeout:
            pass
        except:
            print (sys.exc_info()[1])

def datalog():
   #adds latest received telemetry to text file every second
    global dp
    while runthreads:
        if 'dp' in globals():
            if len(str(dp)) > 10:
                f = open('data.txt', 'a+')
                f.write(str(dp))
                f.write("\n")
                f.close()
                dp = ()
        time.sleep(1)
      
q = queue.Queue()

## Begin data intake and data processing threads
runthreads = True

i = threading.Thread(target=dataintake)
i.daemon = True
i.start()

while True:
    datalog()
    time.sleep(1) #20 updates per second
