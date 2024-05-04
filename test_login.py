from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.options import Options as FireFoxOptions
from selenium.webdriver.firefox.service import Service as FireFoxService
from webdriver_manager.firefox import DriverManager as FireFoxDriverManager

import time
import sys
import os
from dotenv import load_dotenv

class WebAutomation:
    def __init__(self):
        self.driver = None

    def nav(self, slug, delay=0):
        site_url = self.login_data['site_url'].rstrip('/')
        self.driver.get(site_url + '/' + slug)
        time.sleep(delay)


    def setup(self, is_prod=False, install=False, web_driver='Google'):
        options = ChromeOptions() if web_driver == 'Google' else FireFoxOptions() if web_driver == 'FireFox' else None

        if options is None:
            raise ValueError(f"Unsupported web driver: {web_driver}. Supported options are 'Chrome' and 'Firefox'")
        
        if is_prod:
            # prod
            options.add_argument('--headless=new')
        else:
            # dev
            options.add_extension("DarkReader.crx")    

        # options.add_argument("--headless")
        # options.add_argument('--headless=new')
        # options.add_argument("start-maximized")
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')
        # option.binary_location = "/path/to/google-chrome"

        if install:  
            if (web_driver == 'Google'):
                self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) 

            if (web_driver == 'FireFox'):
                self.driver = webdriver.Firefox(service=ChromeService(FireFoxDriverManager().install()), options=options) 
        else:
            if (web_driver == 'Google'):
                self.driver = webdriver.Chrome(options=options)

            if (web_driver == 'FireFox'):
                self.driver = webdriver.Firefox(options=options)


    def load_instructions(self, test_file):
        instructions = {}
        test_file_path = os.path.join('tests', test_file)
       
        if not os.path.isfile(test_file_path):
            print(f"Error: File '{test_file}' not found.")
            return

        with open(test_file_path, 'r') as f:
            exec(f.read(), instructions)
            
        return instructions

    def main(self):
        instructions    = self.load_instructions('gourmet.py')

        self.login_data = instructions.get('login_data')

        try:
            self.nav(self.login_data['login_page'], 10)

            # Capturar el HTML renderizado
            html = self.driver.page_source
            with open('login_page.html', 'w') as f:
                f.write(html)
            
            username_input = self.driver.find_element(By.ID, 'user_login')
            username_input.send_keys(self.login_data['log'])

            password_input = self.driver.find_element(By.ID, 'user_pass')
            password_input.send_keys(self.login_data['pwd'])

            login_button = self.driver.find_element(By.ID, 'wp-submit')
            login_button.click()


        finally:
            print("Esperando para salir")
            # time.sleep(60)

   


if __name__ == "__main__":
    automation = WebAutomation()

    # 
    # .env
    #
    # pip install python-dotenv
    #
    # https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1
    #

    load_dotenv()

    if os.getenv('IS_PRODUCTION') == 'True':
        is_prod = True
    else:
        is_prod = False

    web_driver = os.getenv('WEB_DRIVER')


    automation.setup(is_prod, False, web_driver)
    automation.main()
