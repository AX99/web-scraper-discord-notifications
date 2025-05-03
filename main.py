import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import requests
from flask import Flask, request

# Load environment variables
load_dotenv()

app = Flask(__name__)

def send_discord_message(message):
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    print(webhook_url)
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL environment variable not set")
        return None
        
    data = {
        'content': message,
        'username': 'Amazon Flex Monitor',
        'avatar_url': 'https://m.media-amazon.com/images/G/01/amazonFlexMarketing/flex-favicon.png'
    }
    return requests.post(webhook_url, json=data).status_code

@app.route('/', methods=['POST'])
def check_website():
    """
    Checks a website for a specific text and sends notifications via Discord.
    """
    website_url = os.environ.get('WEBSITE_URL')
    search_text = os.environ.get('SEARCH_TEXT')

    if not website_url or not search_text:
        error_message = "❌ Error: WEBSITE_URL and SEARCH_TEXT environment variables must be set."
        print(error_message)
        send_discord_message(error_message)
        return error_message, 400

    try:
        print(f"🔍 Starting check for text: '{search_text}' on {website_url}")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        print("🚀 Initializing Chrome WebDriver...")
        # Initialize the Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            print(f"🌐 Navigating to {website_url}")
            # Navigate to the website
            driver.get(website_url)
            
            # Wait for the content to load (up to 10 seconds)
            wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds
            
            # Wait for page load
            print("⏳ Waiting for page to be fully loaded...")
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            
            # Add a small delay to allow dynamic content to render
            driver.implicitly_wait(5)
            
            # Try different selectors
            selectors = [
                'div.swa-body.desktop div div div:nth-child(3) div:nth-child(9) div',
                'body > div.swa-body.desktop > div > div > div:nth-child(3) > div:nth-child(9) > div',
                '/html/body/div/div/div/div[3]/div[9]/div',
            ]
            
            print("🔎 Trying to find target element...")
            target_element = None
            for selector in selectors:
                try:
                    print(f"  Trying selector: {selector}")
                    if selector.startswith('/'):
                        target_element = wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        # Wait for element to be visible and have text
                        target_element = wait.until(
                            EC.visibility_of_element_located((By.XPATH, selector))
                        )
                    else:
                        target_element = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        # Wait for element to be visible and have text
                        target_element = wait.until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    if target_element:
                        # Wait a moment for any dynamic text to load
                        driver.execute_script("return arguments[0].innerText;", target_element)
                        print(f"✅ Found element with selector: {selector}")
                        break
                except Exception as e:
                    print(f"  ❌ Selector failed: {str(e)}")
                    continue
            
            if not target_element:
                message = f"⚠️ Target element not found on {website_url}"
                print(message)
                send_discord_message(message)
                return message, 200
            
            # Get the text content
            element_text = target_element.text.strip()
            print(f"📝 Element text: '{element_text}'")
            print(f"🔍 Searching for: '{search_text}'")
            
            if search_text.lower() not in element_text.lower():
                message = f"🔍 Text '{search_text}' not found in target element on {website_url}"
                print(f"❌ Text not found. Full element text: '{element_text}'")
            else:
                message = f"🎉 Found: '{search_text}' on {website_url}"
                print(f"✅ Text found in: '{element_text}'")
            
            # Send notification
            send_discord_message(message)
            
            print(message)
            return message, 200
                
        finally:
            print("🛑 Closing WebDriver")
            driver.quit()

    except Exception as e:
        error_message = f"❌ Error: {e}"
        print(error_message)
        send_discord_message(error_message)
        return error_message, 500

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
