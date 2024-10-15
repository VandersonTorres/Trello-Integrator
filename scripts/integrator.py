import logging
import os
import requests

logging.basicConfig(level=logging.INFO)


class TrelloIntegrator:
    base_url: str = "https://api.trello.com/1"

    def __init__(self, apikey: str = "", token: str = "", board_id: str = "") -> None:
        self.logger = logging.getLogger(__name__)
        if not board_id:
            raise NotImplementedError(
                "Missing board_id. You can get it going to your BOARDS"
            )
        self.board_id = board_id
        if not apikey:
            apikey = os.getenv("TRELLO_APIKEY")
        if not token:
            token = os.getenv("TRELLO_TOKEN")
        self.apikey = apikey
        self.token = token
        if not self.apikey or not self.token:
            raise NotImplementedError(
                "Missing credentials: APIKEY and TOKEN. You can get it on 'https://trello.com/power-ups/admin/'"
            )

    def create_new_card(self, title: str, list_id: str, tag_id: str = "", description: str = "", user_name: str = "", user_id: str = "") -> None:
        query = {
            "name": title,
            "idList": list_id,
            "key": self.apikey,
            "token": self.token,
        }
        if description:
            query["desc"] = description
        if user_name:
            query["desc"] = f"{description}\nAssigned to: {user_name}"
        if tag_id:
            query["idLabels"] = tag_id
        if user_id:
            query["idMembers"] = user_id

        response = self.make_request(url=f"{self.base_url}/cards", params=query, method="POST")
        if response:
            self.logger.info(f"Task successfully created. Card title: {title}, Assigned to: {user_name}")
        else:
            self.logger.error("Error while creating card.")

    def move_cards(self, card_id: str, destination_list_id: str) -> None:
        """
        Method that moves a Trello card to another list.

        ARGUMENTS:
            "card_id" = MANDATORY - str(ID of the card to move);
            "destination_list_id" = MANDATORY - str(ID of the target list where the card will be moved);
        """

        query = {
            "idList": destination_list_id,
            "key": self.apikey,
            "token": self.token
        }
        response = self.make_request(url=f"{self.base_url}/cards/{card_id}", params=query, method="PUT")
        if response:
            self.logger.info(f"Card successfully moved to list {destination_list_id}.")
        else:
            self.logger.error(f"Error while moving the card. Error: {response}")

    def get_comments(self, card_id: str) -> dict:
        """
        Method that get comments from a card.

        ARGUMENTS:
            "card_id" = MANDATORY - str(ID of the card to move);
        """

        query = {"key": self.apikey, "token": self.token}
        response = self.make_request(url=f"{self.base_url}/cards/{card_id}/actions", params=query)
        if response:
            records = []
            for item in response:
                if item.get("type") == "commentCard":
                    message_content = item.get("data", {}).get("text", "")
                    user = item.get("memberCreator", {}).get("fullName", "")
                    records.append({"user": user, "message_content": message_content})
            return records

    def get_trello_element(self, element: str, key: str = "", target: str = "") -> list | str:
        """
        Function that get a specific element from Trello, example: "Members", "Tags" or "Lists"

        ARGUMENTS:
            "element" = MANDATORY - str(The data you want to get, like 'members' or 'lists' for example);
            "key" = OPTIONAL - str(The key where the value you want is in. 'name' for example.). If not provided, it'll return all the values;
            "target" = OPTIONAL - str(if provided, it'll return exclusivelly the ID of what you provided) if not, will return the entire list
        """
        if target and not key:
            raise NotImplementedError("If you provide 'Target', you must provide also the 'Key' to be checked.")

        query = {"key": self.apikey, "token": self.token}
        response = self.make_request(url=f"{self.base_url}/boards/{self.board_id}/{element}", params=query)
        if response:
            if target:
                for item in response:
                    if target in item.get(key):
                        return item.get("id")
            else:
                if key:
                    elements_list = [item.get(key) for item in response]
                else:
                    elements_list = response
                return elements_list
        return ""

    def get_tags(self, key: str = "name", target: str = "") -> list | str:
        """Omit "target" to receive all tags, otherwise it'll return the ID of the target"""
        return self.get_trello_element(element="labels", key=key, target=target)

    def get_members(self, key: str = "fullName", target: str = "") -> list | str:
        """Omit "target" to receive all members, otherwise it'll return the ID of the target"""
        return self.get_trello_element(element="members", key=key, target=target)

    def get_lists(self, key: str = "name", target: str = "") -> list | str:
        """Omit "target" to receive all lists, otherwise it'll return the ID of the target"""
        return self.get_trello_element(element="lists", key=key, target=target)

    def archive_card(self, card_id: str) -> None:
        """
        Method to archive a card in Trello.

        ARGUMENTS:
            "card_id" = MANDATORY - str(ID of the card to archive);
        """
        query = {
            "closed": "true",
            "key": self.apikey,
            "token": self.token
        }

        response = self.make_request(url=f"{self.base_url}/cards/{card_id}", params=query, method="PUT")
        if response:
            self.logger.info(f"Card {card_id} successfully archived.")
        else:
            self.logger.error(f"Error while archiving the card {card_id}.")

    def get_cards_from_list(self, list_name: str = "", list_id: str = "") -> dict:
        """
        Method that get all cards from a specific list

        ARGUMENTS:
            "list_id" = OPTIONAL - str(ID of the requested list/column);
            "list_name" = OPTIONAL - str(NAME of the requested list/column);
        """
        if not list_name and not list_id:
            raise NotImplementedError("You must provide the list name or list id you want the cards from.")

        if list_name:
            list_id = self.get_lists(target=list_name)

        query = {"key": self.apikey, "token": self.token}
        response = self.make_request(url=f"{self.base_url}/lists/{list_id}/cards", params=query)
        if response:
            cards = {}
            for item in response:
                cards[item.get("name")] = item.get("id")
            return cards

    def get_card_details(self, card_id: str) -> dict:
        """
        Method that get all information from a card.

        ARGUMENTS:
            "card_id" = MANDATORY - str(ID of the card to move);
        """

        query = {"key": self.apikey, "token": self.token}
        if response := self.make_request(url=f"{self.base_url}/cards/{card_id}/actions", params=query):
            return response

    def make_request(self, url: str, params: dict = {}, method: str = "GET") -> dict:
        if method == "GET":
            response = requests.get(url=url, params=params)
        elif method == "POST":
            response = requests.post(url=url, params=params)
        elif method == "PUT":
            response = requests.put(url=url, params=params)

        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Error while obtaining request for URL: {url}. Status code: {response.status_code}")


# if __name__ == "__main__":
#     integrator = TrelloIntegrator(board_id="eykOmaEf")
