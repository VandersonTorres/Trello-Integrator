import os
import requests


class TrelloIntegrator:
    base_url: str = "https://api.trello.com/1/cards"

    def __init__(self, trello_apikey: str = "", trello_token: str = "") -> None:
        if not trello_apikey:
            trello_apikey = os.getenv("TRELLO_APIKEY")
        if not trello_token:
            trello_token = os.getenv("TRELLO_TOKEN")
        self.trello_apikey = trello_apikey
        self.trello_token = trello_token
        if not self.trello_apikey or not self.trello_token:
            raise NotImplementedError(
                "Missing credentials: APIKEY and TOKEN. You can get it on 'https://trello.com/power-ups/admin/'"
            )

    def create_trello_card(
        self, title: str, description: str, user_name: str, user_id: str, list_id: str, tag_id: str
    ) -> dict | None:
        query = {
            "name": title,
            "desc": f"{description}\nAssigned to: {user_name}",
            "idList": list_id,
            "idLabels": tag_id,
            "idMembers": user_id,
            "key": self.trello_apikey,
            "token": self.trello_token,
        }
        response = requests.post(self.base_url, params=query)
        if response.status_code == 200:
            print(f"Task successfully created. Card title: {title}, Assigned to: {user_name}")
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

        query = {
            "idList": target_list_id,
            "key": self.trello_apikey,
            "token": self.trello_token
        }
        response = requests.put(f"{self.base_url}/{card_id}", params=query)
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

        query = {"key": self.trello_apikey, "token": self.trello_token}
        response = requests.get(f"{self.base_url}/{card_id}/actions", params=query)
        if response.status_code == 200:
            res_json = response.json()
            records = []
            for item in res_json:
                if item.get("type") == "commentCard":
                    message_content = item.get("data", {}).get("text", "")
                    user = item.get("memberCreator", {}).get("fullName", "")
                    records.append({"user": user, "message_content": message_content})
            return records


class TrelloElementsHandler(TrelloIntegrator):
    base_url: str = "https://api.trello.com/1"

    def get_trello_element(self, board_id: str, element: str, key: str = "", target: str = "") -> list | str:
        """
        Function that get a specific element from Trello, example: "Members", "Tags" or "Lists"

        ARGUMENTS:
            "board_id" = MANDATORY - str(ID of the main board in the workspace);
            "element" = MANDATORY - str(The data you want to get, like 'members' or 'lists' for example);
            "key" = OPTIONAL - str(The key where the value you want is in. 'name' for example.). If not provided, it'll return all the values;
            "target" = OPTIONAL - str(if provided, it'll return exclusivelly the ID of what you provided) if not, will return the entire list
        """
        if target and not key:
            raise NotImplementedError("If you provided 'Target', you must provide also the 'Key' to be checked.")

        query = {"key": self.trello_apikey, "token": self.trello_token}
        response = requests.get(f"{self.base_url}/boards/{board_id}/{element}", params=query)
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

    def get_cards_from_list(self, list_id: str) -> dict:
        """
        Method that get all cards from a specific list

        ARGUMENTS:
            "list_id" = MANDATORY - str(ID of the requested list/column);
        """
        query = {"key": self.trello_apikey, "token": self.trello_token}
        response = requests.get(f"{self.base_url}/lists/{list_id}/cards", params=query)
        if response.status_code == 200:
            res_json = response.json()
            cards = {}
            for item in res_json:
                cards[item.get("name")] = item.get("id")
            return cards

    def get_trello_members(self, board_id: str, key: str = "fullName", target: str = ""):
        """Omit "target" to receive all members"""
        return self.get_trello_element(board_id=board_id, element="members", key=key, target=target)

    def get_trello_lists(self, board_id: str, key: str = "name", target: str = ""):
        """Omit "target" to receive all lists"""
        return self.get_trello_element(board_id=board_id, element="lists", key=key, target=target)

    def get_trello_tags(self, board_id: str, key: str = "name", target: str = ""):
        """Omit "target" to receive all tags"""
        return self.get_trello_element(board_id=board_id, element="labels", key=key, target=target)


if __name__ == "__main__":
    board_id = "eykOmaEf"       # BOARD: "SCRAPERS"
    list_name = "Backlog"       # Available: Backlog, In Progress, Review, Approved, Merged, Done
    tag_name = "LOW PRIORITY"   # Available: TRAINING, LOW PRIORITY, HIGH PRIORITY, SIDE PROJECTS (Personal)
    user_name = "Vanderson"     # Available: Vanderson, renato
    title = "<ADD THE TITLE HERE>"
    description = "<ADD THE DESCRIPTION HERE>"

    elements_handler = TrelloElementsHandler()
    user_id = elements_handler.get_trello_members(board_id=board_id, key="fullName", target=user_name)
    list_id = elements_handler.get_trello_lists(board_id=board_id, key="name", target=list_name)
    tag_id = elements_handler.get_trello_tags(board_id=board_id, key="name", target=tag_name)

    integrator = TrelloIntegrator()
    integrator.create_trello_card(
        title=title,
        description=description,
        user_name=user_name,
        user_id=user_id,
        list_id=list_id,
        tag_id=tag_id,
    )
