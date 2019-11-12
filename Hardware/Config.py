import json

from PyQt5.QtCore import QObject


def string_keys_to_int(dictionary):
    if type(dictionary) is not dict:
        return dictionary

    result = {}
    for key, value in dictionary.items():
        if key.isdigit():
            result[int(key)] = string_keys_to_int(value)
        else:
            result[key] = string_keys_to_int(value)

    return result


class JSONWrapper(QObject):
    def __init__(self, file_name, parent=None):
        super().__init__(parent)

        f = open(file_name)
        self.config = json.load(f)
        f.close()


class Config(JSONWrapper):
    def __init__(self, file_name, parent=None):
        super().__init__(file_name, parent)

        self.config = string_keys_to_int(self.config)


if __name__ == "__main__":
    cfg = Config("config.json")
