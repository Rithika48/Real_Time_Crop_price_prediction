from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
from datetime import datetime, timedelta

def scrape_crop_district(driver, wait, crop, district):
    """Scrape data for specific crop and district"""
    try:
        driver.get("https://www.agmarknet.gov.in/SearchCmmMkt.aspx")
        time.sleep(2)
        
        # Set date range for last 20 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=20)
        
        # Fill from date
        from_date_field = driver.find_element(By.ID, "txtDate")
        from_date_field.clear()
        from_date_field.send_keys(start_date.strftime("%d-%b-%Y"))
        
        # Fill to date
        to_date_field = driver.find_element(By.ID, "txtDateTo")
        to_date_field.clear()
        to_date_field.send_keys(end_date.strftime("%d-%b-%Y"))
        
        # Select commodity
        commodity_select = Select(driver.find_element(By.ID, "ddlCommodity"))
        commodity_select.select_by_visible_text(crop)
        time.sleep(1)
        
        # Select state
        state_select = Select(driver.find_element(By.ID, "ddlState"))
        state_select.select_by_visible_text("Karnataka")
        time.sleep(2)
        
        # Select district
        district_select = Select(driver.find_element(By.ID, "ddlDistrict"))
        district_select.select_by_visible_text(district)
        time.sleep(1)
        
        # Click Go
        driver.find_element(By.ID, "btnGo").click()
        wait.until(EC.presence_of_element_located((By.ID, "cphBody_GridPriceData")))
        
        # Extract data
        table = driver.find_element(By.ID, "cphBody_GridPriceData")
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]
        
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 10:
                # Format date to DD-MM-YYYY
                raw_date = cells[9].text.strip()
                try:
                    formatted_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%d-%m-%Y")
                except:
                    formatted_date = raw_date
                
                data.append([
                    district,
                    cells[2].text.strip(),  # Market Name
                    crop,
                    cells[4].text.strip(),  # Variety
                    cells[5].text.strip(),  # Grade
                    cells[6].text.strip(),  # Min Price
                    cells[7].text.strip(),  # Max Price
                    cells[8].text.strip(),  # Modal Price
                    formatted_date          # Date
                ])
        
        return data
        
    except Exception as e:
        print(f"    Error: {e}")
        return []

def main():
    crops = ["Tomato", "Potato", "Maize", "Coconut", "Ragi", "Wheat", "Rice", "Groundnut"]
    districts = [
        "Bagalkot", "Bangalore","Belgaum", "Bellary", "Bidar", 
        "Bijapur", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga", 
        "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Gulbarga", "Hassan", 
        "Haveri", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysore", "Raichur", 
        "Shimoga", "Tumkur", "Udupi", "Uttara Kannada", "Yadgir"
    ]
    
    # Create CSV with headers if it doesn't exist
    try:
        with open('final_complete_data.csv', 'x', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["District Name", "Market Name", "Commodity", "Variety", "Grade", 
                           "Min Price (Rs./Quintal)", "Max Price (Rs./Quintal)", 
                           "Modal Price (Rs./Quintal)", "Price Date"])
    except FileExistsError:
        pass
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    wait = WebDriverWait(driver, 10)
    
    try:
        total_combinations = len(crops) * len(districts)
        current = 0
        
        for crop in crops:
            print(f"Scraping {crop}...")
            for district in districts:
                current += 1
                print(f"  {district} ({current}/{total_combinations})")
                
                data = scrape_crop_district(driver, wait, crop, district)
                
                if data:
                    print(f"    Found {len(data)} records")
                    with open('final_complete_data.csv', 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(data)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
