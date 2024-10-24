from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import time
from pathlib import Path
"""tip: from now on, update this with Selenium IDE, as this gives you the opportunity to interact with
the website and it records the actions and create the code"""

def test_headless():
    #dependencies
    # Determine the script directory
    script_dir = Path(__file__).resolve().parent

    # Path to the unique_id.txt file
    unique_id_file = script_dir / 'unique_id.txt'

    # Ensure the file exists before trying to read it
    assert unique_id_file.exists(), "no unique id file to delete the subsystem!"

    # Get unique id from the file
    with unique_id_file.open('r') as f:
        unique_test_id = f.read().strip()

    # Initialize Selenium webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')
    driver = webdriver.Chrome(options=options)

    # Open the website
    # profile_url = "https://www.collimundo.com"
    profile_url = "http://127.0.0.1:3034"  # todo: if <TEST_PORT> changed in cicd this will fail..

    driver.get(profile_url)

    # try to edit dashboard -> login will appear
    pop_up_close_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="edit-dashboard-button"]')))
    pop_up_close_button.click()

    # login with test account
    input_field = driver.find_element(By.XPATH, '//*[@id="username"]')
    input_field.send_keys("test@test.be")
    time.sleep(1)
    input_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    input_field.send_keys("#Testking")
    time.sleep(2)
    # Press login button
    pop_up_close_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/main/div/form/button')))
    pop_up_close_button.click()

    # test if the dashboard has elements and you can edit:
    pop_up_close_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dashboard-selection-1"]')))
    # Click the button
    pop_up_close_button.click()

    # check availability of widget(s) -> outcommented due to latencies :(
    # driver.find_element(By.XPATH, '//*[@id="widget-1_0"]')

    # also test if you can edit dashboards when logged in:
    # Wait for the button to be clickable
    pop_up_close_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="edit-dashboard-button"]')))
    # Click the button
    pop_up_close_button.click()

    # find if there are some widgets
    # driver.find_element(By.XPATH, '//*[@id="dashboard-2"]/div[2]/div[1]/div[1]')
    time.sleep(2)

    # leave
    pop_up_close_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="return-button"]')))
    pop_up_close_button.click()
    time.sleep(2)

    # integration testing: Test availability of search engine, and if it returns something (-> database availability)
    # Find the button
    button = driver.find_element(By.XPATH, '//*[@id="search-input"]')
    button.click()
    # Refresh the page to load the next set of elements
    time.sleep(3)
    input_field = driver.find_element(By.XPATH,
                                      '//*[@id="search-input"]')  # Replace 'input_field_id' with the actual ID of the input field
    input_field.send_keys(f"collimundotest_{unique_test_id}")
    time.sleep(1)
    # Press the 'Enter' key to submit
    input_field.send_keys(Keys.ENTER)

    # Find the button (automatically also check if there are results -> search engine works)
    # Locate the first hyperlink within the result container

    """
    button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="results-container"]/div[1]/div[2]/div[1]/a')))
    # Do something with the button (e.g., click it)
    button.click()
    time.sleep(10)

    # check if you can follow
    # Find the button (change time out if we want a hard loading time limit in our tests
    button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="follow-btn"]')))
    # Do something with the button (e.g., click it)
    button.click()
    time.sleep(2)

    # end with checking if you follow this?
    # Find the button
    button = driver.find_element(By.XPATH, '//*[@id="navbarSupportedContent"]/ul/li[1]/a')
    button.click()

    time.sleep(20)
    # click on the collimundo result
    button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "company-cards"] / div / div / a / div / h1')))
    button.click()

    # unfollow for next tests
    button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "unfollow-btn"]')))
    button.click()

    # driver.find_element(By.XPATH, '//*[@id="logo_collimundo"]')
    """
    driver.quit()


