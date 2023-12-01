import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
import time

# --------------------

# -- Parse command line arguments
parser = argparse.ArgumentParser(description='Automate booking process.')
parser.add_argument('email', help='Email address for login')
parser.add_argument('password', help='Password for login')
args = parser.parse_args()

email_address = args.email
password = args.password

# --- Input Variables

# Desired days and times
# booking_schedule = [('Tuesday', '7:00 PM'),
#                     ('Thursday', '7:00 PM')]
# booking_schedule = [('Friday', '10:00 PM'),
#                     ('Saturday', '10:00 PM')]
booking_schedule = [('Friday', '9:00 PM'),
                    ('Saturday', '9:00 AM')]

WAIT_SECONDS_BEFORE_RETRY = 1
MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD = 3
MAX_RETRIES = 1000
DEBUG_MODE = False  # Sleep extra 2s before any click.

# --- Constants
LOGIN_URL = "https://northwestbadmintonacademy.sites.zenplanner.com/login.cfm"
BASE_URL = "https://northwestbadmintonacademy.sites.zenplanner.com/calendar.cfm?DATE="
TIME_SLOT_XPATH = "//tr[@class='item']/td[@class='label']/div[contains(@class, 'clickable')]"


def sleep(t):
    if DEBUG_MODE:
        time.sleep(t + 2)  # Extra wait for debugging
    else:
        time.sleep(t)


# Setup WebDriver.
# Here I choose to use firefox.
firefox_options = Options()
firefox_options.set_capability("detach", True)
driver = webdriver.Firefox(
    executable_path='./geckodriver', options=firefox_options)

# --------------------
# Methods


def login():
    print("Navigating to login page.")
    driver.get(LOGIN_URL)

    try:
        # Wait for the username field to be present and then fill in the credentials
        WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
            EC.presence_of_element_located((By.ID, 'idUsername')))
        driver.find_element_by_id('idUsername').send_keys(email_address)
        driver.find_element_by_id('idPassword').send_keys(password)

        # Find and click the login button
        submit_button = driver.find_element_by_css_selector(
            "input.btn-primary[type='submit']")
        sleep(0.01)
        submit_button.click()

        # Wait for a response from the server
        WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
            lambda driver: driver.find_element_by_tag_name('body')
        )

        # Check for the error message
        sleep(0.01)
        error_message = "Please check your email address and password and try again."
        if error_message in driver.page_source:
            print("Login failed: Incorrect email address or password.")
            driver.quit()
            exit(1)

        print("Login successful.")
    except Exception as e:
        print(f"An error occurred during login: {e}")
        driver.quit()
        exit(1)


def get_url_for_day(day):
    current_day = datetime.now()
    target_day = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                  'Friday': 4, 'Saturday': 5, 'Sunday': 6}.get(day, current_day.weekday())
    day_difference = (target_day - current_day.weekday()) % 7
    target_date = current_day + timedelta(days=day_difference)
    return f'{BASE_URL}{target_date.strftime("%Y-%m-%d")}'


def check_already_registered():
    return "Reserved" in driver.page_source


def book_court(day, time_slot_text):
    '''
    Return 1 if succeeded.
    Return -1 if failed and need retry.
    Return 0 if you already booked a court on this day and shouldn't book again.
    '''
    day_url = get_url_for_day(day)
    print("")
    print(f"Going to the webpage for {day} ({day_url})")
    driver.get(day_url)
    try:
        WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
            EC.presence_of_element_located((By.XPATH, TIME_SLOT_XPATH)))
        if check_already_registered():
            return 0

        time_slots = driver.find_elements_by_xpath(TIME_SLOT_XPATH)
        for slot in time_slots:
            if time_slot_text in slot.text:
                print(f"Attempting to book the time slot for {time_slot_text}")
                if 'sessionFull' in slot.get_attribute('class'):
                    print(f"Slots are full.")
                else:
                    print(f"Slots are not full. Try to click.")
                    slot.click()
                    sleep(0.01)
                    WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
                        EC.element_to_be_clickable((By.ID, 'reserve_1'))).click()
                    if check_reservation_confirmation():
                        return 1
                    else:
                        return -1

    except TimeoutException:
        print("Timed out waiting for page to load or element to be available")
    except NoSuchElementException:
        print("Element not found on page")
    return -1


def check_reservation_confirmation():
    print("Checking for reservation confirmation...")
    try:
        WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
            EC.presence_of_element_located((By.ID, 'idPersonRegistered')))
        return "is registered for this class" in driver.find_element_by_id('idPersonRegistered').text
    except TimeoutException:
        print("No confirmation received for reservation.")
        return False

# --------------------
# Main


login()
print("\n\n")

num_retries = 0
for num_retries in range(MAX_RETRIES):
    if len(booking_schedule) == 0:
        break
    print("----------------------------------------------")
    print(f"Attempt: {num_retries + 1}/{MAX_RETRIES}")
    print(f"Remaining bookings: {len(booking_schedule)}")
    for idx, (day, time_slot) in enumerate(booking_schedule):
        print(f"{idx + 1}. Day: {day}, Time: {time_slot}")
    print()

    # Iterate over a copy of the list
    for day, time_slot in list(booking_schedule):
        res = book_court(day, time_slot)
        if res == 1:
            print(f"Successfully booked for {day} at {time_slot}!")
            # Remove successful booking
            booking_schedule.remove((day, time_slot))
        elif res == 0:
            print(f"You already booked a court on {day}."
                  " You can't book anymore, even if it's a different slot.")
            booking_schedule.remove((day, time_slot))
        elif res == -1:
            print(f"Failed to book for {day} at {time_slot}, will retry.")
        else:
            print("Unknown error code: ", res)
            print(f"Failed to book for {day} at {time_slot}, will retry.")
    print("----------------------------------------------")
    print("\n")
    sleep(WAIT_SECONDS_BEFORE_RETRY)

print("----------------------------------------------")
print(f"Remaining bookings: {len(booking_schedule)}")

driver.quit()
