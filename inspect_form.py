from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def inspect_form():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        print("Inspecting form structure...")
        driver.get("https://agmarknet.gov.in/datewisespeccommdodityinput")
        time.sleep(5)
        
        print("Page title:", driver.title)
        print("Current URL:", driver.current_url)
        
        # Check for select elements
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"Found {len(selects)} select elements")
        
        for i, select in enumerate(selects):
            print(f"Select {i+1}:")
            print(f"  Name: {select.get_attribute('name')}")
            print(f"  ID: {select.get_attribute('id')}")
            options = select.find_elements(By.TAG_NAME, "option")
            print(f"  Options: {len(options)}")
            if options:
                print(f"  First few options: {[opt.text for opt in options[:5]]}")
        
        # Check for input elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\nFound {len(inputs)} input elements")
        
        # Check for buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} button elements")
        
        # Save page source for inspection
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to page_source.html")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_form()
