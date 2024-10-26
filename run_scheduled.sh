#!/bin/bash

# Variables for the target day and time
TARGET_WEEKDAY=6  # Saturday
TARGET_HOUR=10    # 10 AM (24-hour format)

# Function to calculate the number of seconds until the target day and time in Seattle time
calculate_sleep_duration() {
    # Use the Python script provided to calculate the sleep duration
    echo $(python -c "
import pytz
from datetime import datetime, timedelta

# Current time in Seattle timezone
seattle_time = datetime.now(pytz.timezone('America/Los_Angeles'))

# Target weekday and hour
target_weekday = $TARGET_WEEKDAY
target_hour = $TARGET_HOUR

# Calculate days ahead to the target weekday
days_ahead = (target_weekday - 1 + 7 - seattle_time.weekday()) % 7
if days_ahead == 0 and seattle_time.hour >= target_hour:
    days_ahead = 7

# Set target time
target_time = seattle_time + timedelta(days=days_ahead)
target_time = target_time.replace(hour=target_hour, minute=0, second=0, microsecond=0)

# Calculate and print the sleep duration in seconds
print(int((target_time - seattle_time).total_seconds()))
")
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
# Convert seconds to hours, minutes, seconds
formatted_duration=$(convert_seconds $sleep_duration)
echo "Sleeping for another $formatted_duration..."

# Loop until the sleep duration is zero or negative
while [ $sleep_duration -gt 0 ]; do
    echo "--- Current Seattle time: $(TZ='America/Los_Angeles' date)"

    # Break the loop if sleep duration is less than or equal to 600 seconds
    if [ $sleep_duration -le 600 ]; then
        echo "Breaking out of the loop as the remaining time is less than or equal to 600 seconds."
        break
    fi

    # Sleep for 1 minute
    sleep 60

    # Recalculate sleep duration
    sleep_duration=$(calculate_sleep_duration)

    # Convert seconds to hours, minutes, seconds
    formatted_duration=$(convert_seconds $sleep_duration)

    # Print a message with the remaining sleep duration
    echo "Sleeping for another $formatted_duration..."
done


# After the loop ends, run the task
python3 main.py felixchenfy@gmail.com xxx
