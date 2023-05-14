# Hydrobird

Repository for the Hydrobird hydroponics system controller and associated files.

**DISCLAIMER:** This code was developed for use on a Raspberry Pi running the Rasberry Pi OS. Therefore, this code structure assumes a Linux-based system, and any attempts to run this on a non-Linux system cannot be guaranteed to work.

## Console Program Installation

In it's current state, this code cannot be easily deployed through the command line; you must manually set up the file structure. Do so in the following manner:

* Create a single folder to store all of Hydrobird's files in. Copy `hydrobird_terminal.py` and `run.sh` to this folder.
* Create a file `instrux.txt` containing your desired instruction set, following the format described in the example `instrux.txt` file. Save this in the folder.
* Modify the `path` variable in the third line of `hydrobird_terminal.py` to point to the folder's location.
* Modify the filepath stated in `run.sh` to point to `hydrobird_terminal.py`. Make sure`run.sh` has execute permissions; use `chmod +x run.sh` if neccesary.
* Copy `hydrobird.desktop` to the desktop. This shortcut will run `run.sh`, which will launch `hydrobird_terminal.py`.
* Modify user and file permissions as necessary.

Hydrobird is hardcoded to interact with the Phidgets family of sensors, specifically the Power Plug Phidget (PSU1000_0) and the pH Sensor Phidget (ADP1000_0). This also necessitates the use of the  Hub Phidget (HUB0001_0) that the power plug and pH sensor will be plugged into. Connect the smart plug to port 0 and the pH sensor to port 1 of the hub. You may plug the hub into any USB-A port of the host computer.

## Usage

Upon initiation, or when prompted to by user command, Hydrobird will open a specified text file and read each line. Any lines preceded by a `#` symbol will be wholly ignored, while the rest will be copied into Hydrobird for parsing. Parsing follows these rules:
* Segment each line (full instruction) as a list, reading space characters as dividers between items.
* Record the first item as a time in 24 hour format.
* Record the second item as the device to perform an action on.
* Record the third item as the action to perform.
* Any further items will be ignored.

Hydrobird will check its list of instructions every minute and execute any instructions whose time matches the current system time. Using this instruction set as an example:
```
# This is a comment!
13:30 pump on
13:45 pump off
```
The first line will be ignored. The second line instructs Hydrobird to turn on the smart plug (and therefore the pump) at 13:30 (1:30 PM). The third line instructs Hydrobird to turn off the smart plug at 13:45 (1:45 PM).

Note that this system checks against the system time; if the system time is inaccurate, instructions will execute at unexpected times.

## Commands

While Hydrobird is running, you may run any of these commands:
* `help` to bring up the list of commands.
*  `ph` to open the pH reader utility. You may choose to save readings to a `.csv` file or not.
* `update` to update/reload the instructions loaded into Hydrobird. You may load a different file if desired.
*  `check` to check devices for operability and reopen any closed channels.
* `pumpon` or `pumpoff` to manually turn on or off the pump (power plug).
* `about` to view the about page.

## Customization

If you want to use the Hydrobird functions in your own implementation (say, a Flask app), copy the functions located in the `hydrobird_core.py` file. Not sure if they'll work as direct imports yet, but that'll be updated soon.

## Contribute

This system is still very much a work-in-progress; any bug fixes or feature requests would be much appreciated. If you wish to use this code in your own system (or are a student recruited to mantain its original implementation), you're more than welcome to contact me for assistance. Email avaliable upon request.

## License

[MIT](https://choosealicense.com/licenses/mit/)
