import time
import sys
import os
import re
import traceback

import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.options import Options as FireFoxOptions
from selenium.webdriver.firefox.service import Service as FireFoxService
from webdriver_manager.firefox import DriverManager as FireFoxDriverManager
from dotenv import load_dotenv

from libs.web_automation import WebAutomation
from collections import namedtuple


class Select2:
    Option = namedtuple('Option', 'text')

    # Javascript scripts -----------------------------------------------------------------------------------------------
    SELECT_BY_VALUE = \
    '''
    $(arguments[0]).val(arguments[1]);
    $(arguments[0]).trigger('change');
    '''

    GET_OPTIONS = \
    '''
    var myOpts = document.getElementById(arguments[0]).options;
    return myOpts;
    '''

    GET_SELECTIONS = \
    '''
    return $(arguments[0]).select2('data');
    '''
    # End Javascript scripts -------------------------------------------------------------------------------------------
    
    """Drop-in replacement for Selenium Select"""
    def __init__(self, webdriver, select_id: str):
        self.webdriver = webdriver
        self.select_id = select_id
        self.options = None

    def get_options(self):
        if not self.options:
            options_elements = self.webdriver.execute_script(GET_OPTIONS, self.select_id)
            self.options = {opt.text: opt.get_attribute('value') for opt in options_elements}
        return self.options

    def select_by_visible_text(self, text):
        options = self.get_options()
        value = options[text]
        self.select_by_value(value)

    def select_by_value(self, value):
        self.webdriver.execute_script(SELECT_BY_VALUE, '#' + self.select_id, value)

    @property
    def first_selected_option(self):
        selections = self.webdriver.execute_script(GET_SELECTIONS, '#' + self.select_id)
        option = self.Option(selections[0]['text'])
        return option


class MyScraper(WebAutomation):
    """
        https://chatgpt.com/c/b460b582-3f19-48e4-bd76-ae1f5c322890
    """
    
    def __init__(self):
        self.driver = None
        self.debug  = True

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

    def main(self):
        try:
            self.driver.maximize_window()
            self.driver.get('http://simplerest.lan/html_builder/select2')

            select2_countries = Select2(self.driver, 'countries')
            select2_countries.select_by_visible_text('Austria')

            # Espera un momento para que los cambios se reflejen
            time.sleep(5)

            # Aquí puedes añadir más acciones o verificaciones si es necesario

        except Exception as e:
            traceback.print_exc(limit=5)
        finally:
            self.quit(60)

if __name__ == "__main__":
    automation = MyScraper()
    automation.setup(False, False, 'Google')
    automation.main()
