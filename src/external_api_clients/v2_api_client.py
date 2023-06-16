import json
from typing import Dict

from configs.env import V2_BASE_URL, V2_X_API_KEY
from .base_api_client import BaseAPIClient


class V2APIClient(BaseAPIClient):
    BASE_URL = V2_BASE_URL

    HEADERS = {"content-type": "application/json", "x-api-key": V2_X_API_KEY}
    CONVERSATION_DATA_ENDPOINT = "/internal/data/conversations/{conversation_id}"
    THREAD_DATA_ENDPOINT = "/internal/data/conversations/{conversation_id}/{user_id}"
    CREATE_NOTIFICATION_ENDPOINT = "/internal/create_notif"
    COLLABORATORS_EMAILS_ENDPOINT = "/internal/collaborators/get-email"
    COLLABORATORS_REGISTER_ENDPOINT = "/internal/collaborators"
    USERS_ENDPOINT = "/internal/users"
    CREATE_VIEW_ENDPOINT = "/internal/sm-views/{user_id}/{sm_id}"
    FAVOURITE_VIEW_ENDPOINT = "/internal/sm-views/favs/{sm_id}/{view_id}"

    def get_sm_users_data(self, params):
        return self.make_request("GET", self.USERS_ENDPOINT, self.HEADERS, params)

    def get_collaborators_emails(self, params):
        return self.make_request("GET", self.COLLABORATORS_EMAILS_ENDPOINT, self.HEADERS, params)

    def get_conversation_data(self, conversation_id: int) -> Dict:
        url = self.CONVERSATION_DATA_ENDPOINT.format(conversation_id=conversation_id)
        return self.make_request("GET", url, self.HEADERS)

    def get_thread_data(self, conversation_id: int, user_id: int) -> Dict:
        url = self.THREAD_DATA_ENDPOINT.format(conversation_id=conversation_id, user_id=user_id)
        return self.make_request("GET", url, self.HEADERS)

    def create_notification(self, payload: Dict) -> Dict:
        return self.make_request("POST", self.CREATE_NOTIFICATION_ENDPOINT, self.HEADERS, data = json.dumps(payload))

    def register_collaborator(self, email_id, usergroupid, invited_by):
        payload = {
            "email_id": email_id,
            "usergroupid": usergroupid,
            "invited_by": invited_by
        }

        return self.make_request("POST", self.COLLABORATORS_REGISTER_ENDPOINT, self.HEADERS, data=json.dumps(payload))

    def create_view(self, *, user_id: int, sm_id: int, payload: Dict) -> Dict:
        url = self.CREATE_VIEW_ENDPOINT.format(user_id=user_id, sm_id=sm_id)
        return self.make_request("POST", url, self.HEADERS, data=json.dumps(payload))

    def favourite_view(self, *, sm_id: int, view_id: int) -> Dict:
        url = self.FAVOURITE_VIEW_ENDPOINT.format(sm_id=sm_id, view_id=view_id)
        return self.make_request("PUT", url, self.HEADERS)
