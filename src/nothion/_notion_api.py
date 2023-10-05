import json
from typing import List

import requests


class NotionAPI:
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def __init__(self, auth_secret: str):
        self._auth_secret = auth_secret

    def _default_headers(self) -> dict:
        """Returns the headers required for the Notion API requests."""
        return {
            "content-type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
            "Authorization": f"Bearer {self._auth_secret}"
        }

    def query_table(self, table_id: str, query: dict) -> List[dict]:
        next_page_id = None
        first_request = True
        all_results = []

        while next_page_id or first_request:
            first_request = False

            response = requests.post(url=self.BASE_URL + "/databases/" + table_id + "/query",
                                     data=json.dumps(query),
                                     headers=self._default_headers())
            response.raise_for_status()

            all_results += response.json().get("results")
            next_page_id = response.json().get("next_cursor")

            if next_page_id:
                query["start_cursor"] = next_page_id

        return all_results

    def create_table_entry(self, payload: str) -> dict:
        response = requests.post(url=self.BASE_URL + "/pages",
                                 data=payload,
                                 headers=self._default_headers())
        response.raise_for_status()
        return response.json()

    def get_table_entry(self, page_id: str) -> dict:
        response = requests.get(url=self.BASE_URL + "/pages/" + page_id,
                                headers=self._default_headers())
        response.raise_for_status()
        return response.json()

    def update_table_entry(self, page_id: str, payload: str):
        response = requests.patch(url=self.BASE_URL + "/pages/" + page_id,
                                  data=payload,
                                  headers=self._default_headers())
        response.raise_for_status()
