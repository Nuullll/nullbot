from typing import Callable, Any

from spideroj.crawler.processor import JsonParser, Cleaner


class Field(object):
    """
    Abstraction of a xpath-selectable or json-parsable field on the webpages. A cleaner can also be bind to a Field.
    """
    def __init__(self, name: str, xpath_selector: str = '', json_parser: Callable[[dict], Any] = JsonParser.default,
                 cleaner: Callable[[str], Any] = Cleaner.default):
        self.name = name

        self.xpath_selector = xpath_selector
        self.json_parser = json_parser

        self.cleaner = cleaner
    
    def serialize(self, value):
        return f"{self.name}: {value}"