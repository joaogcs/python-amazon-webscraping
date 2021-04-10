import logging
from selenium.webdriver.common.by import By
from src.bin.app import AmazonSearch


def main():
    # create AmazonSearch app. Optional silent_mode (Default is False)
    amazonsearch = AmazonSearch(silent_mode=False)
    try:
        # Run AmazonSearch app
        amazonsearch.run()
        # Go to url (required) and wait for element to be located (optional)
        amazonsearch.goto("https://www.amazon.com.br/", get_element_by=By.ID, value='twotabsearchtextbox')
        # Search for some text in amazon br in all site
        amazonsearch.search_for("iPhone")
        # Get items from result page. Optional set number_of_pages to whatever you want.
        list_of_items = amazonsearch.get_items_through_pages(number_of_pages=2)
        # Save result (required) to csv file in main folder.File name and delimiter are Optional.
        amazonsearch.save_search(list_to_save=list_of_items, file_name='search_result_', delimiter=';')
        # close app, end script
        amazonsearch.close()

    except Exception as e:
        logging.fatal(f"{e}")
        amazonsearch.close()
    finally:
        pass


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()
