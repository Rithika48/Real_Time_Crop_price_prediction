from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def inspect_agmarknet():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        print("Loading AgMarkNet...")
        driver.get("https://www.agmarknet.gov.in/SearchCmmMkt.aspx")
        time.sleep(5)
        
        # Save page source
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        # Find all select elements
        selects = driver.find_elements("tag name", "select")
        print(f"Found {len(selects)} select elements:")
        
        for i, select in enumerate(selects):
            try:
                select_id = select.get_attribute("id")
                options = select.find_elements("tag name", "option")
                print(f"  {i+1}. ID: {select_id}, Options: {len(options)}")
                
                if "commodity" in select_id.lower():
                    print("    Commodity options:")
                    for opt in options[:10]:  # First 10 options
                        value = opt.get_attribute("value")
                        text = opt.text.strip()
                        if text:
                            print(f"      {value}: {text}")
            except:
                pass
        
        print("\nPage title:", driver.title)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_agmarknet()
