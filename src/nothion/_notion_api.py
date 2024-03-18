import json
from typing import List

import requests


class NotionAPI:
    NOTION_VERSION = "2022-06-28"
    BASE_URL = "https://api.notion.com/v1"
    PAGE_URL = BASE_URL + "/pages"
    DATABASE_URL = BASE_URL + "/databases"
    BLOCK_URL = BASE_URL + "/blocks"

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

            response = requests.post(url=f"{self.DATABASE_URL}/{table_id}/query",
                                     data=json.dumps(query),
                                     headers=self._default_headers())
            response.raise_for_status()

            response_body = response.json()
            all_results += response_body.get("results")
            next_page_id = response_body.get("next_cursor")

            if query.get("page_size") and len(all_results) >= query.get("page_size", 0):
                break

            if next_page_id:
                query["start_cursor"] = next_page_id

        return all_results

    def create_table_entry(self, payload: str) -> dict:
        response = requests.post(url=self.PAGE_URL,
                                 data=payload,
                                 headers=self._default_headers())
        response.raise_for_status()
        return response.json()

    def get_table_entry(self, page_id: str) -> dict:
        response = requests.get(url=f"{self.PAGE_URL}/{page_id}",
                                headers=self._default_headers())
        response.raise_for_status()
        return response.json()

    def update_table_entry(self, page_id: str, payload: str):
        response = requests.patch(url=f"{self.PAGE_URL}/{page_id}",
                                  data=payload,
                                  headers=self._default_headers())
        response.raise_for_status()

    def get_block_children(self, block_id: str) -> dict:
        response = requests.get(url=f"{self.BLOCK_URL}/{block_id}/children?page_size=100",
                                headers=self._default_headers())
        response.raise_for_status()
        return response.json()
