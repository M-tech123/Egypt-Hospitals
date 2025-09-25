from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

website = "https://www.google.com/maps"
path = r"C:\Users\ms505\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
service = Service(path)
driver = webdriver.Chrome(service=service)
driver.get(website)

wait = WebDriverWait(driver, 15)

# Search for stations
search_box = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
search_box.send_keys("مستشفيات اسكندرية")
search_box.send_keys(Keys.ENTER)
time.sleep(7)

# Locate results panel
results_panel = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "m6QErb")))

# Desired number of leads
LIMIT = 50
data = []
scraped_count = 0
scroll_round = 0

while scraped_count < LIMIT:
    # Refresh the list of places (new ones may appear after scrolling)
    places = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")

    # Work on the next 10 places
    batch = places[scraped_count:scraped_count + 10]

    for idx, place in enumerate(batch, start=scraped_count + 1):
        driver.execute_script("arguments[0].scrollIntoView(true);", place)
        place.click()
        time.sleep(4)  # wait for right panel

        try:
            title = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
            ).text
        except:
            title = "N/A"

        try:
            rating = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[3]/div[9]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]",
            ).text
        except:
            rating = "N/A"

        try:
            reviews = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[3]/div[9]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span",
            ).text
        except:
            reviews = "N/A"

        try:
            website = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[9]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[5]/a").text
        except:
            website = "N/A"

        try:
            address = driver.find_element(
                By.CSS_SELECTOR, "button[data-item-id='address']"
            ).text
        except:
            address = "N/A"

        print(f"{idx}. {title} | {rating} | {address} | {reviews} | {website} ")
        data.append(
            {
                "Title": title,
                "Stars": rating,
                "Reviews": reviews,
                "Address": address,
                "Website": website,
            }
        )

        scraped_count += 1
        if scraped_count >= LIMIT:
            break

    # Scroll more to load next batch if needed
    if scraped_count < LIMIT:
        scroll_round += 1
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
        time.sleep(3)
        print(f"🔽 Scrolled round {scroll_round}, total loaded: {len(places)}")

# Save data to CSV
df = pd.DataFrame(data)
df.to_csv("Alex_Hospitals.csv", index=False, encoding="utf-8-sig")

driver.quit()
