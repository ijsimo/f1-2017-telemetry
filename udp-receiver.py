#!/usr/bin/python

import sys
import socket
import threading
import queue
import time
from struct import unpack

class carInfo(object):
   # def __init(self):
    ip = "127.0.0.1"
    sessionTime = "0"
    sessionType = "0"
    trackId = "0"
    x = '0'
    y = '0'
    z = '0'
    lastLapTime = '0'
    currentLapTime ='0'
    bestLapTime ='0'
    sector1Time ='0'
    sector2Time ='0'
    lapDistance ='0'
    driverId ='0'
    teamId ='0'
    trackPosition ='0'
    currentLapNum ='0'
    tyreCompound ='0'
    inPits ='0'
    sector ='0'
    currentLapInvalid ='0'
    

def updateDatabase(cars):

    for car in cars:
        print(vars(car))


def dataIntake():
    #Data Intake thread - receives packets from the UDP socket
    #and adds the data into a queue
    UDP_IP = "127.0.0.1"
    UDP_PORT = 20777 #receiving port
    sock = socket.socket(socket.AF_INET, # Internet
                 socket.SOCK_DGRAM) # UDP
    sock.bind(("", UDP_PORT))
    sock.settimeout(0.1)
    global runthreads
    while runthreads:
        try:
            data, addr = sock.recvfrom(2048) # buffer size is 2048 bytes
            fmt = '76f26b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b9f8b'
            telem = unpack(fmt, data)
            d = addr + telem
            #unpivot into allCars matrix
            allCars = [[0 for x in range(22)] for y in range(20)]
            #creates blank car data arrays
            #22 attributes, 20 cars
            for i in range(20):
                allCars[i][0] = d[0] #ip address received from
                allCars[i][1] = d[1] #port
                allCars[i][2] = d[2] #sessiontime
                allCars[i][3] = d[70] #trackid
                allCars[i][21] = d[68] #sessiontype
                for j in range(17):
                    allCars[i][j+4] = d[104 + i*17 + j] #other car data
            for c in allCars:
                #add data from all 20 cars into queue
                q.put(c)
        except socket.timeout:
            pass
        except:
            #Handle errors with processing UDP packet
            print ("Unexpected error:" , sys.exc_info()[1])

def dataProcess():
    #Take data from queue and add to temporary cars array
    global runthreads
    while runthreads:
        try:
            d = q.get()
            global cars
            i = 0
            c = -1
            for car in cars:
                if car.ip == d[0] and car.driverId == int(d[13]): #check for existing ip address and driverId
                    c = i
                i = i + 1
            if (c == -1):
                newCar = carInfo()
                newCar.ip = d[0]
                newCar.driverId = int(d[13])
                cars.append(newCar)
            cars[c].sessionTime = d[2]
            cars[c].sessionType = d[21]
            cars[c].trackId = d[3]
            cars[c].x = d[4]
            cars[c].y = d[5]
            cars[c].z = d[6]
            cars[c].lastLapTime = d[7]
            cars[c].currentLapTime = d[8]
            cars[c].bestLapTime = d[9]
            cars[c].sector1Time = d[10]
            cars[c].sector2Time = d[11]
            cars[c].lapDistance = d[12]
            cars[c].teamId = d[14]
            cars[c].trackPosition = d[15]
            cars[c].currentLapNum = d[16]
            cars[c].tyreCompound = d[17]
            cars[c].inPits = d[18]
            cars[c].sector = d[19]
            cars[c].currentLapInvalid = d[20]

            q.task_done()
            
        except q.Empty:
            time.sleep(0.1) #if queue empty then pause slightly

def refreshdata():
    try:
        global cars
        cars_copy = cars[:]
        cars = []
        updateDatabase(cars_copy)
    except:
        pass
cars = []
q = queue.Queue()

## Begin data intake and data processing threads
runthreads = True

i = threading.Thread(target=dataIntake)
i.daemon = True
i.start()

j = threading.Thread(target=dataProcess)
j.daemon = True
j.start()

while True:
    refreshdata()
    time.sleep(0.05) #20 updates per second
