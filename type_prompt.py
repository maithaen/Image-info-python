import getpass
import os
from pathlib import Path
from time import sleep
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException

# Constants
WAIT_TIME = 10
MIN_TYPE_DELAY = 0.05
MAX_TYPE_DELAY = 0.2
PROMPT_PROCESSING_DELAY = 15

def emulate_typing(element, text, min_delay=MIN_TYPE_DELAY, max_delay=MAX_TYPE_DELAY):
    """
    Emulate human-like typing in a web element with improved randomness.
    """
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))
    
    # Add a random pause after typing to mimic human behavior
    time.sleep(random.uniform(0.3, 0.7))

def get_chrome_options():
    """
    Configure and return Chrome options for WebDriver with additional settings.
    """
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--start-maximized")  # Start with maximized window
    options.add_argument("--disable-extensions")  # Disable extensions for better performance
    return options

def open_chrome_with_profile(profile_path):
    """
    Open Chrome with a specific user profile and enhanced error handling.
    """
    chrome_options = get_chrome_options()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except WebDriverException as e:
        print(f"Error initializing WebDriver: {e}")
        return None

def open_leonardo_ai_profile(profile_number):
    """
    Open Leonardo AI with a specific Chrome profile and navigate to the image generation page.
    """
    profile_path = Path(os.path.expanduser("~")) / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / f"Profile {profile_number}"
    driver = open_chrome_with_profile(str(profile_path))
    if driver:
        driver.get("https://app.leonardo.ai/image-generation")
        return driver
    return None

def process_prompts(driver, excel_file, sheet_name):
    """
    Read prompts from an excel sheet and interact with the Leonardo AI prompt input field.
    """
    df = pd.read_excel(io=excel_file, sheet_name=sheet_name, index_col=0)
    wait = WebDriverWait(driver, WAIT_TIME)

    try:
        label_prompt = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="prompt-input"]')))
    except TimeoutException:
        print("Timeout waiting for prompt input field. Check if the page loaded correctly.")
        return

    for index, text in enumerate(df.prompt, 1):
        print(f"Processing prompt {index}/{len(df)}: {text}")
        label_prompt.click()
        label_prompt.send_keys(Keys.CONTROL + 'a' + Keys.BACKSPACE)  # Clear prompt
        emulate_typing(label_prompt, text)
        sleep(random.uniform(1.5, 2.5))  # Random delay before submitting
        label_prompt.send_keys(Keys.ENTER)
        
        # Dynamic wait time based on prompt length
        # wait_time = max(PROMPT_PROCESSING_DELAY, len(text) * 0.5)
        sleep(PROMPT_PROCESSING_DELAY)

def main():
    """
    Main function to define profile number, read excel file and call processing function.
    """
    profile_number = 1 
    excel_file_path = Path(r"D:\Ai_leonado\day24\picture frame_prompts.xlsx")
    sheet_name = f"Sheet{profile_number}"

    driver = open_leonardo_ai_profile(profile_number)
    if not driver:
        print("Failed to initialize WebDriver. Exiting.")
        return

    try:
        process_prompts(driver, excel_file_path, sheet_name)
    except Exception as e:
        print(f"Error encountered: {e}")
    finally:
        print("Closing browser...")
        sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()
