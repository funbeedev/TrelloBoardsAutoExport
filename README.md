# TrelloBoardsAutoExport 
Export JSON of Trello boards using web scraping.

## Contents
- [Background](#Background)
- [Setup](#Setup)
- [RunningScript](#RunningScript)
- [AutoSchedule](#AutoSchedule)
- [Extras](#Extras)

## Background

### About Trello
Trello.com is a website providing a visual organisation platform for lists, notes, projects or anything you want to organise. Trello boards are used to group visuals of your information.

[Browse Trello boards samples to learn more](https://trello.com/templates)

### Why use this script
Trello provides a menu option within each board to export the contents in JSON format. These JSON exports can be used as a backup of information contained within each board.
This script will automatically navigate to each board listed and export the JSON.
Why this may be helpful for you:
- It's a handy way to perform a JSON export of all your Trello boards in a single click.
- You can schedule this script to auto run at scheduled times, acting as an auto backup of your Trello boards (See [AutoSchedule](#AutoSchedule) section).


## Setup

### Step 1. Trello account
You need a user account on Trello.com with at least one Trello board created. Know your Trello login email and password.

### Step 2. Browser and driver 
You need to have either Firefox or Chrome installed. You also need the corresponding driver for the browser.

For Firefox download geckodriver:
https://github.com/mozilla/geckodriver/releases

For Chrome download chromedriver:
https://chromedriver.chromium.org/downloads

### Step 3. Setup Python and modules

Python and the following modules must be installed on the computer running this script.
Instructions tested on Ubuntu Linux distros, run commands on a terminal.

Install Python 3 and pip3:
```
sudo apt-get install python3
sudo apt-get install pip3
```

Install requirements:
```
pip3 install -r requirements.txt
```


## RunningScript

### Step 1. Configure file 

- Open the file "trello-boards-export-info"
- Set your browser and if you want to run in headless mode. (Headless mode means the browser window won't open while script is running)
- Input your Trello email on the second line in the file.
- Input your Trello password on the third line in the file (case-sensitive).
- From the fourth line onwards, list the name of each board you want to export. One line per board. 

Sample file configuration:
```
driver=firefox;headless=true
user@gmail.com
mysecretpassword
BOARDNAME_1
BOARDNAME_2
```

### Step 2. Run the script
Run the python script through any compatible IDE. Or run on a terminal using:
```
python3 trello-boards-auto-export.py
```

The program should export the JSON of each board in the same directory as the script. The file exported will be in the format:
```
BOARDNAME_1_ddmmyyyy.json
BOARDNAME_2_ddmmyyyy.json
```

## AutoSchedule
This section is optional.

### Using Crontab Linux utility
Schedule the time and frequency to run this script. See the [Crontab man page](https://linux.die.net/man/5/crontab).

Open the crontab file for editing
```
crontab -e
```
This example will run the script everyday at 07:05am. Edit according to your needs.

Add the following to the end of the crontab file
```
# needed if headless=false
DISPLAY=:0

# at 07:05am go to directory of script and run. log output and potential errors to 'crontab.log'
05 07 * * * cd /pathtoscript/ && python3 trello-boards-auto-export.py > crontab.log 2>&1
```
Save the crontab file
```
crontab: installing new crontab
```
The script should now run everyday at 07:05am.

## Troubleshooting

- A log file 'trello-scraping.log' is produced during running of the script. It will be located in the same directory as the script. 

- This script runs on Linux. Not tested on Windows yet.

## Extras

### Why use webscraping for this purpose?

Good question. 
Since webscraping manipluates HTML elements on a page, any change in the HTML layout of the website being controlled can result in failure when running a web scraping script. It means this script might need to be updated if Trello.com changed certain aspects of the site layout. 

This is admittedly a huge disadvantage. However, I wrote this script to learn web scraping and test the limits of it :)
Trello does have an API interface that can probably perform the same functionality much easier (not completely sure as I haven't tried that method yet).
