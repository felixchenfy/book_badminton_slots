
# Usage

Run the script from the command line, providing your email and password as arguments:

```bash
python main.py your_email@example.com your_password

# or schedule the script to run on Saturday 10am, by creating email_and_password.sh and running:
./run_scheduled.sh
```


# Court Booking Automation Script

Automate the booking of badminton courts at Northwest Badminton Academy with this Python script. Utilizing Selenium WebDriver, the script logs into your account, navigates the booking calendar, and attempts to reserve specified time slots based on your predefined schedule.

## Features

- **Automated Login:** Securely logs into your account using provided email and password.
- **Flexible Scheduling:** Define multiple days and time slots for booking.
- **Retry Mechanism:** Continuously attempts to book until successful or maximum retries are reached.
- **Headless Operation:** Runs without opening a browser window for seamless automation.
- **Error Handling:** Handles common exceptions and provides informative logs.

## Dependencies

- **Python 3.7+**
- **Selenium**
- **BeautifulSoup (bs4)**
- **Firefox Browser**
- **GeckoDriver:** Compatible with your Firefox version.

## Setup

1. **Install Python Packages:**

   Install the required Python packages using `pip`:

   ```bash
   pip install selenium bs4
   ```

2. **Download GeckoDriver:**

   - Download the appropriate version of [GeckoDriver](https://github.com/mozilla/geckodriver/releases) for your operating system.
   - Extract the executable and place it in the project directory or a directory included in your system's `PATH`.

3. **Ensure Firefox is Installed:**

   Make sure the Firefox browser is installed on your system.

## Configuration

1. **Define Booking Schedule:**

   Open the script and locate the `booking_schedule` variable. Define the days and times you wish to book courts.

   ```python
   booking_schedule = [("Tuesday", "8:00 PM"), ("Thursday", "8:00 PM")]
   ```

   You can modify this list to include multiple days and times as needed.

2. **Adjust Script Parameters (Optional):**

   - **Retry Settings:**

     ```python
     WAIT_SECONDS_BEFORE_RETRY = 1
     MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD = 5
     MAX_RETRIES = 600000
     DEBUG_MODE = False
     ```

     Adjust these settings based on your requirements.

   - **Headless Mode:**

     The script runs in headless mode by default. To observe the browser actions, set `headless` to `False` in the Firefox options.

     ```python
     firefox_options.headless = False
     ```

## How It Works

1. **Login:**
   - The script navigates to the login page and enters your email and password.
   - It verifies successful login by checking for specific elements on the page.

2. **Navigate to Booking Calendar:**
   - For each specified day in the `booking_schedule`, the script navigates to the corresponding date's calendar page.

3. **Attempt Booking:**
   - It searches for the specified time slots.
   - If a slot is available, the script attempts to reserve it.
   - Successful bookings are logged, and the slot is removed from the schedule.

4. **Retry Mechanism:**
   - If a booking attempt fails, the script waits for a defined interval and retries until the maximum number of retries is reached.

5. **Cleanup:**
   - After completing the booking attempts, the script closes the browser.

## Troubleshooting

- **GeckoDriver Issues:**
  - Ensure GeckoDriver is installed and its path is correctly specified.
  - Verify that the GeckoDriver version matches your Firefox browser version.

- **Login Failures:**
  - Double-check your email and password.
  - Ensure your account has the necessary permissions to book courts.

- **Element Not Found Errors:**
  - The website's structure may have changed. Inspect the website to update XPath or CSS selectors accordingly.

- **Firewall or Network Issues:**
  - Ensure your internet connection is stable and that no firewall is blocking Selenium or Firefox.

## Disclaimer

Use this script responsibly and ensure compliance with the website's terms of service. The author is not liable for any misuse or damages resulting from the use of this script.
