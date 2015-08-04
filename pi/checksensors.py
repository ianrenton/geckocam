#! /usr/bin/env python3

# Vivarium monitoring sensor script. Run by a cron job. Reads temperature and
# humidity values, stores them in a log file.

# Written by Ian Renton (http://ianrenton.com)

from datetime import datetime
import os
import AM2315 as a

# Constants
TIME_FORMAT = "%Y-%m-%d-%H-%M-%S"

# Acquire data
temp = 0
humid = 0
while (temp == 0) or (humid == 0): # fetching temp and humid sometimes fails so repeat until successful
  sensor=a.AM2315()
  temp = sensor.temperature()
  humid = sensor.humidity()

# Write data to file
csvdata = datetime.now().strftime(TIME_FORMAT) + ',' + str(temp) + ',' + str(humid) + '\n'
with open("sensordata.csv", "a") as myfile:
  myfile.write(csvdata)
