from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time

# Set up ChromeDriver path
chrome_driver_path = r"C:\Users\sanju\OneDrive\Desktop\web scraping\chromedriver.exe"
service = Service(chrome_driver_path)

# Start WebDriver
driver = webdriver.Chrome(service=service)
driver.get("http://sec2021.bihar.gov.in/sec_np_p1_01/Admin/WinningCandidatespost_wise.aspx")  # Change URL if needed

time.sleep(3)  # Allow time for the page to load

try:
    # Locate the dropdown
    nagar_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddl_Post"))  # Change ID if needed

    # Print available options
    print("Available dropdown options:")
    for option in nagar_dropdown.options:
        print(option.text, "=>", option.get_attribute("value"))

    # Select by value
    try:
        nagar_dropdown.select_by_value("-1")  # Change value if needed
        print("Selected using select_by_value('-1')")
    except:
        print("Option '-1' not found, trying alternative methods...")

        # Select by index (Try different indexes if needed)
        nagar_dropdown.select_by_index(0)  
        print("Selected using select_by_index(0)")

        # Select by visible text (Change text if needed)
        # nagar_dropdown.select_by_visible_text("Your Option Text Here")
        # print("Selected using select_by_visible_text('Your Option Text Here')")

    time.sleep(2)  # Allow selection to take effect

except Exception as e:
    print("Error:", e)

# Keep browser open for inspection
input("Press Enter to close the browser...")  
driver.quit()
