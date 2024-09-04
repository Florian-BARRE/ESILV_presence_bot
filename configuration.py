import json
import os


def load_json_file(file_path):
    try:
        with open(file_path) as config:
            file_json = json.load(config)
    except FileNotFoundError:
        try:
            with open(os.path.join(BASE_DIR, file_path)) as config:
                file_json = json.load(config)
        except Exception:
            raise

    return file_json


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SECRET_FILE_PATH = os.path.join('config', 'secrets.json')
CONFIG_FILE_PATH = os.path.join('config', 'configuration.json')

SECRET_CONFIG_STORE = load_json_file(SECRET_FILE_PATH)
CONFIG_STORE = load_json_file(CONFIG_FILE_PATH)


class Config:
    # General
    APPLICATION_NAME = 'ESILV presence notifier'
    BASE_DIR = BASE_DIR

    # Secret config
    EMAIL = os.getenv('EMAIL', SECRET_CONFIG_STORE["email"])
    MDP = os.getenv('MDP', SECRET_CONFIG_STORE["mdp"])
    TOKEN = os.getenv('TOKEN', SECRET_CONFIG_STORE["token"])
    CHATID = os.getenv('CHATID', SECRET_CONFIG_STORE["chatID"])

    # Config
    PRIORITY_DEBUG_LEVEL = int(os.getenv('PRIORITY_DEBUG_LEVEL', CONFIG_STORE["priority_debug_level"]))
    URL = os.getenv('URL', CONFIG_STORE["url"])
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', CONFIG_STORE["refresh_interval"]))
    SESSIONS_PATH = os.getenv('SESSIONS_PATH', CONFIG_STORE["sessions_path"])
    CLASSES_DATA_PATH = os.getenv('CLASSES_DATA_PATH', CONFIG_STORE["classes_data_path"])
    MAX_LOAD_WAIT = int(os.getenv('MAX_LOAD_WAIT', CONFIG_STORE["max_load_wait"]))
    IDLE_REFRESH_INTERVAL = int(os.getenv('IDLE_REFRESH_INTERVAL', CONFIG_STORE["idle_refresh_interval"]))

    # Convert to timestamp
    DAY_START_HOUR = os.getenv('DAY_START_HOUR', CONFIG_STORE["day_start_hour"])
    DAY_START_HOUR = int(DAY_START_HOUR.split(":")[0]) * 3600 + int(DAY_START_HOUR.split(":")[1]) * 60
    DAY_END_HOUR = os.getenv('DAY_END_HOUR', CONFIG_STORE["day_end_hour"])
    DAY_END_HOUR = int(DAY_END_HOUR.split(":")[0]) * 3600 + int(DAY_END_HOUR.split(":")[1]) * 60



class Configuration(dict):
    def from_object(self, obj):
        for attr in dir(obj):

            if not attr.isupper():
                continue

            self[attr] = getattr(obj, attr)

        self.__dict__ = self


APP_CONFIG = Configuration()
APP_CONFIG.from_object(Config)
