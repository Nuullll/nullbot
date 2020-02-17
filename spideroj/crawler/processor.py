from typing import Union, List


class JsonParser(object):

    @staticmethod
    def default(obj: dict) -> None:
        return None


class Cleaner(object):

    @staticmethod
    def default(x: str) -> Union[int, str]:
        try:
            return Cleaner.get_int(x)
        except ValueError:
            return x

    @staticmethod
    def get_int(x: str) -> int:
        return int(x.strip())

    @staticmethod
    def get_fraction(x: str) -> List[int]:
        return [Cleaner.get_int(v) for v in x.split('/')]

    @staticmethod
    def get_percent(x: str) -> float:
        return float(x.split('%')[0].strip()) / 100
