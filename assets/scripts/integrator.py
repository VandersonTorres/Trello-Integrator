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
        tag_id: str,
        list_id: str
    ) -> None:
        self.user_name = user_name
        self.user_id = user_id
        self.title = title
        self.description = description
        self.tag_id = tag_id
        self.list_id = list_id

    def create_trello_card(self) -> dict | None:
        url = "https://api.trello.com/1/cards"
        query = {
            "name": self.title,
            "desc": f"{self.description}\nAssigned to: {self.user_name}",
            "idList": self.list_id,
            "idLabels": self.tag_id,
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

    def move_trello_card(self, card_id: str, target_list_id: str) -> dict | None:
        """
        Method that moves a Trello card to another list.

        ARGUMENTS:
            "card_id" = MANDATORY - str(ID of the card to move);
            "target_list_id" = MANDATORY - str(ID of the target list where the card will be moved);
        """

        url = f"https://api.trello.com/1/cards/{card_id}"
        query = {
            "idList": target_list_id,
            "key": TRELLO_APIKEY,
            "token": TRELLO_TOKEN
        }
        response = requests.put(url, params=query)
        if response.status_code == 200:
            print(f"Card successfully moved to list {target_list_id}.")
            return response.json()
        else:
            print(f"Error while moving the card. Status code: {response.status_code}. Error: {response.text}")
            return

    def see_comments_on_card(self, card_id: str) -> None:
        """
        Method that get comments from a card.

        ARGUMENTS:
            "card_id" = MANDATORY - str(ID of the card to move);
        """

        url = f"https://api.trello.com/1/cards/{card_id}/actions"
        query = {"key": TRELLO_APIKEY, "token": TRELLO_TOKEN}
        response = requests.get(url, params=query)
        if response.status_code == 200:
            res_json = response.json()
            records = []
            for item in res_json:
                if item.get("type") == "commentCard":
                    message_content = item.get("data", {}).get("text", "")
                    user = item.get("memberCreator", {}).get("fullName", "")
                    records.append({"user": user, "message_content": message_content})
            return records


def get_trello_element(board_id: str, element: str, key: str = "", target: str = "") -> list | str:
    """
    Function that get a specific element from Trello, exemple: "Members", "Tags" or "Lists"

    ARGUMENTS:
        "board_id" = MANDATORY - str(ID of the main board in the workspace);
        "element" = MANDATORY - str(The data you want to get, like 'members' or 'lists' for example);
        "key" = OPTIONAL - str(The key where the value you want is in. 'name' for example.). If not provided, it'll return all the values;
        "target" = OPTIONAL - str(if provided, it'll return exclusivelly the ID of what you provided) if not, will return the entire list
    """

    url = f"https://api.trello.com/1/boards/{board_id}/{element}"
    query = {"key": TRELLO_APIKEY, "token": TRELLO_TOKEN}
    response = requests.get(url, params=query)
    if response.status_code == 200:
        res_json = response.json()
        if target:
            for item in res_json:
                if target in item.get(key):
                    return item.get("id")
        else:
            if key:
                elements_list = [item.get(key) for item in res_json]
            else:
                elements_list = res_json
            return elements_list
    return ""


def get_cards_from_list(list_id: str) -> dict:
    """
    Function that get all cards from a specific list

    ARGUMENTS:
        "list_id" = MANDATORY - str(ID of the requested list/column);
    """
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    query = {"key": TRELLO_APIKEY, "token": TRELLO_TOKEN}
    response = requests.get(url, params=query)
    if response.status_code == 200:
        res_json = response.json()
        cards = {}
        for item in res_json:
            cards[item.get("name")] = item.get("id")
        return cards


if __name__ == "__main__":
    board_id = "eykOmaEf"  # BOARD: "SCRAPERS"
    list_name = "Backlog"
    tag_name = "LOW PRIORITY"
    user_name = "Vanderson"
    title = "CARD ADDED BY BOT INTEGRATOR"
    description = "TEST CARD DESCRIPTION"

    user_id = get_trello_element(board_id=board_id, element="members", key="fullName", target=user_name)
    tag_id = get_trello_element(board_id=board_id, element="labels", key="name", target=tag_name)
    list_id = get_trello_element(board_id=board_id, element="lists", key="name", target=list_name)

    integrator = TrelloIntegrator(
        user_name=user_name,
        user_id=user_id,
        title=title,
        description=description,
        tag_id=tag_id,
        list_id=list_id,
    )
    # integrator.create_trello_card()

"""
EXAMPLES

1. Getting all possible "tags":
    tags = get_trello_element(board_id=board_id, element="labels", key="name")
2. Getting all possible "members":
    users = get_trello_element(board_id=board_id, element="members", key="fullName")
3. Getting all possible "lists" (columns):
    lists = get_trello_element(board_id=board_id, element="lists", key="name")
4. Getting all possible "cards" from a list/column:
    cards = get_cards_from_list(list_id=list_id)
5. Moving cards from a list to another:
    integrator.move_trello_card(card_id=card_id, target_list_id=target_list_id)
6. Seeing comments on a card:
    integrator.see_comments_on_card(card_id=card_id)

PS: If you want to get all the information, just ommit the argument "key"
"""
