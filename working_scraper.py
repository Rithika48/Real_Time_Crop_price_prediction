from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

def scrape_agmarknet():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        driver.get("https://www.agmarknet.gov.in/SearchCmmMkt.aspx")
        wait = WebDriverWait(driver, 10)
        
        # Select commodity (Apple)
        commodity_select = Select(driver.find_element(By.ID, "ddlCommodity"))
        commodity_select.select_by_visible_text("Apple")
        time.sleep(2)
        
        # Select state (Karnataka)
        state_select = Select(driver.find_element(By.ID, "ddlState"))
        state_select.select_by_visible_text("Karnataka")
        time.sleep(3)
        
        # Select district (Bangalore)
        district_select = Select(driver.find_element(By.ID, "ddlDistrict"))
        district_select.select_by_visible_text("Bangalore")
        time.sleep(2)
        
        # Click Go button
        go_button = driver.find_element(By.ID, "btnGo")
        go_button.click()
        
        # Wait for results
        wait.until(EC.presence_of_element_located((By.ID, "cphBody_GridPriceData")))
        
        # Extract data
        table = driver.find_element(By.ID, "cphBody_GridPriceData")
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header
        
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 10:
                record = {
                    'sl_no': cells[0].text.strip(),
                    'district': cells[1].text.strip(),
                    'market': cells[2].text.strip(),
                    'commodity': cells[3].text.strip(),
                    'variety': cells[4].text.strip(),
                    'grade': cells[5].text.strip(),
                    'min_price': cells[6].text.strip(),
                    'max_price': cells[7].text.strip(),
                    'modal_price': cells[8].text.strip(),
                    'price_date': cells[9].text.strip()
                }
                data.append(record)
        
        # Save to CSV
        with open('apple_prices.csv', 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        print(f"Scraped {len(data)} records for Apple in Bangalore")
        for record in data[:5]:  # Show first 5
            print(f"  {record['market']}: ₹{record['modal_price']}/quintal on {record['price_date']}")
        
    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("error.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_agmarknet()
