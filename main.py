import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import subprocess

# WARNING: This is to avoid creating multiple icons
subprocess.run(
    ["killall", "firefox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

# --------------------

# -- Parse command line arguments
parser = argparse.ArgumentParser(description="Automate booking process.")
parser.add_argument("email", help="Email address for login")
parser.add_argument("password", help="Password for login")
args = parser.parse_args()

email_address = args.email
password = args.password

# --- Input Variables

# Desired days and times
# booking_schedule = [('Tuesday', '7:00 PM'), ('Thursday', '7:00 PM'), ('Tuesday', '8:00 PM'), ('Thursday', '8:00 PM')]
# booking_schedule = [('Monday', '8:00 PM'), ('Monday', '9:00 PM')]
booking_schedule = [("Tuesday", "8:00 PM"), ("Thursday", "8:00 PM")]
# booking_schedule = [('Thursday', '7:00 PM'), ('Thursday', '8:00 PM')]
# booking_schedule = [('Monday', '9:00 AM'), ('Sunday', '4:00 PM')]
# booking_schedule = [('Friday', '8:00 PM')]

# WAIT_SECONDS_BEFORE_RETRY = 30
WAIT_SECONDS_BEFORE_RETRY = 1
MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD = 5
MAX_RETRIES = 600000
DEBUG_MODE = False  # Sleep extra 2s before any click.

# --- Constants
LOGIN_URL = "https://northwestbadmintonacademy.sites.zenplanner.com/login.cfm"
BASE_URL = "https://northwestbadmintonacademy.sites.zenplanner.com/calendar.cfm?DATE="
TIME_SLOT_XPATH = (
    "//tr[@class='item']/td[@class='label']/div[contains(@class, 'clickable')]"
)


def sleep(t):
    if DEBUG_MODE:
        time.sleep(t + 2)  # Extra wait for debugging
    else:
        time.sleep(t)


if 0:
    # Setup WebDriver.
    # Here I choose to use firefox.
    firefox_options = Options()
    firefox_options.set_capability("detach", True)
    driver = webdriver.Firefox(executable_path="./geckodriver", options=firefox_options)
else:
    # Setup WebDriver using Service
    firefox_options = Options()

    firefox_options.headless = True
    # profile_path = "/Users/feiyuc/Library/Caches/Firefox/Profiles/81ytv4a3.default-release"
    # firefox_profile = webdriver.FirefoxProfile(profile_path)
    # firefox_options.profile = firefox_profile
    # firefox_options.add_argument("-profile")
    # firefox_options.add_argument("/tmp/my_firefox_profile_tmp")
    # firefox_options.set_preference("profile", "/tmp/my_firefox_profile_tmp")
    # firefox_options.add_argument("-profile")
    # firefox_options.add_argument("/tmp/selenium_firefox_profile")
    # Specify the path to geckodriver

    gecko_service = Service("./geckodriver")

    # Initialize the Firefox driver with the Service object
    # driver = webdriver.Firefox(service=gecko_service, options=firefox_options)
    # Initialize the Firefox driver with the profile
    driver = webdriver.Firefox(service=gecko_service, options=firefox_options)

# --------------------
# Methods


def login():
    print("Navigating to login page.")
    driver.get(LOGIN_URL)

    try:
        # Wait for the username field to be present and then fill in the credentials
        WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
            EC.presence_of_element_located((By.ID, "idUsername"))
        )
        driver.find_element(By.ID, "idUsername").send_keys(email_address)
        driver.find_element(By.ID, "idPassword").send_keys(password)

        # Find and click the login button
        submit_button = driver.find_element(
            By.CSS_SELECTOR, "input.btn-primary[type='submit']"
        )
        sleep(0.01)
        submit_button.click()

        # Wait for a response from the server
        WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
            lambda driver: driver.find_element(By.TAG_NAME, "body")
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
    target_day = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }.get(day, current_day.weekday())
    day_difference = (target_day - current_day.weekday()) % 7
    target_date = current_day + timedelta(days=day_difference)
    return f'{BASE_URL}{target_date.strftime("%Y-%m-%d")}'


def is_slot_booked(time_slot_text):
    # Convert the page source into a BeautifulSoup object for easier parsing
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find all the time slot rows in the table
    slot_rows = soup.find_all("tr", class_="item")

    for row in slot_rows:
        # Extract time and reservation status from each row
        time = row.find("div", class_="clickable").text.strip()
        reservation_status = row.find_all("td")[-1].text.strip()

        # Check if the time matches and if it's reserved
        if time == time_slot_text and "Reserved" in reservation_status:
            return True

    return False


from selenium.webdriver.common.by import By


def book_court(day, time_slot_text):
    """
    Return 1 if succeeded.
    Return -1 if failed and need retry.
    """
    day_url = get_url_for_day(day)
    print("")
    print(f"Going to the webpage for {day} ({day_url})")
    driver.get(day_url)
    try:
        WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
            EC.presence_of_element_located((By.XPATH, TIME_SLOT_XPATH))
        )  # Update to use By.XPATH
        time_slots = driver.find_elements(
            By.XPATH, TIME_SLOT_XPATH
        )  # Use the new find_elements() with By.XPATH
        for slot in time_slots:
            if time_slot_text in slot.text:
                print(f"Attempting to book the time slot for {time_slot_text}")
                if is_slot_booked(time_slot_text):
                    return 0  # Already booked
                elif "sessionFull" in slot.get_attribute("class"):
                    print(f"Slots are full.")
                else:
                    print(f"Slots are not full. Try to click.")
                    slot.click()
                    sleep(0.01)
                    WebDriverWait(driver, MAX_WAIT_SECONDS_FOR_PAGE_TO_LOAD).until(
                        EC.element_to_be_clickable((By.ID, "reserve_1"))
                    ).click()  # Update to use By.ID
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
            EC.presence_of_element_located((By.ID, "idPersonRegistered"))
        )
        return (
            "is registered for this class"
            in driver.find_element(By.ID, "idPersonRegistered").text
        )
    except TimeoutException:
        print("No confirmation received for reservation.")
        return False



# --------------------
# Main

try:
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
            if res >= 0:
                if res == 1:
                    print(f"Successfully booked for {day} at {time_slot}!")
                else:
                    print(f"This slot was already booked: {day} at {time_slot}!")
                # Remove successful booking
                booking_schedule.remove((day, time_slot))
            elif res == -1:
                print(f"Failed to book for {day} at {time_slot}, will retry.")
            else:
                print("Unknown error code: ", res)
                print(f"Failed to book for {day} at {time_slot}, will retry.")
        print("----------------------------------------------")
        print("\n")
        sleep(WAIT_SECONDS_BEFORE_RETRY)
finally:
    print("----------------------------------------------")
    print(f"Remaining bookings: {len(booking_schedule)}")

    driver.quit()
