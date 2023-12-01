**Automate Badminton Court Booking**

This script automates booking badminton courts at your local facility using Selenium and Firefox.

**Features:**

* Supports booking multiple days and time slots, but excludes days already booked.
* Automatically retries booking if unsuccessful.
* Logs the booking process for easy tracking.

**Requirements:**

* **Firefox browser**
* **Selenium** (`pip install selenium`)
* **Geckodriver:** Download the appropriate version from [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases) and place it in the same directory as the script.

**Configuration**:

* `booking_schedule`: A list of tuples containing the desired booking day and time in 24-hour format.
* `WAIT_SECONDS_BEFORE_RETRY`: Time to wait between retries (in seconds).
* `MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD`: Maximum time to wait for webpages to load (in seconds).
* `MAX_RETRIES`: Maximum number of attempts to book a court before giving up.
* `DEBUG_MODE`: Enable extra wait time for debugging purposes.

Example:

```python
booking_schedule = [
    ('Tuesday', '8:00 PM'),
    ('Thursday', '8:00 PM'),
]
```

**Running the script:**

1. Open a terminal and navigate to the directory containing the script.
2. Run the script:

```bash
python3 main.py
```
