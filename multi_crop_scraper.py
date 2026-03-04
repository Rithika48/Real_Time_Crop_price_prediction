from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import datetime, timedelta
import re

def click_custom_dropdown(driver, dropdown_id, option_text):
    """Click custom React dropdown and select option"""
    try:
        # Click the dropdown to open it
        dropdown = driver.find_element(By.ID, dropdown_id)
        driver.execute_script("arguments[0].click();", dropdown)
        time.sleep(2)
        
        # Wait for dropdown options to appear and click the desired option
        option_xpath = f"//div[contains(text(), '{option_text}') or contains(@value, '{option_text}')]"
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        driver.execute_script("arguments[0].click();", option)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"    Failed to select {option_text} from {dropdown_id}: {e}")
        return False

def get_district_from_market(market_name):
    """Map market names to correct district names for Karnataka"""
    
    # Karnataka market to district mapping
    market_district_map = {
        # Bangalore District
        'Bangalore': 'Bangalore', 'Bengaluru': 'Bangalore', 'Nelamangala': 'Bangalore',
        'Doddaballapur': 'Bangalore', 'Hoskote': 'Bangalore', 'Devanahalli': 'Bangalore',
        
        # Mysore District  
        'Mysore': 'Mysore', 'Mysuru': 'Mysore', 'Nanjangud': 'Mysore', 'T.Narasipur': 'Mysore',
        'Hunsur': 'Mysore', 'Piriyapatna': 'Mysore', 'K.R.Nagar': 'Mysore',
        
        # Mandya District
        'Mandya': 'Mandya', 'Maddur': 'Mandya', 'Malavalli': 'Mandya', 'Pandavapura': 'Mandya',
        'Srirangapatna': 'Mandya', 'Nagamangala': 'Mandya',
        
        # Hassan District
        'Hassan': 'Hassan', 'Arkalgud': 'Hassan', 'Holenarasipur': 'Hassan', 'Channarayapatna': 'Hassan',
        'Belur': 'Hassan', 'Sakleshpur': 'Hassan', 'Alur': 'Hassan', 'Arasikere': 'Hassan',
        
        # Tumkur District
        'Tumkur': 'Tumkur', 'Tumakuru': 'Tumkur', 'Kunigal': 'Tumkur', 'Tiptur': 'Tumkur',
        'Turuvekere': 'Tumkur', 'Gubbi': 'Tumkur', 'Madhugiri': 'Tumkur', 'Koratagere': 'Tumkur',
        
        # Kolar District
        'Kolar': 'Kolar', 'Bangarpet': 'Kolar', 'Malur': 'Kolar', 'Srinivaspur': 'Kolar',
        'Mulbagal': 'Kolar', 'Chintamani': 'Chikkaballapur', 'Chikkaballapur': 'Chikkaballapur',
        
        # Chikkamagaluru District
        'Chikkamagaluru': 'Chikkamagaluru', 'Chikmagalur': 'Chikkamagaluru', 'Kadur': 'Chikkamagaluru',
        'Tarikere': 'Chikkamagaluru', 'Koppa': 'Chikkamagaluru', 'Mudigere': 'Chikkamagaluru',
        'Sringeri': 'Chikkamagaluru', 'Narasimharajapura': 'Chikkamagaluru',
        
        # Davangere District
        'Davangere': 'Davangere', 'Harihar': 'Davangere', 'Jagalur': 'Davangere',
        'Channagiri': 'Davangere', 'Davanagere': 'Davangere',
        
        # Chitradurga District
        'Chitradurga': 'Chitradurga', 'Hiriyur': 'Chitradurga', 'Holalkere': 'Chitradurga',
        'Hosadurga': 'Chitradurga', 'Molakalmuru': 'Chitradurga', 'Challakere': 'Chitradurga',
        
        # Shimoga District
        'Shimoga': 'Shimoga', 'Shivamogga': 'Shimoga', 'Bhadravati': 'Shimoga',
        'Sagara': 'Shimoga', 'Soraba': 'Shimoga', 'Shikaripura': 'Shimoga',
        'Thirthahalli': 'Shimoga', 'Hosanagar': 'Shimoga',
        
        # Dharwad District
        'Dharwad': 'Dharwad', 'Hubli': 'Dharwad', 'Huballi': 'Dharwad', 'Kalghatgi': 'Dharwad',
        'Kundgol': 'Dharwad', 'Navalgund': 'Dharwad',
        
        # Gadag District
        'Gadag': 'Gadag', 'Bettageri': 'Gadag', 'Shirhatti': 'Gadag', 'Mundargi': 'Gadag',
        'Nargund': 'Gadag', 'Ron': 'Gadag',
        
        # Haveri District
        'Haveri': 'Haveri', 'Ranebennuru': 'Haveri', 'Hirekerur': 'Haveri', 'Savanur': 'Haveri',
        'Shiggaon': 'Haveri', 'Hangal': 'Haveri', 'Byadgi': 'Haveri',
        
        # Uttara Kannada District
        'Karwar': 'Uttara Kannada', 'Sirsi': 'Uttara Kannada', 'Kumta': 'Uttara Kannada',
        'Honavar': 'Uttara Kannada', 'Bhatkal': 'Uttara Kannada', 'Mundgod': 'Uttara Kannada',
        'Haliyal': 'Uttara Kannada', 'Ankola': 'Uttara Kannada', 'Joida': 'Uttara Kannada',
        'Yellapur': 'Uttara Kannada', 'Siddapur': 'Uttara Kannada',
        
        # Belgaum District
        'Belgaum': 'Belgaum', 'Belagavi': 'Belgaum', 'Athani': 'Belgaum', 'Ramdurg': 'Belgaum',
        'Khanapur': 'Belgaum', 'Soundatti': 'Belgaum', 'Saundatti': 'Belgaum', 'Parasgad': 'Belgaum',
        'Bailhongal': 'Belgaum', 'Mudalgi': 'Belgaum', 'Gokak': 'Belgaum', 'Hukkeri': 'Belgaum',
        'Chikkodi': 'Belgaum', 'Nippani': 'Belgaum',
        
        # Bagalkot District
        'Bagalkot': 'Bagalkot', 'Badami': 'Bagalkot', 'Bilagi': 'Bagalkot', 'Hungund': 'Bagalkot',
        'Jamkhandi': 'Bagalkot', 'Mudhol': 'Bagalkot',
        
        # Bijapur District
        'Bijapur': 'Bijapur', 'Vijayapura': 'Bijapur', 'Indi': 'Bijapur', 'Sindgi': 'Bijapur',
        'Basavana Bagewadi': 'Bijapur', 'Muddebihal': 'Bijapur', 'Talikota': 'Bijapur',
        
        # Gulbarga District
        'Gulbarga': 'Gulbarga', 'Kalaburagi': 'Gulbarga', 'Kalburgi': 'Gulbarga',
        'Afzalpur': 'Gulbarga', 'Aland': 'Gulbarga', 'Chincholi': 'Gulbarga',
        'Jewargi': 'Gulbarga', 'Sedam': 'Gulbarga',
        
        # Bidar District
        'Bidar': 'Bidar', 'Aurad': 'Bidar', 'Bhalki': 'Bidar', 'Homnabad': 'Bidar',
        'Basavakalyan': 'Bidar',
        
        # Raichur District
        'Raichur': 'Raichur', 'Devadurga': 'Raichur', 'Lingsugur': 'Raichur',
        'Manvi': 'Raichur', 'Sindhanur': 'Raichur',
        
        # Koppal District
        'Koppal': 'Koppal', 'Gangavathi': 'Koppal', 'Kushtagi': 'Koppal', 'Yelburga': 'Koppal',
        
        # Bellary District
        'Bellary': 'Bellary', 'Ballari': 'Bellary', 'Hospet': 'Bellary', 'Hosapete': 'Bellary',
        'Kudligi': 'Bellary', 'Hagaribommanahalli': 'Bellary', 'Siruguppa': 'Bellary',
        'Sandur': 'Bellary', 'Hadagalli': 'Bellary',
        
        # Dakshina Kannada District
        'Mangalore': 'Dakshina Kannada', 'Mangaluru': 'Dakshina Kannada', 'Puttur': 'Dakshina Kannada',
        'Sullia': 'Dakshina Kannada', 'Bantwal': 'Dakshina Kannada', 'Belthangady': 'Dakshina Kannada',
        
        # Udupi District
        'Udupi': 'Udupi', 'Kundapura': 'Udupi', 'Karkala': 'Udupi', 'Brahmavar': 'Udupi',
        
        # Kodagu District
        'Madikeri': 'Kodagu', 'Somwarpet': 'Kodagu', 'Virajpet': 'Kodagu',
        
        # Chamarajanagar District
        'Chamarajanagar': 'Chamarajanagar', 'Chamaraj Nagar': 'Chamarajanagar', 
        'Gundlupet': 'Chamarajanagar', 'Kollegal': 'Chamarajanagar', 'Yelandur': 'Chamarajanagar'
    }
    
    # Clean market name and try to find match
    market_clean = market_name.replace(' APMC', '').replace(' Market', '').strip()
    
    # Direct lookup
    if market_clean in market_district_map:
        return market_district_map[market_clean]
    
    # Try partial matching
    for market_key, district in market_district_map.items():
        if market_key.lower() in market_clean.lower() or market_clean.lower() in market_key.lower():
            return district
    
    # Fallback to first word if no match found
    return market_clean.split()[0] if market_clean else "Unknown"
    """Click custom React dropdown and select option"""
    try:
        # Click the dropdown to open it
        dropdown = driver.find_element(By.ID, dropdown_id)
        driver.execute_script("arguments[0].click();", dropdown)
        time.sleep(2)
        
        # Wait for dropdown options to appear and click the desired option
        option_xpath = f"//div[contains(text(), '{option_text}') or contains(@value, '{option_text}')]"
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        driver.execute_script("arguments[0].click();", option)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"    Failed to select {option_text} from {dropdown_id}: {e}")
        return False

