import json
from typing import Dict

from configs.env import LABEL_MANAGER_BASE_URL
from external_api_clients.base_api_client import BaseAPIClient


class LabelManagerAPIClient(BaseAPIClient):
    BASE_URL = LABEL_MANAGER_BASE_URL

    HEADERS = {"content-type": "application/json"}

    CREATE_LABEL_ENDPOINT = "/api/label-manager/service-label"

    def create_labels(self, *, sm_id: int, payload: Dict) -> Dict:
        return self.make_request("POST", self.CREATE_LABEL_ENDPOINT, self.HEADERS, data=json.dumps(payload))
