import os
import requests

TRELLO_APIKEY = os.getenv("TRELLO_APIKEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")


class TrelloIntegrator:
    def __init__(
        self,
        user_name: str,
        user_id: str,
        title: str,
        description: str,
        label_id: str,
        list_id: str
    ) -> None:
        self.user_name = user_name
        self.user_id = user_id
        self.title = title
        self.description = description
        self.label_id = label_id
        self.list_id = list_id

    def create_trello_card(self) -> dict | None:
        url = "https://api.trello.com/1/cards"
        query = {
            "name": self.title,
            "desc": f"{self.description}\nAssigned to: {self.user_name}",
            "idList": self.list_id,
            "idLabels": self.label_id,
            "idMembers": self.user_id,
            "key": TRELLO_APIKEY,
            "token": TRELLO_TOKEN,
        }
        response = requests.post(url, params=query)
        if response.status_code == 200:
            print("Task sccessfully created.")
            return response.json()
        else:
            print("Error while creating card.")
            return


def get_trello_element_id(board_id: str, element: str, key: str, target: str) -> str:
    url = f"https://api.trello.com/1/boards/{board_id}/{element}"
    query = {"key": TRELLO_APIKEY, "token": TRELLO_TOKEN}
    response = requests.get(url, params=query)
    if response.status_code == 200:
        res_json = response.json()
        for item in res_json:
            if target in item.get(key):
                return item.get("id")
    return ""


if __name__ == "__main__":
    board_id = "eykOmaEf"  # BOARD: "SCRAPERS"
    list_name = "Backlog"
    label_name = "LOW PRIORITY"
    user_name = "Vanderson"
    title = "CARD ADDED BY BOT INTEGRATOR"
    description = "TEST CARD DESCRIPTION"
    user_id = get_trello_element_id(board_id=board_id, element="members", key="fullName", target=user_name)
    label_id = get_trello_element_id(board_id=board_id, element="labels", key="name", target=label_name)
    list_id = get_trello_element_id(board_id=board_id, element="lists", key="name", target=list_name)

    integrator = TrelloIntegrator(
        user_name=user_name,
        user_id=user_id,
        title=title,
        description=description,
        label_id=label_id,
        list_id=list_id,
    )
    integrator.create_trello_card()
