#! /usr/bin/env python3

# Vivarium monitoring sensor script. Run by a cron job. Reads temperature and
# humidity values, stores them in a log file.

# Written by Ian Renton (http://ianrenton.com)

from datetime import datetime
import numpy
import AM2315 as a

# Constants
TIME_FORMAT = "%Y-%m-%d-%H-%M-%S"

# Acquire data. Grab several values and calculate the median to strip out any
# outliers that sometimes occur.
temps = []
humids = []
for num in range(1,20):
  sensor=a.AM2315()
  temps.append(sensor.temperature())
  humids.append(sensor.humidity())
temp = numpy.median(temps)
humid = numpy.median(humids)

# Write data to file
csvdata = datetime.now().strftime(TIME_FORMAT) + ',' + str(temp) + ',' + str(humid) + '\n'
with open("sensordata.csv", "a") as myfile:
  myfile.write(csvdata)
