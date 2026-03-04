from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def click_custom_dropdown(driver, dropdown_id, option_text):
    try:
        print(f"Clicking dropdown {dropdown_id}")
        dropdown = driver.find_element(By.ID, dropdown_id)
        driver.execute_script("arguments[0].click();", dropdown)
        time.sleep(2)
        
        print(f"Looking for option: {option_text}")
        option_xpath = f"//div[contains(text(), '{option_text}')]"
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        driver.execute_script("arguments[0].click();", option)
        time.sleep(1)
        print(f"Successfully selected {option_text}")
        return True
    except Exception as e:
        print(f"Failed to select {option_text}: {e}")
        return False

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

try:
    print("Loading page...")
    driver.get("https://agmarknet.gov.in/datewisespeccommdodityinput")
    time.sleep(8)
    
    print("Trying to select year...")
    if click_custom_dropdown(driver, "year", "2025"):
        print("Year selected successfully")
    else:
        print("Year selection failed")
        
finally:
    driver.quit()
