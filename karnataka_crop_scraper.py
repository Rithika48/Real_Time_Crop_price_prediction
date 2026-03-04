from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

OUTPUT_FILE = Path(__file__).resolve().parent / "scraped_data.json"

class AgMarkNetCalendarHandler:
    """Specialized handler for AgMarkNet calendar interactions"""
    
    def __init__(self, driver, debug=True):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.debug = debug
    
    def handle_calendar_date(self, input_id, target_date, description="date"):
        """Enhanced calendar date selection with multiple strategies"""
        if self.debug:
            print(f"📅 Setting {description} to: {target_date}")
        
        # Convert string date to datetime object for manipulation
        try:
            if isinstance(target_date, str):
                # Try different date formats
                date_formats = ["%d-%b-%Y", "%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"]
                target_dt = None
                
                for fmt in date_formats:
                    try:
                        target_dt = datetime.strptime(target_date, fmt)
                        break
                    except ValueError:
                        continue
                
                if target_dt is None:
                    raise ValueError(f"Could not parse date format: {target_date}")
            else:
                target_dt = target_date
                
        except Exception as e:
            if self.debug:
                print(f"❌ Date parsing error: {e}")
            return False
        
        # Format for AgMarkNet (DD-MMM-YYYY)
        formatted_date = target_dt.strftime("%d-%b-%Y")
        
        # Multiple strategies for date input
        strategies = [
            self._strategy_direct_input,
            self._strategy_javascript_set,
            self._strategy_calendar_navigation,
            self._strategy_clear_and_type,
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                if self.debug:
                    print(f"   Trying strategy {i}: {strategy.__name__}")
                
                if strategy(input_id, formatted_date, target_dt):
                    if self.debug:
                        print(f"   ✅ Strategy {i} succeeded!")
                    return True
                    
            except Exception as e:
                if self.debug:
                    print(f"   ❌ Strategy {i} failed: {e}")
                continue
        
        if self.debug:
            print(f"   ❌ All strategies failed for {description}")
        return False
    
    def _strategy_direct_input(self, input_id, formatted_date, target_dt):
        """Strategy 1: Direct input with proper events"""
        element = self.wait.until(EC.element_to_be_clickable((By.ID, input_id)))
        
        # Focus the element
        element.click()
        time.sleep(0.5)
        
        # Clear existing value
        element.clear()
        time.sleep(0.3)
        
        # Type the date
        element.send_keys(formatted_date)
        time.sleep(0.5)
        
        # Trigger events
        self.driver.execute_script("""
            var element = arguments[0];
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));
            element.blur();
        """, element)
        
        time.sleep(1)
        
        # Verify the value was set
        actual_value = element.get_attribute("value")
        return len(actual_value) > 5 and any(part in actual_value for part in formatted_date.split("-"))
    
    def _strategy_javascript_set(self, input_id, formatted_date, target_dt):
        """Strategy 2: Pure JavaScript value setting"""
        element = self.wait.until(EC.presence_of_element_located((By.ID, input_id)))
        
        # Set value via JavaScript
        self.driver.execute_script("""
            var element = document.getElementById(arguments[0]);
            if (element) {
                element.value = arguments[1];
                element.dispatchEvent(new Event('input', {bubbles: true}));
                element.dispatchEvent(new Event('change', {bubbles: true}));
                element.focus();
                element.blur();
            }
        """, input_id, formatted_date)
        
        time.sleep(1)
        
        actual_value = element.get_attribute("value")
        return len(actual_value) > 5
    
    def _strategy_calendar_navigation(self, input_id, formatted_date, target_dt):
        """Strategy 3: Navigate through calendar widget"""
        element = self.wait.until(EC.element_to_be_clickable((By.ID, input_id)))
        
        # Click to open calendar
        element.click()
        time.sleep(1)
        
        # Look for calendar popup
        calendar_selectors = [
            ".ui-datepicker",
            "#ui-datepicker-div", 
            ".calendar",
            ".datepicker"
        ]
        
        calendar_popup = None
        for selector in calendar_selectors:
            try:
                calendar_popup = self.driver.find_element(By.CSS_SELECTOR, selector)
                if calendar_popup.is_displayed():
                    break
            except:
                continue
        
        if calendar_popup:
            if self.debug:
                print("   📅 Calendar popup found, navigating...")
            
            return self._navigate_calendar(calendar_popup, target_dt)
        else:
            # If no popup, fall back to direct input
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(formatted_date)
            element.send_keys(Keys.TAB)
            
            actual_value = element.get_attribute("value")
            return len(actual_value) > 5
    
    def _strategy_clear_and_type(self, input_id, formatted_date, target_dt):
        """Strategy 4: Clear field completely and type slowly"""
        element = self.wait.until(EC.element_to_be_clickable((By.ID, input_id)))
        
        # Multiple clearing attempts
        for _ in range(3):
            element.click()
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            element.clear()
            time.sleep(0.2)
        
        # Type slowly, character by character
        for char in formatted_date:
            element.send_keys(char)
            time.sleep(0.1)
        
        # Press Tab to confirm
        element.send_keys(Keys.TAB)
        time.sleep(0.5)
        
        actual_value = element.get_attribute("value")
        return len(actual_value) > 5
    
    def _navigate_calendar(self, calendar_popup, target_dt):
        """Navigate calendar widget to specific date"""
        try:
            # Get current displayed month/year
            current_month_year = calendar_popup.find_element(By.CSS_SELECTOR, ".ui-datepicker-title, .calendar-title")
            
            # Navigate to target month/year (simplified - would need more logic for distant dates)
            target_day = target_dt.day
            
            # Find the day button
            day_buttons = calendar_popup.find_elements(By.CSS_SELECTOR, "td a, .calendar-day")
            
            for button in day_buttons:
                if button.text.strip() == str(target_day):
                    button.click()
                    time.sleep(0.5)
                    return True
            
            return False
            
        except Exception as e:
            if self.debug:
                print(f"   ❌ Calendar navigation error: {e}")
            return False


class EnhancedAgMarkNetScraper:
    """Enhanced scraper with proper calendar handling"""
    
    def __init__(self, debug=True):
        self.debug = debug
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 20)
        self.calendar_handler = AgMarkNetCalendarHandler(self.driver, debug)
    
    def _setup_driver(self):
        """Setup Chrome driver with enhanced options"""
        chrome_options = webdriver.ChromeOptions()
        
        # Enhanced stability options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to appear more like regular browser
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Hide automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def scrape_data(self, 
                   commodity="17", 
                   state="UP", 
                   district="0", 
                   market="0",
                   from_date="01-Jan-2023", 
                   to_date="22-Sep-2025"):
        """Main scraping method with enhanced date handling"""
        
        try:
            if self.debug:
                print("🌐 Loading AgMarkNet...")
            
            self.driver.get("https://www.agmarknet.gov.in/SearchCmmMkt.aspx")
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.ID, "ddlCommodity")))
            time.sleep(2)
            
            if self.debug:
                print("✅ Page loaded")
            
            # Select commodity
            if self.debug:
                print(f"🌾 Selecting commodity: {commodity}")
            commodity_dropdown = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "ddlCommodity"))))
            commodity_dropdown.select_by_value(commodity)
            time.sleep(2)
            
            # Select state
            if self.debug:
                print(f"📍 Selecting state: {state}")
            state_dropdown = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "ddlState"))))
            state_dropdown.select_by_value(state)
            time.sleep(2)
            
            # Select district (if not default)
            if district != "0":
                if self.debug:
                    print(f"🏘️ Selecting district: {district}")
                district_dropdown = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "ddlDistrict"))))
                district_dropdown.select_by_value(district)
                time.sleep(1)
            
            # Select market (if not default)
            if market != "0":
                if self.debug:
                    print(f"🏪 Selecting market: {market}")
                market_dropdown = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "ddlMarket"))))
                market_dropdown.select_by_value(market)
                time.sleep(1)
            
            # Handle dates using enhanced calendar handler
            if not self.calendar_handler.handle_calendar_date("txtDate", from_date, "From Date"):
                raise Exception("Failed to set from date")
            
            if not self.calendar_handler.handle_calendar_date("txtDateTo", to_date, "To Date"):
                raise Exception("Failed to set to date")
            
            # Click search
            if self.debug:
                print("🔍 Clicking search...")
            
            search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "btnGo")))
            self.driver.execute_script("arguments[0].click();", search_button)
            
            # Wait for results
            if self.debug:
                print("⏳ Waiting for results...")
            
            # Wait for either results or no data message
            try:
                # Wait for the results table to appear
                wait_long = WebDriverWait(self.driver, 30)
                wait_long.until(EC.presence_of_element_located((By.ID, "cphBody_Grid")))
                
                # Get table HTML
                table_element = self.driver.find_element(By.ID, "cphBody_Grid")
                table_html = table_element.get_attribute("outerHTML")
                
                if self.debug:
                    print("✅ Results retrieved!")
                
                return table_html
                
            except TimeoutException:
                if self.debug:
                    print("⏰ Timeout waiting for results")
                return None
        
        except Exception as e:
            if self.debug:
                print(f"❌ Scraping error: {e}")
            self._save_debug_info()
            raise
    
    def _save_debug_info(self):
        """Save debug information"""
        try:
            timestamp = int(time.time())
            
            # Save screenshot
            screenshot_file = f"debug_screenshot_{timestamp}.png"
            self.driver.save_screenshot(screenshot_file)
            
            # Save page source
            html_file = f"debug_page_{timestamp}.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            
            if self.debug:
                print(f"💾 Debug files saved: {screenshot_file}, {html_file}")
                
        except Exception as e:
            if self.debug:
                print(f"⚠️ Could not save debug info: {e}")
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()


