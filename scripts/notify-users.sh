#!/bin/bash

newline=$'\n'
timestamp=$(date)
output=$(curl https://api.parts3492.org/alerts/run/)

echo "$timestamp" "$output" "$newline" >> /home/parts3492/domains/api.parts3492.org/code/logs/log-notify-users.txt

output=$(curl https://api.parts3492.org/alerts/send/)

echo "$timestamp" "$output" "$newline" >> /home/parts3492/domains/api.parts3492.org/code/logs/log-notify-users.txt