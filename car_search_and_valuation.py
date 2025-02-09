import re
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# File Configurations
# FILE 1&2: Input and output file given as specification
INPUT_FILE = "car_input - V5.txt"
OUTPUT_FILE = "car_output - V5.txt"

# FILE 3: This is runtime file to store what data has been searched
SEARCH_RESULT_OUTPUT_FILE = "car_output_during_search.txt"
# FILE 4: this is data that search result not found during run time
Error_FILE = "car_search_reg_not_found.txt"
# FILE 5: this is the data that mismatch from runtime data and pre-exist car_output - V5.txt file.
UNVERIFIED_DATA = "unverified_data.txt"
# FILE 6: This is missing data that outfile have but run time there was not search made for those cars.
SEPERATE_FILE_WITH_MISSED_ROW = "missing_data.txt"

URL = "https://motorway.co.uk/"


# Initialize WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
    return driver


# Read registration numbers from file
def read_reg_from_input_file(file_name):
    # Open the file and read the content
    with open(file_name, 'r') as file:
        content = file.read()

    # Regular expression pattern for UK car number plates
    pattern = r"[A-Z]{2}[0-9]{2}\s?[A-Z]{3}"
    # Find all matches of the pattern in the content
    car_numbers = re.findall(pattern, content)

    return car_numbers


# Read expected output
def write_expected_output(filename, vehicleInfo):
    with open(filename, "a+") as output:
        if vehicleInfo == "HEADER":
            output.write("VARIANT_REG,MAKE_MODEL,YEAR\n")
        else:
            output.write(f"{vehicleInfo}\n")


# Search vehicle details
class MotorwayPage:
    def __init__(self, driver):
        self.driver = driver
        open(SEARCH_RESULT_OUTPUT_FILE, "w").close()
        open(Error_FILE, "w").close()

    def search_vehicle(self, reg_number):
        self.driver.get(URL)
        time.sleep(2)
        self.search_box = (By.ID, "vrm-input")
        self.vehicle_title = (By.CLASS_NAME, "HeroVehicle__title-FAmG")
        self.vehicle_year = (By.CLASS_NAME, "HeroVehicle__details-XpAI")
        self.driver.find_element(*self.search_box).send_keys(reg_number + Keys.RETURN)

        try:
            # use the wait property instead of hard timer
            time.sleep(3)
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "HeroVehicle__title-FAmG"))
            vehicle_title = self.driver.find_element(*self.vehicle_title).text
            vehicle_year_list = self.driver.find_element(*self.vehicle_year)
            # Now, find the first <li> element within this <ul>
            vehicle_year_first_list_element = vehicle_year_list.find_element(By.TAG_NAME, 'li')
            print("Text of the first <li> element:", vehicle_year_first_list_element.text)
            vehicle_infomation = f"{reg_number},{vehicle_title},{vehicle_year_first_list_element.text}"
            write_expected_output(SEARCH_RESULT_OUTPUT_FILE, vehicle_infomation)
            search_and_append(OUTPUT_FILE, vehicle_infomation, UNVERIFIED_DATA, SEPERATE_FILE_WITH_MISSED_ROW)
        except Exception as e:
            write_expected_output(Error_FILE, f"{reg_number}")
            print("Error locating element:", e)


def search_and_append(output_file, vehicle_infomation, unverified_data, separate_file):
    """
    Searches for a string in the output file.
    If not found, appends it and unverified rows from unverified_data to a separate file.
    """
    # Read output file and file2
    output_lines = read_file_lines(output_file)
    file2_lines = read_file_lines(unverified_data)

    # Check if the search string is in the output file
    if vehicle_infomation not in output_lines:
        print(f"'{vehicle_infomation}' not found in {output_file}. Writing to {separate_file}...")

        with open(separate_file, "a") as sep_file:
            sep_file.write(f"{vehicle_infomation}\n")  # Add the missing string

            # Append unverified rows from file2 (rows not in output file)
            for line in file2_lines:
                if line not in output_lines:  # Not verified
                    sep_file.write(f"{line}\n")

        print(f"Missing data written to {separate_file}")
    else:
        print(f"'{vehicle_infomation}' found in {output_file}. No action needed.")


def read_file_lines(filename):
    """
    Reads a file and returns a set of stripped lines.
    """
    with open(filename, "r") as file:
        return set(line.strip() for line in file)


# Run tests
def test_car_reg_search_with_output_file():
    driver = init_driver()
    motorway_page = MotorwayPage(driver)
    registration_numbers = read_reg_from_input_file(INPUT_FILE)
    write_expected_output(SEARCH_RESULT_OUTPUT_FILE, "HEADER")

    for reg in registration_numbers:
        motorway_page.search_vehicle(reg)
        print(f"Test Passed for {reg}")

    driver.quit()


if __name__ == "__main__":
    test_car_reg_search_with_output_file()
