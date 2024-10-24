
"""
# Open LinkedIn profile page
profile_url = "https://www.vlaio.be/nl/begeleiding-advies/financiering/risicokapitaal/zoek"
driver.get(profile_url)
#wait for the page to be loaded fully
time.sleep(5)

# a chatbot can occur (just for visuals)
try:
    # Find the button
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/button')))

    # Do something with the button (e.g., click it)
    button.click()
except:
    None

# cookie asking can occur (just for visuals)
try:
    # Find the button
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll"]')))

    # Do something with the button (e.g., click it)
    button.click()
except:
    None

# load all the whole page:
while True:
    try:
        # scroll down (just for the visuals
        scroll_down(driver)

        # Find the button
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="block-vlaio-content"]/div/div/ul/li/a')))

        # Do something with the button (e.g., click it)
        button.click()

        # Refresh the page to load the next set of elements
        time.sleep(2)

    except:
        # If the button is not found or stale, break out of the loop
        break

time.sleep(2)
#scroll up:
scroll_up(driver)

# click second one for the demo
time.sleep(2)
links = driver.find_elements(By.XPATH, '//*[@id="block-vlaio-content"]/div/div/div[2]/div[1]/article/a')

# TODO: normally you need a for loop here but i will demonstrate second one for now
driver.get(links[0].get_attribute('href'))

time.sleep(2)
scroll_down(driver)
time.sleep(2)
# click on the website
# Find the element containing the website link
website_element = driver.find_element(By.XPATH, "//div[@class='field--field-website']//a[@class='ext']")

#click
website_element.click()

time.sleep(3)

driver.quit()



"""


