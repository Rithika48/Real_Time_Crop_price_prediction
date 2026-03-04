from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

def scrape_all_data():
    crops = ["Tomato", "Potato", "Maize", "Coconut", "Rice", "Groundnut"]
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    wait = WebDriverWait(driver, 8)
    all_data = []
    
    try:
        for i, crop in enumerate(crops, 1):
            print(f"{i}/{len(crops)} Scraping {crop}...")
            
            try:
                driver.get("https://www.agmarknet.gov.in/SearchCmmMkt.aspx")
                
                # Select commodity
                Select(driver.find_element(By.ID, "ddlCommodity")).select_by_visible_text(crop)
                
                # Select Karnataka (all districts)
                Select(driver.find_element(By.ID, "ddlState")).select_by_visible_text("Karnataka")
                
                # Click Go
                driver.find_element(By.ID, "btnGo").click()
                wait.until(EC.presence_of_element_located((By.ID, "cphBody_GridPriceData")))
                
                # Extract data
                rows = driver.find_element(By.ID, "cphBody_GridPriceData").find_elements(By.TAG_NAME, "tr")[1:]
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 10:
                        all_data.append({
                            'crop': crop,
                            'district': cells[1].text.strip(),
                            'market': cells[2].text.strip(),
                            'variety': cells[4].text.strip(),
                            'min_price': cells[6].text.strip(),
                            'max_price': cells[7].text.strip(),
                            'modal_price': cells[8].text.strip(),
                            'date': cells[9].text.strip()
                        })
                
                print(f"  Found {len([d for d in all_data if d['crop'] == crop])} records")
                
            except Exception as e:
                print(f"  Error with {crop}: {e}")
        
        # Save results
        if all_data:
            with open('karnataka_all_crops.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
                writer.writeheader()
                writer.writerows(all_data)
            
            print(f"\nSaved {len(all_data)} total records")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_all_data()
