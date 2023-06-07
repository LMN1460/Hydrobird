# Version number
ver = "1.2.0"
path = "/home/Shared/OMS_Hydroponics/"

# Import Phidgets libraries
from Phidget22.Phidget import *
from Phidget22.Devices.DigitalInput import *
from Phidget22.Devices.DigitalOutput import *
from Phidget22.Devices.PHSensor import *

# Import other libraries
import os
import time
import csv
from pathlib import Path
from threading import Thread

# Check/connect devices
def devCheck():
    failed = [] # any failed devices will be reported in this list
    try: # check motor plug
        global motorPlug # need to be able to perform functions on motorPlug later in program
        motorPlug = DigitalOutput()
        motorPlug.setHubPort(0)
        motorPlug.setIsHubPortDevice(True)
        motorPlug.openWaitForAttachment(1000) # open channel
    except PhidgetException as err:
        failed.append("motor plug")
    try: # check pH reader
        global phSensor # need to be able to perform functions on phSensor later in program
        phSensor = PHSensor()
        phSensor.setHubPort(1)
        phSensor.openWaitForAttachment(1000) # open channel
    except PhidgetException as err:
        failed.append("pH reader")
        
    # Report results
        with open(path + "log.txt", "a") as log: # log device failures
            log.write("[" + time.strftime("%m/%d/%Y %H:%M") + "] WARNING! These devices failed the device check: " + str(failed) + "\n")
        return failed # return failed devices
    else:
        return None  
    
# Load instruction set
def loadInstrux(instruxLoc = path + "instrux.txt"):
    instruxPath = Path(instruxLoc) # convert string to Path object
    if instruxPath.is_file() == False: # if file does not exist
        return "notFound"
    elif not os.access(instruxPath, os.R_OK): # if user doesn't have read access to file
        return "noAccess"
    elif instruxLoc.find(".txt") == -1: # if path does not have .txt in it (doesn't lead to a .txt file)
        return "wrongType"
        
    # Load/format instruction set data for use
    with open(instruxPath, "r") as instrux:
        instruxList = instrux.readlines() # pull data from file
        for i in range(0, len(instruxList)): # strip newline characters from each item in list
            instruxList[i] = instruxList[i].replace("\n", "")
    # File closed by method, continue formatting data
    global instruxSet
    instruxSet = []
    for i in range(0, len(instruxList)):
        if instruxList[i][0] != "#": # ignore all lines that start with # (comments)
            xtime = instruxList[i].split(" ")[0] # pull line, split along space divider, and add each part to a dictionary
            device = instruxList[i].split(" ")[1] # if user mistakenly adds any additional parameters they'll be ignored
            action = instruxList[i].split(" ")[2] # first part: time, second: device, third: action to take
            instruxSet.append({"time" : xtime, "device" : device, "action" : action})
        
    # Log opening of instuction set
    with open(path + "log.txt", "a") as log:
        log.write("[" + time.strftime("%m/%d/%Y %H:%M") + "] Instruction set loaded from " + instruxLoc + "\n")
    return instruxSet # return finished instrux set
    
# Define thread to run timed components in background
def timing():
    mn = time.strftime("%M") # initial setting of variable of current minute to compare against
    while 1:
        if time.strftime("%M") != mn: # check to see if a minute has passed
            mn = time.strftime("%M") # update comparison variable
            for i in range(0, len(instruxSet)): # check each entry in instrux set
                if time.strftime("%H:%M") == instruxSet[i]["time"]: # if the current time matches an entry
                    
                    # Motor plug actions
                    if instruxSet[i]["device"].lower() in ["pump", "plug", "motor"]: # validate entry segments, allows wiggle room for device/action wording
                        doDevice = "motor plug" # for log formatting
                        if instruxSet[i]["action"].lower() in ["on", "true"]:
                            doAct = True
                        elif instruxSet[i]["action"].lower() in ["off", "false"]:
                            doAct = False
                        motorPlug.setState(doAct) # perform action
                    # Room for expansion: add more if statements to support additional devices, follow above structure
                    # Make sure to set doDevice and doAct so the log file will record that information
                    
                    # Record action to file
                    with open(path + "log.txt", "a") as log:
                        log.write("[" + time.strftime("%m/%d/%Y %H:%M") + "] Device \"" + doDevice + "\" set to state \"" + str(doAct) + "\"\n")


# Take pH readings
def takePH(record, phLoc = path + "readings.csv"):
    if record == True: # if user chooses to log readings
        phPath = Path(phLoc) # convert string to Path object
        if phPath.is_file() == True: # only check for write access if is an already existent file
            if not os.access(phPath, os.W_OK):
                return "noAccess"
        elif phLoc.find(".csv") == -1: # if path does not lead to a .csv file
            return "wrongType"
        
        # Open files and record readings
        with open(path + "log.txt", "a") as log, open(phPath, "a", newline="") as phFile:
            writer = csv.writer(phFile)
            if phPath.stat().st_size == 0: # if file is empty (newly created)
                writer.writerow(["Date and Time", "pH Reading"]) # add appropriate headers
            reading = round(phSensor.getPH(), 2) # sensor is inaccurate beyond 2 decimal places
            writer.writerow([time.strftime("%m/%d/%Y %H:%M"), reading]) # write pH reading to .csv file
            log.write("[" + time.strftime("%m/%d/%Y %H:%M") + "] pH reading " + str(reading) + " recorded to " + phLoc + "\n") # log write action
        return reading
    # If user chose not to log readings
    else:
        reading = round(phSensor.getPH(), 2) # sensor is inaccurate beyond 2 decimal places
        return reading
