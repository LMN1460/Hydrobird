# Version number
ver = "1.1.1"
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

# Initialization
os.system("clear")
print("Hydrobird is online!")
time.sleep(2)

# Verify datetime accuracy
if input("The system datetime is " + time.strftime("%m/%d/%Y %H:%M") + ", is this correct? (y/n) ").upper() == "N":
    print("This system depends on an accurate clock to run properly. Ask your teacher to set the time on the Rasberry Pi (requires sudo).")
    if input("Continue anyway? ").upper() == "N":
        quit()

# Core method: Check/connect devices
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
    
# Call once as part of startup (defined as function to call later from menu)
def deviceCall():
    print("Checking devices...", end = " ")
    failed = devCheck() #should return None if all good
    if failed != None:
        output = "" # format list of failed devices into string
        for i in range(0, len(failed)):
            output = output + failed[i]
            if i < len(failed)-1: # insert commas between items for readability
                output = output + ", "
        print("Error! One or more devices failed: " + output)
deviceCall()
print()

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
        
# Call once as part of startup (defined as function to call later from menu)
def instruxCall():
    print("Default instruction set is located at " + path + "instrux.txt.")
    while 1:
        inp = input("Enter file path or press enter to load default. ")
        if inp == "":
            outp = loadInstrux()
        else:
            outp = loadInstrux(inp)
        if outp == "notFound":
            print("Error! No file found.", end = " ")
        elif outp == "noAccess":
            print("Error! Invalid file permissions.", end = " ")
        elif outp == "wrongType":
            print("Error! Invalid file type (must be a .txt file).", end = " ")
        else:
            break
instruxCall()
        
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

# Start thread
t = Thread(target = timing)
t.start()

# Define header text
def header():
    print("Hydrobird ver " + ver + ". All physical components are the property of Oakdale Middle School.")
    print("Do not close this window, or all Hydrobird processes will close as well.")
    print()

# List of commands with descriptions: edit if adding a new command
cmdList = ["help", "ph", "update", "check", "pumpon", "pumpoff", "about"]
cmdDesc = ["brings up this list.", "opens the pH reader utility.", "updates Hydrobird's instruction set if it has been modified since first load. You can set a different file path if necessary.", "checks devices for operability and reopens any closed channels.", "manually turns the pump motor on.", "manually turns the pump motor off.", "lists information about Hydrobird and its contributors."]

# Command help
def help():
    print("Command list:", end = " ")
    for i in range(0, len(cmdList)): # print command list
        print(cmdList[i], end = "")
        if i < len(cmdList)-1: # format commas between each item
            print(", ", end = "")
    print() # won't actually create newline
    for i in range(0, len(cmdList)): # print description for each command
        print("    - \"" + cmdList[i] + "\" " + cmdDesc[i])

# Core method: take pH readings (renamed from core definition to prevent conflict from menu call)
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

# Call from menu
def ph():
    # If user chooses to log readings
    if input("Record to file? (y/n) ").upper() == "Y":
        # Get .csv file path
        print("The default save location for pH readings is located at " + path + "readings.csv. A file with this path will be created if it does not currently exist.")
        while 1:
            inp = input("Enter file path or press enter for default. ") 
            if inp == "":
                outp = takePH(True)
            else:
                outp = takePH(True, inp)
            if outp == "noAccess":
                print("Error! Invalid file permissions.", end = " ")
            elif outp == "wrongType":
                print("Error! Invalid file type (must be a .txt file).", end = " ")
            else:
                print("pH: " + str(outp)) # return pH reading
            break
    # If user chose not to log readings
    else:
        print("pH: " + str(takePH(False)))
        
# Update instruction set
def update():
    instruxCall()

# Recheck/connect devices
def check():
    deviceCall()
    print() # newline
    
# Turn pump on
def pumpon():
    motorPlug.setState(True)
    print("Pump turned on.")
    
# Turn pump off
def pumpoff():
    motorPlug.setState(False)
    print("Pump turned off.")

# About
def about():
    os.system("clear")
    print(''' 
 /%%   /%%                 /%%                     /%%       /%%                 /%%
| %%  | %%                | %%                    | %%      |__/                | %%
| %%  | %% /%%   /%%  /%%%%%%%  /%%%%%%   /%%%%%% | %%%%%%%  /%%  /%%%%%%   /%%%%%%%
| %%%%%%%%| %%  | %% /%%__  %% /%%__  %% /%%__  %%| %%__  %%| %% /%%__  %% /%%__  %%
| %%__  %%| %%  | %%| %%  | %%| %%  \__/| %%  \ %%| %%  \ %%| %%| %%  \__/| %%  | %%
| %%  | %%| %%  | %%| %%  | %%| %%      | %%  | %%| %%  | %%| %%| %%      | %%  | %%
| %%  | %%|  %%%%%%%|  %%%%%%%| %%      |  %%%%%%/| %%%%%%%/| %%| %%      |  %%%%%%%
|__/  |__/ \____  %% \_______/|__/       \______/ |_______/ |__/|__/       \_______/
           /%%  | %%                                                                
          |  %%%%%%/                                                                
           \______/                                                      ''', end = "")
    print("Version " + ver)
    print()
    print("All physical components are the property of Oakdale Middle School.")
    print("Controller: Raspberry Pi 3 Model B+")
    print("Devices: ")
    print("    - VINT Hub Phidget    HUB0001_0")
    print("    - Power Plug Phidget  PSU1000_0")
    print("    - pH Sensor Phidget   ADP1000_0")
    print()
    print("Teacher Advisor:  Anita Waravdekar, Oakdale Middle School Science Teacher")
    print("Project Manager:  Rowan Wood, Class of '27")
    print("Lead Engineer:    Rowan Wood")
    print("Lead Programmer:  Chloe Wood, Class of '24")
    print("Graphics Design:  Chloe Wood")
    print("OS Assistance:    Evan Moser, FCPS Career and Tech Center Linux Instructor")
    print("Rubber Ducking:   Sylvia BSD (https://github.com/unix-witch)")
    print()
    print("Special thanks to Penn State University for hosting their 2022 Expanding Youth Involvement in Exploring Exciting Employment Directions in Agriculture (YIELD) workshop.")
    print("Ms. Waravdekar's participation in this workshop inspired her to launch this project. The Raspberry Pi and other hardware components used in this project were also supplied/funded by the workshop.")
    print()
    print()
    input("Press enter to continue. ")
    os.system("clear")
    header()

# Main menu loop
time.sleep(3)
os.system("clear")
header()
while 1:
    cmd = input("Type a command: ").lower()
    if cmd in cmdList:
        exec(cmd+"()")
    else:
        print("Invalid command.", end = " ")
