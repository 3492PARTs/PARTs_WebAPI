#!/bin/bash

newline=$'\n'
timestamp=$(date)
output=$(curl https://parts.bduke.dev/public/notify-users/)

echo "$timestamp" "$output" "$newline" >> /home/brandon/PARTs_WebAPI/logs/log-notify-users.txt