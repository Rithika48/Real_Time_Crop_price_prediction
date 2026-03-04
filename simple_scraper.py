from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import json
import time

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

def scrape_single_crop():
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)
    
    try:
        print("🌐 Loading AgMarkNet...")
        driver.get("https://www.agmarknet.gov.in/SearchCmmMkt.aspx")
        
        # Wait and select commodity (Tomato = 17)
        commodity_dropdown = Select(wait.until(EC.element_to_be_clickable((By.ID, "ddlCommodity"))))
        commodity_dropdown.select_by_value("17")
        time.sleep(1)
        
        state_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ddlState"))
        )

        Select(state_dropdown).select_by_visible_text("Karnataka")
        
        district_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ddlDistrict"))
  )
        
        # Set dates
        from_date = driver.find_element(By.ID, "txtDate")
        from_date.clear()
        from_date.send_keys("01-Jan-2023")
        
        to_date = driver.find_element(By.ID, "txtDateTo")
        to_date.clear()
        to_date.send_keys("22-Sep-2025")
        
        # Click search
        search_btn = driver.find_element(By.ID, "btnGo")
        search_btn.click()
        
        print("⏳ Waiting for results...")
        time.sleep(10)  # Simple wait
        
        # Try to get results
        try:
            table = driver.find_element(By.ID, "cphBody_Grid")
            soup = BeautifulSoup(table.get_attribute("outerHTML"), "html.parser")
            
            rows = []
            for tr in soup.find_all("tr")[1:]:  # Skip header
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cells:
                    rows.append(cells)
            
            print(f"✅ Found {len(rows)} records")
            
            # Save results
            with open("tomato_results.json", "w") as f:
                json.dump(rows, f, indent=2)
            
            return rows
            
        except Exception as e:
            print(f"❌ No results found: {e}")
            return []
            
    finally:
        driver.quit()

if __name__ == "__main__":
    results = scrape_single_crop()
    print(f"Scraping completed. Found {len(results)} records.")
