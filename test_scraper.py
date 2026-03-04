from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import datetime, timedelta

def click_custom_dropdown(driver, dropdown_id, option_text):
    """Click custom React dropdown and select option"""
    try:
        dropdown = driver.find_element(By.ID, dropdown_id)
        driver.execute_script("arguments[0].click();", dropdown)
        time.sleep(2)
        
        option_xpath = f"//div[contains(text(), '{option_text}') or contains(@value, '{option_text}')]"
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        driver.execute_script("arguments[0].click();", option)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Failed to select {option_text}: {e}")
        return False

def main():
    print("Testing scraper with Tomato only...")
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        driver.get("https://agmarknet.gov.in/datewisespeccommdodityinput")
        time.sleep(8)
        
        # Select 2025
        if not click_custom_dropdown(driver, "year", "2025"):
            return
        
        # Select November
        if not click_custom_dropdown(driver, "month", "November"):
            return
        
        # Select Karnataka
        if not click_custom_dropdown(driver, "state", "Karnataka"):
            return
        
        # Select Tomato
        if not click_custom_dropdown(driver, "commodity", "Tomato"):
            return
        
        # Submit
        submit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit')]")
        if submit_buttons:
            driver.execute_script("arguments[0].click();", submit_buttons[0])
            time.sleep(8)
        
        print(f"Current URL: {driver.current_url}")
        
        if "datewisespeccommodityoutput" in driver.current_url:
            print("Successfully reached results page!")
            
            # Check for data
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"Found {len(tables)} tables")
            
            if tables:
                rows = tables[0].find_elements(By.TAG_NAME, "tr")
                print(f"First table has {len(rows)} rows")
                
                # Show first few rows
                for i, row in enumerate(rows[:5]):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        print(f"Row {i}: {[cell.text.strip() for cell in cells[:6]]}")
        else:
            print("Failed to reach results page")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
