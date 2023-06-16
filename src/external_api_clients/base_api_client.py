import http

import requests
from fastapi import status
from exceptions.errors import ExternalApiServiceError
from utils.initialize_common_utils import common_utils_ins


class BaseAPIClient(object):
    BASE_URL = ''  # overriden in child classes

    def __init__(self):
        self.__log = common_utils_ins.logger

    def make_request(self, method, endpoint, headers, params=None, data=None):
        url = self.BASE_URL + endpoint

        self.__log.info(f"Calling {url} with headers : {headers} and params : {params} and data : {data}")

        response = requests.request(method, url, params=params, headers=headers, data=data)
        if response.status_code >= status.HTTP_400_BAD_REQUEST:
            self.__log.error(f"Error {response.status_code} from {url} : {response.content}")
            raise ExternalApiServiceError("External API service error", http.HTTPStatus.FAILED_DEPENDENCY)
        return response.json()
