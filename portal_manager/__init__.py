from configuration import APP_CONFIG

from portal import portal
from classes_data_manager import classes_data
from telegram import bot_telegram

from portal_manager.object import PortalManager

portal_manager = PortalManager(
    portal,
    classes_data,
    refresh_interval=APP_CONFIG.REFRESH_INTERVAL,
    start_classes_time=APP_CONFIG.DAY_START_HOUR,
    end_classes_time=APP_CONFIG.DAY_END_HOUR,
    idle_refresh_interval=APP_CONFIG.IDLE_REFRESH_INTERVAL,
    bot_telegram=bot_telegram
)
