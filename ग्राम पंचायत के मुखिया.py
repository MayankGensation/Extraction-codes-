from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Setup WebDriver
chrome_driver_path = r"C:\Users\sanju\OneDrive\Desktop\web scraping\chromedriver.exe"
url = "https://sec2021.bihar.gov.in/claim-objection/Result11.aspx?D=0&PO=1"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)

wait = WebDriverWait(driver, 3)
time.sleep(2)  # Allow page to load

# Function to extract dropdown options
def get_dropdown_options(dropdown_xpath):
    try:
        dropdown = wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
        return [opt.text.strip() for opt in Select(dropdown).options if opt.text.strip() not in ["Select", "--select--"]]
    except:
        return []

# Function to select dropdown option
def select_dropdown_option(dropdown_xpath, value):
    try:
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
        Select(dropdown).select_by_visible_text(value)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", dropdown)
        time.sleep(2)  # Wait for dependent dropdowns to update
    except:
        print(f"⚠️ Unable to select {value}. Skipping.")

# Function to handle pop-ups
def close_popups():
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
        print("⚠️ Closed pop-up alert.")
    except:
        pass  # No pop-up detected

# Load previously saved data to resume
csv_file = "gram_panchayat_mukhiya_results(11).csv"
completed_entries = set()
if os.path.exists(csv_file):
    existing_data = pd.read_csv(csv_file, encoding="utf-8-sig")
    for _, row in existing_data.iterrows():
        completed_entries.add(tuple(row[:3]))  # Store completed (District, Block, Panchayat)

# Select "ग्राम पंचायत के मुखिया"
try:
    select_dropdown_option('//*[@id="ctl00_ContentPlaceHolder1_ddl_Post"]', "ग्राम पंचायत के मुखिया")
except Exception as e:
    print(f"❌ Failed to select 'ग्राम पंचायत के मुखिया': {e}")
    driver.quit()
    exit()

# Get all districts and prioritize गोपालगंज
districts = get_dropdown_options('//*[@id="ctl00_ContentPlaceHolder1_ddlDistrict"]')
districts.remove("गोपालगंज") if "गोपालगंज" in districts else None
districts.insert(0, "गोपालगंज")  # Move गोपालगंज to the first position

all_data = []
for district in districts:
    try:
        select_dropdown_option('//*[@id="ctl00_ContentPlaceHolder1_ddlDistrict"]', district)
        blocks = get_dropdown_options('//*[@id="ctl00_ContentPlaceHolder1_ddlBlock"]')
    except:
        print(f"⚠️ No blocks found for {district}. Skipping.")
        continue

    for block in blocks:
        select_dropdown_option('//*[@id="ctl00_ContentPlaceHolder1_ddlBlock"]', block)
        panchayats = get_dropdown_options('//*[@id="ctl00_ContentPlaceHolder1_ddlPanchayat"]')

        for panchayat in panchayats:
            if (district, block, panchayat) in completed_entries:
                print(f"⏭️ Skipping already extracted: {district} > {block} > {panchayat}")
                continue

            select_dropdown_option('//*[@id="ctl00_ContentPlaceHolder1_ddlPanchayat"]', panchayat)
            close_popups()  # Handle pop-ups

            # Click the "Filter" button
            try:
                filter_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnFilter"]')))
                driver.execute_script("arguments[0].click();", filter_button)
                time.sleep(3)
            except Exception as e:
                print(f"❌ Failed to click filter button: {e}")
                continue

            # Extract table data
            try:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_RPDetails"})
                if table:
                    headers = [th.text.strip() for th in table.find_all("th")]
                    rows = [[td.text.strip() for td in row.find_all("td")] for row in table.find_all("tr")[1:]]

                    for row in rows:
                        row.insert(0, panchayat)
                        row.insert(0, block)
                        row.insert(0, district)
                        all_data.append(row)

                    print(f"✅ Extracted data for {district} > {block} > {panchayat}")

                    # Save immediately to avoid data loss
                    df = pd.DataFrame(all_data, columns=["District", "Block", "Panchayat"] + headers)
                    df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False, encoding="utf-8-sig")

                    completed_entries.add((district, block, panchayat))  # Mark as completed
                    all_data.clear()  # Clear buffer after saving
                else:
                    print(f"⚠️ No table found for {district} > {block} > {panchayat}")

            except Exception as e:
                print(f"❌ Failed to extract table: {e}")

# Close WebDriver
driver.quit()
print("✅ Extraction complete! Data saved to 'gram_panchayat_mukhiya_results(11).csv'")
