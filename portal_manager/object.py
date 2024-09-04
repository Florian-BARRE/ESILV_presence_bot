from tools import get_current_day_timestamp, get_current_timestamp, dprint
import time


class PortalManager:
    """
        Constrcutor
    """

    def __init__(
            self,
            portal, data_manager,
            refresh_interval, idle_refresh_interval,
            start_classes_time, end_classes_time,
            bot_telegram
    ):
        self.portal = portal
        self.data_manager = data_manager
        self.refresh_interval = refresh_interval
        self.idle_refresh_interval = idle_refresh_interval

        self.start_classes_time = start_classes_time
        self.end_classes_time = end_classes_time

        self.bot_telegram = bot_telegram

        # Used later
        self.first_run = True
        self.classes = []
        self.no_classes_remaining = False
        self.current_classe_index = -1
        self.last_idle_refresh = 0

    """
        Private methods
    """

    def __get_classe_info(self, key):
        if self.current_classe_index < len(self.classes):
            return self.classes[self.current_classe_index].get(key, None)
        return None

    def __set_classe_info(self, key, value):
        if self.current_classe_index < len(self.classes):
            self.classes[self.current_classe_index][key] = value
            self.data_manager.set("classes", self.classes)

    def __clear_classes_inspector_cache(self):
        self.first_run = True
        self.classes = []
        self.no_classes_remaining = False
        self.current_classe_index = -1
        self.last_idle_refresh = 0

    def __first_run_setup(self):
        dprint("First run setup.", priority_level=2, source="PORTAL_MANAGER")
        self.classes = self.portal.get_classes()
        # If the current classes are not already stored (this instance don't run after an old one)
        if not self.portal.check_if_classes_are_already_stored(self.classes):
            self.data_manager.set("classes", self.classes)
            dprint("The current classes are not already stored.", priority_level=3, source="PORTAL_MANAGER")
        else:
            self.classes = self.data_manager.get("classes")
            dprint("The current classes are already stored, let's load them.", priority_level=3,
                   source="PORTAL_MANAGER")

        self.current_classe_index = self.portal.get_current_classe_index()
        self.first_run = False
        dprint(f"The current classe index (compute by schedule hours) is "
               f"[{self.current_classe_index}/{len(self.classes)}].",
               priority_level=2, source="PORTAL_MANAGER")

    def __refresh_page(self):
        dprint("Refreshing the page.", priority_level=5, source="PORTAL_MANAGER")
        self.portal.web.refresh()
        self.last_idle_refresh = get_current_timestamp()

    def __idle_refresh_handle(self):
        if get_current_timestamp() - self.last_idle_refresh > self.idle_refresh_interval:
            dprint("Idle refreshing the page.", priority_level=4, source="PORTAL_MANAGER")
            self.__refresh_page()

    def __start_portal(self):
        dprint("Open portal and go to presence page.", priority_level=2, source="PORTAL_MANAGER")
        self.portal.create_web_instance()
        self.portal.open_esilv_website()
        self.portal.login_to_portal()
        self.portal.go_to_presence_page()

    """
        Test methods
    """

    def _check_register(self):
        if not self.__get_classe_info("register_opened"):
            if self.portal.is_register_open(self.current_classe_index):
                dprint(
                    f"Register for class [{self.__get_classe_info('name')}] is open !",
                    priority_level=2, source="PORTAL_MANAGER"
                )
                self.__set_classe_info("register_opened", True)

    def _send_notification_if_needed(self):
        if self.__get_classe_info("register_opened") and not self.__get_classe_info("notif_sent"):
            dprint(
                f"Sending notification for class [{self.__get_classe_info('name')}]...",
                priority_level=2, source="PORTAL_MANAGER"
            )
            alert_msg = f"#--- APPEL ---#\n" \
                        f"#- Cours :\n" \
                        f"#-- {self.__get_classe_info('name')}\n\n" \
                        f"#- Lien présence :\n" \
                        f"#-- {self.portal.web.current_url}\n\n" \
                        f"#- Lien ZOOM :\n" \
                        f"#-- {self.__get_classe_info('ZOOM_link')}\n\n"

            self.bot_telegram.send_text(alert_msg)
            self.__set_classe_info("notif_sent", True)

    def _pass_to_next_classe(self):
        if self.__get_classe_info("register_opened") and self.__get_classe_info("notif_sent"):
            dprint(
                f"Class [{self.__get_classe_info('name')}] is passed, let's move to the next one.",
                priority_level=2, source="PORTAL_MANAGER"
            )
            self.current_classe_index += 1

    def _wait_next_classes(self):
        while get_current_day_timestamp() < self.classes[self.current_classe_index]["start"]:
            self.__idle_refresh_handle()

    def _inspection_loop(self):
        # For the first run we need to get back the state of the last manager instance
        # (don't alert a second time for the same class)
        if self.first_run:
            self.__first_run_setup()

        # If no classes are remaining -> exit the loop and wait the next day
        if self.current_classe_index == -1:
            self.no_classes_remaining = True
            return

        # Check if the register is open (don't check if we already know that it is open)
        self._check_register()

        # Send the notification if the register is open and the notification is not already sent
        self._send_notification_if_needed()

        # Pass to the next class if the register is open and the notification is sent
        self._pass_to_next_classe()

        # Check if there is remaining classes
        if self.current_classe_index >= len(self.classes):
            dprint("No classes remaining. Exit day loop.", priority_level=2, source="PORTAL_MANAGER")
            self.no_classes_remaining = True
            return

        # If the register is open and the notification is sent, wait the next class
        # Without refreshing the page
        self._wait_next_classes()

        # Wait before the next iteration and refresh the page
        time.sleep(self.refresh_interval)
        self.__refresh_page()

    """
        Public methods
    """

    def run(self):
        current_time = get_current_day_timestamp()

        # Wait until we are during the working hours and working days
        while not self.start_classes_time <= current_time <= self.end_classes_time or self.no_classes_remaining:
            current_time = get_current_day_timestamp()

            # If there was a previous instance of the manager -> close web instance during waiting
            if not self.first_run:
                self.portal.clear_web_instances(debug=False)

            # Reset the manager cache states (flag no_classes_remaining, classe index, ...) at 00:00
            if current_time == 0:
                self.__clear_classes_inspector_cache()

        if self.first_run:
            self.__start_portal()

        # During working hours and working days -> run the inspection loop
        self._inspection_loop()

    def loop(self):
        dprint("Starting the portal manager...", priority_level=1, source="PORTAL_MANAGER")
        while True:
            try:
                self.run()
            except Exception as error:
                dprint(f"An error occurred: {error}", priority_level=1, source="PORTAL_MANAGER")
                dprint("Let's restart scraper bot !", priority_level=2, source="PORTAL_MANAGER")
                self.portal.clear_web_instances()
                self.__clear_classes_inspector_cache()
