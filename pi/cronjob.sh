#! /bin/bash

# Vivarium monitoring cron job. Run every 15 minutes.
# Takes a photo, timestamps it, runs the python script to acquire data
# and generate charts, then uploads them all to the web server.

# Written by Ian Renton (http://ianrenton.com)

# Take photo
raspistill -w 600 -h 400 -ex night -o photo-raw.jpg
convert "photo-raw.jpg" -pointsize 24 -fill white -annotate +10+365 "Gecko Cam 1\n%[exif:DateTimeOriginal]" "photo.jpg"

# Acquire data - sensor lib requires Python 3
python3 checksensors.py

# Separate script to draw graphs (and send emails) - matplotlib requires Python 2!
python drawgraphs.py

# Write some stats
echo "<u>Rimbaud Monitoring System status</u><br/>$(/usr/bin/uptime)<br/>" > stats.html
echo "$(/usr/bin/whoami)@$(/bin/hostname) " >> stats.html
echo "($(/sbin/ifconfig wlan0 | grep addr: | awk -F: '{print $2}' | awk '{print $1}'))<br/>" >> stats.html
echo "Sensor data file size: $(stat -c %s sensordata.csv) bytes<br/>" >> stats.html
echo "Disk space used: $(df -h | grep rootfs | awk '{print $3}'), remaining: $(df -h | grep rootfs | awk '{print $4}')" >> stats.html

# Upload everything
scp photo.jpg server:/srv/www/rimbaud/upload/
scp temp.png server:/srv/www/rimbaud/upload/
scp humid.png server:/srv/www/rimbaud/upload/
scp stats.html server:/srv/www/rimbaud/upload/
