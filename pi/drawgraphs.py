#! /usr/bin/env python

# Vivarium monitoring sensor script. Run by a cron job. Reads temperature and
# humidity values written to the log file. Outputs charts of the last seven
# days for each sensor with min/max lines. Sends alert emails if either figure
# goes out of bounds.

# Written by Ian Renton (http://ianrenton.com)

from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

import matplotlib
matplotlib.use('Agg') # Avoid need for X server. Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pylab import savefig

# Constants
MIN_TEMP = 16.0
MAX_TEMP = 28.0
MIN_HUMID = 50.0
MAX_HUMID = 100.0
ALARM_EMAIL = 'geckocam'
TIME_FORMAT = "%Y-%m-%d-%H-%M-%S"

# Tail history data from file, using system call because I'm lazy
stdin,stdout = os.popen2("tail -n 672 sensordata.csv") # 672 = one week of samples at 15 min intervals
stdin.close()
lines = stdout.readlines()
stdout.close()

# Mangle strings into proper data
datetimes = []
temps = []
humids = []
i = 0
for line in lines:
  splitline = line[:-1].split(',')
  datetimes.append(datetime.strptime(splitline[0], TIME_FORMAT))
  temps.append(float(splitline[1]))
  humids.append(float(splitline[2]))

# Get latest values for special handling
temp = temps[-1]
humid = humids[-1]
  
# Create min/max lines
maxTemp = [MAX_TEMP]*len(temps)
minTemp = [MIN_TEMP]*len(temps)
maxHumid = [MAX_HUMID]*len(humids)
minHumid = [MIN_HUMID]*len(humids)

# Plot and save temp chart
matplotlib.rcParams.update({'font.size': 8})
fig = plt.figure(figsize=(4,3))
ax  = fig.add_subplot(1, 1, 1, axisbg='#181211')
ax.spines['bottom'].set_color('white')
ax.spines['top'].set_color('white') 
ax.spines['right'].set_color('white')
ax.spines['left'].set_color('white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.yaxis.label.set_color('white')
ax.set_color_cycle(['y', 'b', 'r'])
plt.plot(datetimes, temps, datetimes, minTemp, datetimes, maxTemp)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=12))
plt.ylim(14.0,30.0)
plt.ylabel("Temperature / C")
if temp == 0.0:
  plt.title("[TEMPERATURE SENSOR OFFLINE]")
  ax.title.set_color('red')
else:
  plt.title("Vivarium Temperature (Currently " + str(temp) + "C)")
  ax.title.set_color('white')
plt.gcf().autofmt_xdate()
plt.savefig('temp.png', facecolor='#181211')

# Plot and save humid chart
fig = plt.figure(figsize=(4,3))
ax  = fig.add_subplot(1, 1, 1, axisbg='#181211')
ax.spines['bottom'].set_color('white')
ax.spines['top'].set_color('white') 
ax.spines['right'].set_color('white')
ax.spines['left'].set_color('white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.yaxis.label.set_color('white')
ax.title.set_color('white')
ax.set_color_cycle(['y', 'b', 'r'])
plt.plot(datetimes, humids, datetimes, minHumid, datetimes, maxHumid)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=12))
plt.ylim(40.0,100.0)
plt.ylabel("Humidity / % RH")
if humid == 0.0:
  plt.title("[HUMIDITY SENSOR OFFLINE]")
  ax.title.set_color('red')
else:
  plt.title("Vivarium Humidity (Currently " + str(humid) + "%)")
  ax.title.set_color('white')
plt.gcf().autofmt_xdate()
plt.savefig('humid.png', facecolor='#181211')

# Email alarms
prevTemp = temps[-2]
prevHumid = humids[-2]

if (prevTemp >= MIN_TEMP) and (temp < MIN_TEMP):
  os.popen2('ssh server "echo \\\"Temperature has fallen to ' + str(temp) + 'C\\\" | mail -s \\\"Vivarium Alarm\\\" ' + ALARM_EMAIL + '"')
elif (prevTemp <= MAX_TEMP) and (temp > MAX_TEMP):
  os.popen2('ssh server "echo \\\"Temperature has risen to ' + str(temp) + 'C\\\" | mail -s \\\"Vivarium Alarm\\\" ' + ALARM_EMAIL + '"')
if (prevHumid >= MIN_HUMID) and (humid < MIN_HUMID):
  os.popen2('ssh server "echo \\\"Humidity has fallen to ' + str(humid) + '%\\\" | mail -s \\\"Vivarium Alarm\\\" ' + ALARM_EMAIL + '"')
elif (prevHumid <= MAX_HUMID) and (humid > MAX_HUMID):
  os.popen2('ssh server "echo \\\"Humidity has risen to ' + str(humid) + '%\\\" | mail -s \\\"Vivarium Alarm\\\" ' + ALARM_EMAIL + '"')
