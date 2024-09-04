import json
import os


class ClassesDataManager:
    def __init__(self, path):
        self.path = path

        # Create file if it doesn't exist
        if not os.path.exists(self.path):
            with open(self.path, 'a') as _:
                pass

    def __read_file(self):
        with open(self.path) as file:
            return json.load(file)

    def get(self, key):
        data = self.__read_file()
        return data.get(key)

    def set(self, key, value):
        data = self.__read_file()

        data[key] = value
        with open(self.path, 'w') as file:
            json.dump(data, file, indent=4)
