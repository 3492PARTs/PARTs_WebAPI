#!/bin/bash

newline=$'\n'
timestamp=$(date)
output=$(curl DEPLOY_URL/alerts/stage/)

echo "$timestamp" "$output" "$newline" >> DEPLOY_PATH/logs/log-notify-users.txt

output=$(curl DEPLOY_URL/alerts/send/)

echo "$timestamp" "$output" "$newline" >> DEPLOY_PATH/logs/log-notify-users.txt