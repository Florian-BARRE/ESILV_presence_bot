from configuration import APP_CONFIG

from portal.object import Portal
from classes_data_manager import classes_data

portal = Portal(
    email=APP_CONFIG.EMAIL,
    mdp=APP_CONFIG.MDP,
    url=APP_CONFIG.URL,
    sessions_path=APP_CONFIG.SESSIONS_PATH,
    data_storage_manager=classes_data,
    max_load_wait=APP_CONFIG.MAX_LOAD_WAIT
)
