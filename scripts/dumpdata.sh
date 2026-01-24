#!/bin/bash

# Directory to look for the dump.request file
DIRECTORY="DEPLOY_PATH"

# Check if the directory variable is provided
if [ -z "$DIRECTORY" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

# File to look for
REQUEST_FILE="$DIRECTORY/dump.request"
OUTPUT_FILE="$DIRECTORY/dump.json"
VENV_PATH="$DIRECTORY/venv"

# Check if dump.request file exists
if [ -f "$REQUEST_FILE" ]; then
  echo "Found $REQUEST_FILE. Processing..."

  # Activate Python virtual environment
  source "$VENV_PATH/bin/activate"

  # Run the dumpdata command and direct output to dump.json
  python manage.py dumpdata > "$OUTPUT_FILE"

  # Check if the dumpdata command was successful
  if [ $? -eq 0 ]; then
    echo "Data dumped successfully to $OUTPUT_FILE."
    # Remove the dump.request file
    rm "$REQUEST_FILE"
    echo "$REQUEST_FILE deleted."
  else
    echo "Failed to dump data. Please check your setup."
  fi

  # Deactivate Python virtual environment
  deactivate
else
  echo "$REQUEST_FILE not found. Exiting."
fi