#!/bin/bash

# README:
# This script calculates the time until a specific day/hour (Seattle timezone),
# sleeps until then, and runs a Python task (`main.py`) with email credentials.
# 
# - **Target Day/Time:** Set by `TARGET_WEEKDAY` (0=Mon, 6=Sun) and `TARGET_HOUR` (24-hour).
# - **Dependencies:** Python 3, `pytz`.
# - **Usage:** Make the script executable (`chmod +x script.sh`) and run it: `./script.sh`.
# - **Note:** Ensure `main.py` exists and `email_and_password.sh` provides `$my_email` and `$my_password`.

# Variables for the target day and time
TARGET_WEEKDAY=5  # Saturday (0=Monday, 6=Sunday)
TARGET_HOUR=10     # 10 AM (24-hour format)

# Function to calculate the number of seconds until the target day and time in Seattle time
calculate_sleep_duration() {
    python3 - <<EOF
import pytz
from datetime import datetime, timedelta
import sys

# Current time in Seattle timezone
seattle_tz = pytz.timezone('America/Los_Angeles')
seattle_time = datetime.now(seattle_tz)

# Target weekday and hour
# Python's weekday(): Monday=0, Sunday=6
target_weekday = $TARGET_WEEKDAY
target_hour = $TARGET_HOUR

# Calculate days ahead to the target weekday
days_ahead = (target_weekday - seattle_time.weekday() + 7) % 7

# If target is today and current time is past target_hour, set to next week
if days_ahead == 0 and seattle_time.hour >= target_hour:
    days_ahead = 7

# Calculate target time
target_time = seattle_time + timedelta(days=days_ahead)
target_time = target_time.replace(hour=target_hour, minute=0, second=0, microsecond=0)

# Print Seattle time and Target time to stderr for debugging
print(f"Seattle Time: {seattle_time.strftime('%Y-%m-%d %H:%M:%S %Z')}", file=sys.stderr)
print(f"Target Time: {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}", file=sys.stderr)

# Calculate and print the sleep duration in seconds
sleep_duration = int((target_time - seattle_time).total_seconds())
print(sleep_duration)
EOF
}

# Function to convert seconds to hours, minutes, seconds
convert_seconds() {
    local total_seconds=$1
    local hours=$((total_seconds / 3600))
    local minutes=$(( (total_seconds % 3600) / 60 ))
    local seconds=$((total_seconds % 60))
    echo "$hours hours $minutes minutes $seconds seconds"
}

# Calculate initial sleep duration
sleep_duration=$(calculate_sleep_duration)

# Ensure sleep_duration is valid and a number
if ! [[ "$sleep_duration" =~ ^[0-9]+$ ]]; then
    echo "Error: Invalid sleep duration calculated."
    exit 1
fi

# Convert seconds to hours, minutes, seconds
formatted_duration=$(convert_seconds "$sleep_duration")
echo "Sleeping for another $formatted_duration..."

# Loop until the sleep duration is less than or equal to 180 seconds (3 minutes)
while [ "$sleep_duration" -gt 180 ]; do
    # Display current Seattle time
    echo "--- Current Seattle time: $(TZ='America/Los_Angeles' date)"

    # Sleep for 1 minute
    sleep 60

    # Recalculate sleep duration
    sleep_duration=$(calculate_sleep_duration)

    # Ensure sleep_duration is valid and a number
    if ! [[ "$sleep_duration" =~ ^[0-9]+$ ]]; then
        echo "Error: Invalid sleep duration calculated."
        exit 1
    fi

    # Convert seconds to hours, minutes, seconds
    formatted_duration=$(convert_seconds "$sleep_duration")

    # Print a message with the remaining sleep duration
    echo "Sleeping for another $formatted_duration..."
done

# Execute the scheduled task
echo "Executing the scheduled task..."
source email_and_password.sh
python3 main.py $my_email $my_password