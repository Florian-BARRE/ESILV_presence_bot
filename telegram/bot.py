import requests

class Bot:
    def __init__(self, token, chatID):
        self.token = token
        self.chatID = chatID

    def __get_url(self):
        return f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_text(self, msg):
        response = requests.post(
            self.__get_url(),
            json={'chat_id': self.chatID, 'text': msg}
        )
        print("A Telegram notification has just been sent !")
        print(f"Response: {response}")

        return response.json()
