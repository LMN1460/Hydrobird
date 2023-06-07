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

# Import Hydrobird core functions
import hydrobird_core as hydro

# Initialization
os.system("clear")
print("Hydrobird is online!")
time.sleep(2)

# Verify datetime accuracy
if input("The system datetime is " + time.strftime("%m/%d/%Y %H:%M") + ", is this correct? (y/n) ").upper() == "N":
    print("This system depends on an accurate clock to run properly. Ask your teacher to set the time on the Rasberry Pi (requires sudo).")
    if input("Continue anyway? ").upper() == "N":
        quit()

# Call once as part of startup (defined as function to call later from menu)
def deviceCall():
    print("Checking devices...", end = " ")
    failed = hydro.devCheck() #should return None if all good
    if failed != None:
        output = "" # format list of failed devices into string
        for i in range(0, len(failed)):
            output = output + failed[i]
            if i < len(failed)-1: # insert commas between items for readability
                output = output + ", "
        print("Error! One or more devices failed: " + output)
    else:
        print("all good!", end = " ")
deviceCall()
print()

# Call once as part of startup (defined as function to call later from menu)
def instruxCall():
    print("Default instruction set is located at " + path + "instrux.txt.")
    while 1:
        inp = input("Enter file path or press enter to load default. ")
        if inp == "":
            outp = hydro.loadInstrux()
        else:
            outp = hydro.loadInstrux(inp)
        if outp == "notFound":
            print("Error! No file found.", end = " ")
        elif outp == "noAccess":
            print("Error! Invalid file permissions.", end = " ")
        elif outp == "wrongType":
            print("Error! Invalid file type (must be a .txt file).", end = " ")
        else:
            break
instruxCall()
        
# Start thread
t = Thread(target = hydro.timing)
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

# Call from menu
def ph():
    # If user chooses to log readings
    if input("Record to file? (y/n) ").upper() == "Y":
        # Get .csv file path
        print("The default save location for pH readings is located at " + path + "readings.csv. A file with this path will be created if it does not currently exist.")
        while 1:
            inp = input("Enter file path or press enter for default. ") 
            if inp == "":
                outp = hydro.takePH(True)
            else:
                outp = hydro.takePH(True, inp)
            if outp == "noAccess":
                print("Error! Invalid file permissions.", end = " ")
            elif outp == "wrongType":
                print("Error! Invalid file type (must be a .txt file).", end = " ")
            else:
                print("pH: " + str(outp)) # return pH reading
            break
    # If user chose not to log readings
    else:
        print("pH: " + str(hydro.takePH(False)))
        
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
