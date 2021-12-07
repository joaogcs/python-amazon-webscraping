# from config.app import App
import os
import csv
import logging
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

""" AttributeManager is a simple class to handle attributes,  
    can be created inside __init__ e.g.: self.attributes = AttributeManager()
    or as a Base Class """


class AttributeManager(object):

    def __init__(self, **kwargs):
        self.__attributes = {}
        for key, value in kwargs.items():
            self.__attributes.update({key: value})

    @property
    def attributes(self):
        return self.__attributes

    @attributes.setter
    def attributes(self, var):
        for key, value in var.items():
            logging.debug(f'Setting {key} to {value}')
            self.__attributes.update({key: value})

    def has_attribute(self, key):
        return True if key in self.attributes else False

    def get_attributes_by_key(self, *args):
        result = {}
        for key in args:
            if key in self.__attributes:
                result.update({key: self.__attributes.get(key)})
        return result

    def get_attributes_by_value(self, *args):
        result = {}
        for value in args:
            if value in self.__attributes.values():
                for key, v in self.__attributes.items():
                    if value == v:
                        result.update({key: value})
        return result

    def add_attribute(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.__attributes:
                self.__attributes.update({key: value})

    def update_attribute(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__attributes:
                self.__attributes.update({key: value})

    def remove_attribute(self, *args):
        for key in args:
            if key in self.__attributes:
                del self.__attributes[key]


""" Item class is the class that handles products attributes in search results
    Could be any attribute, could be a validation function and other methods """


class Item(AttributeManager):
    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)

    def print_all_attributes(self):
        for index, (key, value) in enumerate(self.attributes.items()):
            print(f'{index} -> {key}: {value}')


""" App which handles WebDriver 
    something like a Factory design """


class App(AttributeManager):
    def __init__(self, **kwargs):
        super(App, self).__init__(**kwargs)

        # default setup if it was not passed as parameter (it will not overwrite value if it was already created)
        self.add_attribute(silent_mode=False)
        self.add_attribute(timeout=5)
        self.add_attribute(webdriver=None)

    # Run main (could bypass silently default mode configuration for test purposes)
    def run(self):

        logging.info(
            f"Running app with silent mode set to {self.attributes['silent_mode']}")

        options = webdriver.ChromeOptions()
        if self.attributes['silent_mode']:
            options.add_argument("--headless") 


        
        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-setuid-sandbox") 
        options.add_argument("--disable-dev-shm-using") 
        options.add_argument("--disable-extensions") 
        options.add_argument("--disable-gpu") 
        options.add_argument("disable-infobars")

        self.attributes['webdriver'] = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def close(self):
        logging.info(f"Closing app")
        if self.attributes['webdriver']:
            self.attributes['webdriver'].close()

    def goto(self, url, **kwargs):
        logging.info(f"Navigating to --> {url}")
        self.attributes['webdriver'].get(url)
        get_element_by = By.ID if 'get_element_by' not in kwargs else kwargs.get('get_element_by')
        value = False if 'value' not in kwargs else kwargs.get('value')
        if value:
            self.wait_until(timeout=self.attributes['timeout'], get_element_by=get_element_by, value=value)

    def wait_until(self, **kwargs):
        timeout = 5 if 'timeout' not in kwargs else kwargs.get('timeout')
        get_element_by = By.ID if 'get_element_by' not in kwargs else kwargs.get('get_element_by')
        value = "" if 'value' not in kwargs else kwargs.get('value')
        if get_element_by:
            for attempt in range(10):
                try:
                    WebDriverWait(self.attributes['webdriver'], timeout).until(
                        EC.presence_of_element_located((get_element_by, value)))
                    break
                except TimeoutException:
                    logging.warning(
                        f"Loading took more than {self.attributes['timeout']} seconds! Going for {attempt} attempt "
                        f"out of 10")
                    pass
            else:
                logging.fatal(f"Loading is taking too long, aborting...")
                # raise


""" AmazonSearch application which contains all control tools about what can be done within amazon website.
    The logic and flux are at Main()    
"""


class AmazonSearch(App):
    def __init__(self, silent_mode=False, timeout=5, **kwargs):
        self._url = "https://www.amazon.com" if 'url' not in kwargs else kwargs.get('url')

        super(AmazonSearch, self).__init__(silent_mode=silent_mode, timeout=timeout)

        # List of result Items
        self.search_result_items = []

        self.last_search_text = ""  # could be stored with items to know what is the source of each result...

    def search_for(self, value):
        self.last_search_text = value

        logging.info(f"Inserting search text: {value}")
        search_input = self.attributes['webdriver'].find_element_by_css_selector("input[id='twotabsearchtextbox']")
        search_input.send_keys(value)

        time.sleep(2)

        logging.info(f"Submitting search")
        search_button = self.attributes['webdriver'].find_element_by_css_selector("input[type='submit']")
        search_button.click()

    def get_search_result(self):

        list_of_items = []

        logging.info(f"Waiting for page to get loaded")
        self.wait_until(get_element_by=By.XPATH, value='//*[@class="a-last"]')

        logging.info(f"Getting items elements in search page")
        list_of_item_elements = self.attributes['webdriver'].find_elements_by_xpath(
            './/div[@data-component-type="s-search-result"]')

        if len(list_of_item_elements) > 0:
            for item_element in list_of_item_elements:
                flag_price_found = False
                item_name, item_price, item_price_whole, item_price_fraction = "", "", "", ""

                try:
                    item_name = item_element.find_element_by_xpath(
                        './/span[@class="a-size-base-plus a-color-base a-text-normal"]').text
                except NoSuchElementException:
                    item_name = "NAME NOT FOUND!"
                    pass
                try:
                    item_price_whole = item_element.find_element_by_xpath(
                        './/span[@class="a-price-whole"]').text
                    item_price_fraction = item_element.find_element_by_xpath(
                        './/span[@class="a-price-fraction"]').text
                    flag_price_found = True
                except NoSuchElementException:
                    item_price = None

                if flag_price_found:
                    item_price = float(item_price_whole.replace(".", "")) + float(item_price_fraction) / 100.0

                item = Item(name=item_name, price=item_price)
                list_of_items.append(item)

        logging.debug(f"List of items found:")
        for index, item in enumerate(list_of_items):
            logging.debug(f"{index} -> name  {item.attributes['name']}")
            logging.debug(f"{index} -> price {item.attributes['price']}")
        logging.debug(f"Elements found {len(list_of_item_elements)}")
        logging.debug(f"Items assigned {len(list_of_items)}")

        return list_of_items

    def next_result_page(self):
        time.sleep(2)
        try:
            next_button = self.attributes['webdriver'].find_element_by_xpath(
                '//*[@class="a-last"]').find_element_by_css_selector("*")
            next_button.click()
        except NoSuchElementException:
            logging.warning('Next page button not found')
            pass

    def get_items_through_pages(self, number_of_pages=1):
        result = []
        for page in range(1, number_of_pages + 1):
            page_result = self.get_search_result()
            [item.add_attribute(found_in_page=page) for item in page_result]
            result.extend(page_result)
            logging.info(
                f"Page {page} has {len(page_result)} items, already found a total {len(result)} of items")
            self.next_result_page()
        return result

    def save_search(self, list_to_save, file_name='search', delimiter=','):

        now = datetime.now()
        dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")
        file_name = './csvs/' + file_name + dt_string + '.csv'

        if not os.path.exists(os.path.dirname(file_name)):
            try:
                os.makedirs(os.path.dirname(file_name))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        logging.info(f'Saving {len(list_to_save)} results to {file_name}')
        with open(file_name, mode='w+') as file:
            writer = csv.writer(file, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

            header = list(list_to_save[0].attributes.keys())
            writer.writerow(header)
            for item in list_to_save:
                row_values = list(item.attributes.values())
                writer.writerow(row_values)
        logging.info(f'Results saved!')
