import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to ChromeDriver
chromedriver_path = "C:\\Users\\sanju\\OneDrive\\Desktop\\web scraping\\chromedriver.exe"

# Start WebDriver
service = Service(chromedriver_path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# Open the website
url = "https://sec2021.bihar.gov.in/claim-objection/Result1.aspx?D=0&PO=1"
driver.get(url)
wait = WebDriverWait(driver, 10)

# Storage for extracted data
data_list = []
missing_data_list = []

# Function to extract data
def extract_data():
    try:
        # Example: Selecting dropdowns (Modify XPaths as per your script)
        district_dropdown = Select(wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_ddlDistrict"]'))))
        block_dropdown = Select(wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_ddlBlock"]'))))
        filter_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnFilter"]')))

        # Loop through all districts
        for district in district_dropdown.options[1:]:  # Skip first option (default)
            district_text = district.text.strip()
            district_dropdown.select_by_visible_text(district_text)
            time.sleep(2)

            # Loop through all blocks
            for block in block_dropdown.options[1:]:
                block_text = block.text.strip()
                block_dropdown.select_by_visible_text(block_text)
                time.sleep(2)

                # Click filter button
                filter_button.click()
                time.sleep(3)

                # Extract data from table
                rows = driver.find_elements(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_RPDetails"]/table/tbody/tr')

                for row in rows:
                    columns = row.find_elements(By.TAG_NAME, "td")
                    if len(columns) >= 4:  # Ensure enough columns exist
                        candidate_name = columns[0].text.strip()
                        post_name = columns[1].text.strip()
                        ward_name = columns[2].text.strip()
                        votes = columns[3].text.strip()

                        # Store extracted data
                        data_list.append([district_text, block_text, ward_name, candidate_name, post_name, votes])

                        # Check for missing values
                        if not district_text or not block_text or not ward_name or not candidate_name:
                            missing_data_list.append([district_text, block_text, ward_name, candidate_name, post_name, votes])

                print(f"Extracted data for District: {district_text}, Block: {block_text}")

    except Exception as e:
        print(f"Error occurred: {e}")

# Run extraction function
extract_data()

# Save extracted data
df = pd.DataFrame(data_list, columns=["District", "Block", "Ward", "Candidate Name", "Post", "Votes"])
df.to_csv("extracted_data.csv", index=False, encoding="utf-8")
print("✅ Data extraction completed and saved!")

# Save missing values
if missing_data_list:
    df_missing = pd.DataFrame(missing_data_list, columns=["District", "Block", "Ward", "Candidate Name", "Post", "Votes"])
    df_missing.to_csv("missing_data.csv", index=False, encoding="utf-8")
    print("⚠️ Missing data logged in missing_data.csv")
else:
    print("✅ No missing values found!")

# Close the browser
driver.quit()