def scrape_commodity_data(driver, wait, commodity, year, month):
    """Scrape data for a specific commodity, year, and month"""
    try:
        print(f"  Scraping {commodity} for {month}/{year}...")
        
        # Go to input page
        driver.get("https://agmarknet.gov.in/datewisespeccommdodityinput")
        time.sleep(8)  # Wait for React app to load
        
        # Select Year
        if not click_custom_dropdown(driver, "year", str(year)):
            return []
        
        # Select Month
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August", 
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        month_name = month_names.get(month, str(month))
        if not click_custom_dropdown(driver, "month", month_name):
            return []
        
        # Select State (Karnataka)
        if not click_custom_dropdown(driver, "state", "Karnataka"):
            return []
        
        # Select Commodity
        if not click_custom_dropdown(driver, "commodity", commodity):
            return []
        
        # Submit form - look for submit button
        try:
            submit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit')] | //input[@type='submit'] | //button[@type='submit']")
            if submit_buttons:
                driver.execute_script("arguments[0].click();", submit_buttons[0])
                time.sleep(8)  # Wait for results
            else:
                print("    Submit button not found")
                return []
        except Exception as e:
            print(f"    Error clicking submit: {e}")
            return []
        
        # Check if we're on results page
        if "datewisespeccommodityoutput" not in driver.current_url:
            print(f"    Failed to reach results page for {commodity}")
            return []
        
        print(f"    Successfully reached results page for {commodity}")
        
        # Extract data from results page
        data = []
        
        # Find all tables
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"    Found {len(tables)} tables")
        
        if not tables:
            # Try to find data in other formats
            page_text = driver.page_source
            print("    No tables found, checking page content...")
            
            # Look for market names and price data in text
            market_matches = re.findall(r'Market Name : ([^<\n\r]+)', page_text)
            print(f"    Found {len(market_matches)} market names")
            
            # Look for price patterns
            price_patterns = re.findall(r'(\d{2}/\d{2}/\d{4})\s+[\d.]+\s+\w+\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)', page_text)
            print(f"    Found {len(price_patterns)} price entries")
            
            return []
        
        for table_idx, table in enumerate(tables):
            try:
                # Get market name from surrounding text
                market_name = "Unknown Market"
                try:
                    # Look for market name in page source around this table
                    page_source = driver.page_source
                    market_matches = re.findall(r'Market Name : ([^<\n\r]+)', page_source)
                    if market_matches and table_idx < len(market_matches):
                        market_name = market_matches[table_idx].strip()
                    elif market_matches:
                        market_name = market_matches[0].strip()
                except:
                    pass
                
                # Process table rows
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"    Table {table_idx + 1}: {len(rows)} rows, Market: {market_name}")
                
                for row_idx, row in enumerate(rows):
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 6:
                            # Extract data from cells
                            date_str = cells[0].text.strip()
                            arrivals = cells[1].text.strip()
                            variety = cells[2].text.strip()
                            min_price = cells[3].text.strip().replace(',', '')
                            max_price = cells[4].text.strip().replace(',', '')
                            modal_price = cells[5].text.strip().replace(',', '')
                            
                            # Skip header rows
                            if 'arrival' in date_str.lower() or 'date' in date_str.lower():
                                continue
                            
                            # Convert date format
                            formatted_date = date_str
                            if '/' in date_str:
                                try:
                                    date_parts = date_str.split('/')
                                    if len(date_parts) == 3:
                                        formatted_date = f"{date_parts[0]}-{date_parts[1]}-{date_parts[2]}"
                                except:
                                    pass
                            
                            # Extract district from market name using proper mapping
                            district = get_district_from_market(market_name)
                            
                            record = {
                                'District Name': district,
                                'Market Name': market_name,
                                'Commodity': commodity,
                                'Variety': variety if variety else 'Local',
                                'Grade': 'FAQ',
                                'Min Price (Rs./Quintal)': min_price,
                                'Max Price (Rs./Quintal)': max_price,
                                'Modal Price (Rs./Quintal)': modal_price,
                                'Price Date': formatted_date
                            }
                            
                            # Validate data
                            try:
                                float(modal_price.replace(',', ''))
                                if float(modal_price.replace(',', '')) > 0:
                                    data.append(record)
                                    print(f"      Added record: {date_str} - {modal_price}")
                            except ValueError:
                                print(f"      Skipped invalid price: {modal_price}")
                                
                    except Exception as e:
                        print(f"    Error processing row {row_idx}: {e}")
                        continue
                        
            except Exception as e:
                print(f"    Error processing table {table_idx}: {e}")
                continue
        
        print(f"    {commodity}: {len(data)} records extracted")
        return data
        
    except Exception as e:
        print(f"    Error scraping {commodity}: {e}")
        return []

