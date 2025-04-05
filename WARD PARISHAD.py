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
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://sec.bihar.gov.in/ForPublic/ResultP1.aspx")
wait = WebDriverWait(driver, 10)

# Function to select dropdown by visible text
def select_dropdown_by_text(css_selector, text):
    dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    select = Select(dropdown)
    select.select_by_visible_text(text)
    time.sleep(1)  # Allow dropdown to update

# Extract options from a dropdown
def get_dropdown_options(css_selector):
    dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    return [opt.text.strip() for opt in Select(dropdown).options if opt.text.strip() not in ["Select", "--Select--", "--select--"]]

# Handle unexpected pop-ups
def close_popups():
    try:
        popups = driver.find_elements(By.CSS_SELECTOR, "div[style*='display: block']")
        for popup in popups:
            driver.execute_script("arguments[0].style.display = 'none';", popup)
        print("✅ Closed unexpected pop-ups")
    except:
        pass

# Click the filter button
def click_filter_button():
    retries = 3
    for attempt in range(retries):
        try:
            close_popups()  # Ensure no overlay is blocking
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_btnFilter")))
            button.click()
            time.sleep(2)  # Wait for data to load
            return
        except:
            print(f"⚠️ Retry {attempt+1}: Filter button not clickable. Retrying...")
            time.sleep(2)
    print("❌ Failed to click filter button after retries")

# Get table data
def get_table_data():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.select_one("#ctl00_ContentPlaceHolder1_RPDetails")
    if not table:
        return None, None
    headers = [th.text.strip() for th in table.select("th")]
    rows = [[td.text.strip() for td in tr.select("td")] for tr in table.select("tr")[1:]]
    return headers, rows

# Initialize DataFrame for saving
csv_file = "ward_parshad_data.csv"
all_data = []
if os.path.exists(csv_file):
    existing_data = pd.read_csv(csv_file)
else:
    existing_data = pd.DataFrame()

# Target post
try:
    select_dropdown_by_text("#ctl00_ContentPlaceHolder1_ddl_Post", "वार्ड पार्षद")
except:
    print("❌ Could not select post 'वार्ड पार्षद'")
    driver.quit()
    exit()

# Iterate through all dropdown combinations
districts = get_dropdown_options("#ctl00_ContentPlaceHolder1_ddlDistrict")
for district in districts:
    print(f"➡️ Processing District: {district}")
    try:
        select_dropdown_by_text("#ctl00_ContentPlaceHolder1_ddlDistrict", district)
        time.sleep(1)
        types = get_dropdown_options("#ctl00_ContentPlaceHolder1_ddlNPType")

        for np_type in types:
            print(f"   🏢 Nagar Type: {np_type}")
            select_dropdown_by_text("#ctl00_ContentPlaceHolder1_ddlNPType", np_type)
            time.sleep(1)
            bodies = get_dropdown_options("#ctl00_ContentPlaceHolder1_ddlPanchayat")

            for body in bodies:
                print(f"      🏙️ Nagar Name: {body}")
                select_dropdown_by_text("#ctl00_ContentPlaceHolder1_ddlPanchayat", body)
                time.sleep(1)
                wards = get_dropdown_options("#ctl00_ContentPlaceHolder1_ddlWard")

                for ward in wards:
                    print(f"         🔢 Ward Number: {ward}")
                    select_dropdown_by_text("#ctl00_ContentPlaceHolder1_ddlWard", ward)
                    click_filter_button()

                    headers, rows = get_table_data()
                    if headers and rows:
                        for row in rows:
                            all_data.append([district, np_type, body, ward] + row)

                        # Save progress to CSV
                        df = pd.DataFrame(all_data, columns=["District", "Nagar Type", "Nagar Name", "Ward Number"] + headers)
                        df = pd.concat([existing_data, df]).drop_duplicates().reset_index(drop=True)
                        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
                        print(f"✅ Data saved to {csv_file}")

    except Exception as e:
        print(f"⚠️ Error processing {district}: {e}")
        continue

# Final save
if all_data:
    df = pd.DataFrame(all_data, columns=["District", "Nagar Type", "Nagar Name", "Ward Number"] + headers)
    df = pd.concat([existing_data, df]).drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"✅ Final data saved to {csv_file}")
else:
    print("❌ No data found.")

driver.quit()
