from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import tools

import time


class Portal:
    def __init__(self, email, mdp, url, sessions_path, data_storage_manager, max_load_wait):
        self.email = email
        self.mdp = mdp
        self.url = url
        self.sessions_path = sessions_path
        self.data_storage_manager = data_storage_manager
        self.max_load_wait = max_load_wait

        # Define later
        self.web = None

    def create_web_instance(self):
        self.clear_web_instances()
        self.web = webdriver.Firefox()
        tools.dprint("Web instance has been created.", priority_level=3, source="PORTAL")

        # Add current sessions ID and executor url in textfile to save it
        # (it will be used to destroy this instance if there is a problem)
        # with open(self.sessions_path, 'a') as file:
        #    file.write(f"{self.web.session_id}|{self.web.command_executor._url}\n")

    def clear_web_instances(self, debug=True):
        """
        with open(self.sessions_path, 'r') as file:
            sessions = file.readlines()

        for session in sessions:
            session_id, command_executor_url = session.strip().split('|')

            try:
                driver = webdriver.Remote(
                    command_executor=command_executor_url,
                    options=FirefoxOptions()
                )
                driver.session_id = session_id
                driver.quit()
            except Exception as e:
                print(f"Error: {e}")
        """
        if debug:
            tools.dprint("Clear web instance.", priority_level=3, source="PORTAL")
        if self.web is not None:
            self.web.quit()
            self.web = None
            tools.dprint("One has been deleted !", priority_level=4, source="PORTAL")

    def get_extra_url(self):
        if self.web is None:
            raise Exception("FATAL ERROR: Web instance not created")

        current_url = self.web.current_url

        # 2 cases: classic url (www.leonard-de-vinci.net) or connexion url adfs.devinci.fr
        if "leonard-de-vinci.net" in current_url.split("/")[2]:
            current_url = current_url.replace(self.url, "")
            return current_url.split("/")[:-1]
        else:
            return []

    def get_current_page(self):
        path_list = self.get_extra_url()

        # If we don't know the page -> refresh and try again (the page could be not full loading)
        # Max tries = 2
        found_page = None
        for attempt in range(2):
            # Page "presences"
            if len(path_list) > 0 and path_list[-1] == "presences":
                found_page = "presences"

            # Pages login and home
            if len(path_list) == 0:
                # Page "login" (first page with only email to fill)
                # To identify this page, we check if the class "container" is present
                try:
                    self.web.find_element(By.CLASS_NAME, "container")
                    found_page = "login_email"
                except:
                    pass

                # Page "login" (second page with email and password to fill)
                # To identify this page, we check if the id "fullPage"
                try:
                    self.web.find_element(By.ID, "fullPage")
                    found_page = "login_email_password"
                except:
                    pass

                # Page "home" (after login)
                # To identify this page, we check if there is a 'a' ctn with the text "Mon tableau de bord"
                try:
                    self.web.find_element(By.LINK_TEXT, "Mon tableau de bord")
                    found_page = "home"
                except:
                    pass

            if found_page is not None or attempt == 1:
                return found_page

            # Wait and try again
            time.sleep(5)

    def wait_expected_page_is_loaded(self, expected_page):
        start_time = tools.get_current_timestamp()
        while tools.get_current_timestamp() - start_time < self.max_load_wait:
            if self.get_current_page() == expected_page:
                return
            time.sleep(1)

        tools.dprint(f"ERROR: Page [{expected_page}] not loaded in time", priority_level=1, source="PORTAL")
        raise Exception(f"ERROR: Page [{expected_page}] not loaded in time")

    def open_esilv_website(self):
        if self.web is None:
            raise Exception("FATAL ERROR: Web instance not created")

        # Connexion login page
        self.web.get(self.url)

        self.wait_expected_page_is_loaded("login_email")
        tools.dprint("ESILV website has been opened.", priority_level=3, source="PORTAL")

    '''
    Pages navigation functions
    '''

    def login_to_portal(self):
        # Fill Email
        login_ctn = self.web.find_element(By.ID, "login")
        login_ctn.send_keys(self.email)

        # Click to next page
        next_btn = self.web.find_element(By.ID, "btn_next")
        next_btn.click()

        # Fill password
        password_ctn = self.web.find_element(By.ID, "passwordInput")
        password_ctn.send_keys(self.mdp)

        # Connexion
        login_btn = self.web.find_element(By.ID, "submitButton")
        time.sleep(1)
        login_btn.click()

        self.wait_expected_page_is_loaded("home")
        tools.dprint("Login on portal has been done.", priority_level=3, source="PORTAL")

    def go_to_presence_page(self):
        # Go to "Relevés de présence"
        a_ctns = self.web.find_elements(By.TAG_NAME, "a")

        for index, a_ctn in enumerate(a_ctns):
            if a_ctn.text == "Relevés de présence":
                a_ctn.click()
                break

        self.wait_expected_page_is_loaded("presences")
        tools.dprint("Presence page has been opened.", priority_level=3, source="PORTAL")

    '''
    Data storage verification functions
    '''

    def check_if_classes_are_already_stored(self, current_classes) -> bool:
        stored_classes = self.data_storage_manager.get("classes")

        # Trivial cases
        if stored_classes is None or len(stored_classes) != len(current_classes):
            return False

        # Check if classes are the same
        for index in range(len(stored_classes)):
            stored_classe = stored_classes[index]
            current_classe = current_classes[index]

            if stored_classe["name"] != current_classe["name"] or \
                    stored_classe["start"] != current_classe["start"] or \
                    stored_classe["end"] != current_classe["end"]:
                return False

        # No difference found
        return True

    def get_current_classe_index(self) -> int:
        current_classes = self.data_storage_manager.get("classes")
        current_time = tools.get_current_day_timestamp()

        for index in range(len(current_classes)):
            classe = current_classes[index]

            if classe["start"] <= current_time <= classe["end"] or current_time < classe["start"]:
                return index
            else:
                if classe.get("register_opened", False) or not classe.get("notif_sent", False):
                    tools.dprint(
                        f"Classe [{classe['name']}] is passed and "
                        f"register opened [{classe.get('register_opened', False)}],"
                        f" notif sent [{classe.get('notif_sent', False)}].",
                        priority_level=4, source="PORTAL"
                    )

        return -1

    '''
    Classes interaction functions
    '''

    def get_classes(self, add_btn_web_element=False):
        # Get classes ctn (2 cases: with or without classes)
        try:
            classes_ctn = self.web.find_element(By.ID, "body_presences")
            list_of_day_classes = classes_ctn.find_elements(By.TAG_NAME, "tr")
        except:
            list_of_day_classes = []

        classes_info = []
        for classe in list_of_day_classes:
            # Get classe information
            # 0 -> schedule | 1 -> name | 2 -> prof | 3 -> btn | 4 -> ZOOM's link
            info = classe.find_elements(By.TAG_NAME, "td")

            schedule = info[0].text.split(" -")
            start = int(schedule[0].split(":")[0]) * 3600 + int(schedule[0].split(":")[1]) * 60
            end = int(schedule[1].split(":")[0]) * 3600 + int(schedule[1].split(":")[1]) * 60

            classes_info.append({
                "start": start,
                "end": end,
                "name": info[1].text,
                "prof": info[2].text,
                "ZOOM_link": info[4].text,
                "register_opened": False,
                "notif_sent": False
            })

            if add_btn_web_element:
                classes_info[-1]["btn"] = info[3]

        return classes_info

    def is_register_open(self, classe_index) -> bool:
        classe = (self.get_classes(add_btn_web_element=True))[classe_index]

        # Click on the button to see if the register is open
        classe["btn"].find_element(By.TAG_NAME, "a").click()
        is_opened = self.web.find_element(By.ID, "body_presence").text != "L'appel n'est pas encore ouvert."
        self.web.back()

        return is_opened
