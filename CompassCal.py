import requests
import re 
from datetime import datetime
import pytz
import PySimpleGUI as sg
from os import path
date = datetime.now()
login = ''

sg.theme('DarkBlack')



if(path.exists("login.txt")):
    f = open("login.txt", "r")
    login = f.readlines(0)[0] 
    f.close()
else:
    layout = [[sg.Text("Enter Sync My Schedule link: "), sg.InputText(),sg.Submit()]]
    window = sg.Window('Compass Cal', layout)
    event, values = window.read()
    login = values[0]
    f = open("login.txt", "w")
    f.write(login)
    f.close()
    window.close()

login = login.replace("webcal", "https")

# request .ics file and convert it to text
file = requests.get(login).text

# get rid of the newline chars and empty the '' strings from the array
f = re.split("\n|\r", file)
data = []
for l in f:
    if l != '':
        data.append(l)



# todays date
today = datetime.today()
timetable = []
list = []

for line in data:

    if len(list) >= 3 :
        if list[0].date() == datetime.today().date():
            timetable.append(list)
        list = []

    

    location = re.search("^LOCATION", line)
    if location:
        list.append(line.split(":")[1])

    summary = re.search("^SUMMARY", line)
    if summary:
        # TODO split string at : plus one!
        list.append(line.split("9")[1])

    start = re.search("^DTSTART", line)
    if start:
        # split the "DTSTART:time" so its just the time
        d = line.split(":")[1]
        # where to split the time string
        indices = [0,4,6,8,9,11,13]
        parts = [d[i:j] for i,j in zip(indices, indices[1:]+[None])]
        # convert UTC time to AEST
        # get day and hour
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        hr = int(parts[4])
        min = int(parts[5])

        utc = datetime(year, month, day, hr, min, 00, tzinfo = pytz.utc)

        aest = utc.astimezone(pytz.timezone('Australia/Melbourne'))
        
        list.append(aest)
    
    
timetable.sort()
    
for item in timetable:
    print(item[2], item[1], item[0].date(), item[0].time())









# Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text(date.strftime('%A') + ", " + date.strftime('%d') + " " + date.strftime('%B') + " " + date.strftime('%Y'))],
            [sg.Text('')],
]

y = 0
for t in timetable:
    layout += [
        [sg.Text(t[0].time()), sg.Push(), sg.Text(t[2]), sg.Text(t[1])]
    ]
    if y == 1 or y == 4:
        layout += [
        [sg.Text("")]
        ]
    y += 1
if y == 0:
    layout += [
        [sg.Push(), sg.Text("No School"), sg.Push()],
        [sg.Text("")]
    ]


# Create the Window
window = sg.Window('Compass Cal', layout, grab_anywhere=True)
# process "events" and get the "values" of the inputs
event, values = window.read()