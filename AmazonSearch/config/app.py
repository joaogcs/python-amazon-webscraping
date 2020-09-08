import codecs
import configparser
import os


class App:
    __propertiesRelativePath = "app.properties"

    __config_file_path = os.path.join(os.path.dirname(__file__), __propertiesRelativePath)
    config = configparser.ConfigParser()
    with codecs.open(__config_file_path, 'r', encoding='utf-8') as f:
        config.read_file(f)
