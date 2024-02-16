#!/bin/bash

newline=$'\n'
timestamp=$(date)
output=$(curl https://api.parts3492.org/scouting/admin/sync-event-team-info/)

echo "$timestamp" "$output" "$newline" >> /home/brandon/PARTs_WebAPI/logs/log-sync-event-team-info.txt
