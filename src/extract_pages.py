from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import logging
from datetime import datetime

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
start_time = datetime.now()
logging.info(f"Process started at {start_time}")
start_timestamp = time.time()

driver_path = r"C:\Users\Prezes\Downloads\chromedriver-win64\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument("--headless")  # Uncomment to run without opening a visible browser window
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    with open('src/links.json', 'r') as f:
        data = json.load(f)
        
    links = data['football'][0]['links']
    seasons = ['2020-2021', '2021-2022', '2022-2023', '2023-2024']

    for link in links:
        for season in seasons:
            url = f'{link}-{season}/wyniki/'
            logging.info(f'Loading page: {url}')

            driver.get(url)

            wait = WebDriverWait(driver, 3) # if element won't be found in 3 seconds then stop while loop (below)

            def scroll_to_element(element):
                driver.execute_script("arguments[0].scrollIntoView(true);", element)

            while True:
                try:
                    load_more_button = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "event__more") and contains(@class, "event__more--static")]'))
                    )

                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)

                    load_more_button.click()
                    logging.debug("Button clicked to load more matches.")
                    
                    time.sleep(0.7)

                except Exception as e:
                    logging.info("No more matches to load or button is missing.", exc_info=e)
                    break

            page_source = driver.page_source
            file_name = f'data/raw_html/{url.split("/")[-3]}_{url.split("/")[-2]}.txt'
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(page_source)

            logging.info(f"Page content saved to '{file_name}'.")
finally:
    driver.quit()
    logging.info("Driver closed.")

    end_time = datetime.now()
    end_timestamp = time.time()
    duration = end_timestamp - start_timestamp

    logging.info(f"Process finished at {end_time}")
    logging.info(f"Total process duration: {duration:.2f} seconds")