def parse_table(html):
    """Parse HTML table into structured data"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Find headers
    headers = []
    header_row = soup.find("tr")
    if header_row:
        for cell in header_row.find_all(["th", "td"]):
            text = cell.get_text(strip=True)
            if text:
                headers.append(text)
    
    if not headers:
        print("⚠️ No headers found in table")
        return []
    
    # Find data rows
    rows = []
    data_rows = soup.find_all("tr")[1:]  # Skip header row
    
    for row in data_rows:
        cells = []
        for cell in row.find_all(["td", "th"]):
            text = cell.get_text(strip=True)
            cells.append(text)
        
        if cells and len(cells) >= len(headers):
            row_data = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    row_data[header] = cells[i]
                else:
                    row_data[header] = ""
            rows.append(row_data)
    
    return rows


def scrape_multiple_crops():
    """Scrape data for multiple crops and districts"""
    crops = ["Tomato", "Potato", "Maize", "Coconut", "Ragi", "Wheat", "Rice", "Groundnut"]
    
    districts = [
        "Bagalkot", "Bangalore Rural", "Bangalore Urban", "Belgaum", "Bellary", "Bidar", 
        "Bijapur", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga", 
        "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Gulbarga", "Hassan", 
        "Haveri", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysore", "Raichur", 
        "Ramanagara", "Shimoga", "Tumkur", "Udupi", "Uttara Kannada", "Yadgir"
    ]
    
    # Commodity codes mapping (you'll need to find these from the website)
    commodity_codes = {
        "Tomato": "17", "Potato": "18", "Maize": "19", "Coconut": "20",
        "Ragi": "21", "Wheat": "22", "Rice": "23", "Groundnut": "24"
    }
    
    all_data = []
    scraper = EnhancedAgMarkNetScraper(debug=True)
    
    try:
        for crop in crops:
            print(f"\n🌾 Processing {crop}...")
            
            params = {
                "commodity": commodity_codes.get(crop, "0"),
                "state": "KK",
                "district": "0",
                "market": "0", 
                "from_date": "01-Jan-2023",
                "to_date": "22-Sep-2025"
            }
            
            table_html = scraper.scrape_data(**params)
            if table_html:
                rows = parse_table(table_html)
                for row in rows:
                    row['crop_name'] = crop
                all_data.extend(rows)
                print(f"   ✅ {len(rows)} records for {crop}")
            
            time.sleep(2)  # Rate limiting
            
    finally:
        scraper.close()
    
    if all_data:
        output_file = f"karnataka_all_crops_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        print(f"\n🎉 Total {len(all_data)} records saved to {output_file}")

def main():
    """Main execution function"""
    print("🚀 Enhanced AgMarkNet Scraper with Calendar Support")
    print("=" * 60)
    
    # Choose single crop or multiple crops
    choice = input("Scrape (1) Single crop or (2) All crops? Enter 1 or 2: ").strip()
    
    if choice == "2":
        scrape_multiple_crops()
        return
    
    # Single crop scraping (original code)
    scraping_params = {
        "commodity": "140",
        "state": "KK",
        "district": "0", 
        "market": "0",
        "from_date": "01-Jan-2023",
        "to_date": "22-Sep-2025"
    }
    
    scraper = None
    try:
        scraper = EnhancedAgMarkNetScraper(debug=True)
        table_html = scraper.scrape_data(**scraping_params)
        
        if table_html:
            rows = parse_table(table_html)
            if rows:
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(rows, f, indent=4, ensure_ascii=False)
                print(f"🎉 {len(rows)} records saved to {OUTPUT_FILE}")
        
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
