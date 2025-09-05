#!/bin/bash

newline=$'\n'
timestamp=$(date)
output=$(curl DEPLOY_URL/tba/sync-event-team-info/)

echo "$timestamp" "$output" "$newline" >> DEPLOY_PATH/logs/log-sync-event-team-info.txt