def main():
    print("Starting real data scraping from new Agmarknet website...")
    
    # Define commodities based on existing CSV data
    commodities = [
        "Bajra", "Cabbage", "Coconut", "Groundnut", "Maize", 
        "Onion", "Potato", "Ragi", "Rice", "Sunflower", 
        "Tomato", "Wheat"
    ]
    
    # Get current date for scraping last 10 days
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    # Calculate 10 days ago
    ten_days_ago = current_date - timedelta(days=10)
    prev_year = ten_days_ago.year
    prev_month = ten_days_ago.month
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    wait = WebDriverWait(driver, 20)
    all_data = []
    
    try:
        print(f"Scraping data for last 10 days: {ten_days_ago.strftime('%d-%m-%Y')} to {current_date.strftime('%d-%m-%Y')}")
        
        # Scrape current month (for recent days)
        for commodity in commodities:
            try:
                data = scrape_commodity_data(driver, wait, commodity, current_year, current_month)
                all_data.extend(data)
                time.sleep(5)  # Rate limiting
            except Exception as e:
                print(f"Failed to scrape {commodity} for current month: {e}")
        
        # If 10 days ago was in previous month, scrape that too
        if prev_month != current_month:
            for commodity in commodities:
                try:
                    data = scrape_commodity_data(driver, wait, commodity, prev_year, prev_month)
                    all_data.extend(data)
                    time.sleep(5)  # Rate limiting
                except Exception as e:
                    print(f"Failed to scrape {commodity} for previous month: {e}")
        
        # Keep all scraped data (remove 10-day filter for testing)
        if all_data:
            print(f"Total scraped records: {len(all_data)}")
            # Show sample dates
            for i, record in enumerate(all_data[:5]):
                print(f"Sample {i+1}: {record['Price Date']} - {record['Commodity']} - {record['Modal Price (Rs./Quintal)']}")
            
            print(f"Keeping all {len(all_data)} records")
        
        if all_data:
            # Create DataFrame with new data
            new_df = pd.DataFrame(all_data)
            print(f"New DataFrame created with {len(new_df)} records")
            
            # Read existing data if file exists
            try:
                existing_df = pd.read_csv('final_complete_data.csv')
                print(f"Existing CSV has {len(existing_df)} records")
                
                # Remove duplicates based on key columns
                key_cols = ['District Name', 'Market Name', 'Commodity', 'Price Date']
                
                print("Before duplicate removal:")
                print(f"  Existing: {len(existing_df)} records")
                print(f"  New: {len(new_df)} records")
                
                if not existing_df.empty:
                    existing_df = existing_df.drop_duplicates(subset=key_cols, keep='last')
                new_df = new_df.drop_duplicates(subset=key_cols, keep='last')
                
                print("After duplicate removal:")
                print(f"  Existing: {len(existing_df)} records")
                print(f"  New: {len(new_df)} records")
                
                # Append new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                print(f"Combined DataFrame: {len(combined_df)} records")
                
                combined_df = combined_df.drop_duplicates(subset=key_cols, keep='last')
                print(f"Final DataFrame after removing duplicates: {len(combined_df)} records")
                
            except FileNotFoundError:
                combined_df = new_df
                print("No existing CSV found, using new data only")
            
            # Save combined data
            combined_df.to_csv('final_complete_data.csv', index=False)
            print(f"Saved {len(combined_df)} records to CSV")
            
            print(f"\nTotal new records scraped: {len(all_data)}")
            print("Data appended to final_complete_data.csv")
            
            # Show summary
            crop_counts = {}
            for record in all_data:
                crop = record['Commodity']
                crop_counts[crop] = crop_counts.get(crop, 0) + 1
            
            print("\nSummary by crop:")
            for crop, count in crop_counts.items():
                print(f"  {crop}: {count} records")
                
            # Show sample data
            if len(all_data) > 0:
                print(f"\nSample record:")
                sample = all_data[0]
                for key, value in sample.items():
                    print(f"  {key}: {value}")
        else:
            print("No data could be scraped from the website")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
