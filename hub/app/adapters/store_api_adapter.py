import json
import logging
from typing import List

import pydantic_core
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
        try:
            # Перетворюємо об'єкти в JSON-сумісний формат
            payload = [data.model_dump(mode="json") for data in processed_agent_data_batch]

            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{self.api_base_url}/processed_agent_data/", json=payload, headers=headers)

            response.raise_for_status()
            logging.info("Data successfully saved.")
            return True

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to save data: {e}")
            return False

        except Exception as e:
            logging.error(f"Error occurred while saving data: {e}")
            return False
