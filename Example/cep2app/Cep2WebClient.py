import json
from dataclasses import dataclass
from typing import Any
import requests


@dataclass
class Cep2WebDeviceEvent:
    """ Represents a device event that is sent to the remote web service.
    """
    device_id: str
    device_type: str
    measurement: Any

    def to_json(self) -> str:
        """ Serializes the object to a JSON string.

        Returns:
            str: the event in JSON format
        """
        # The dumps() function serializes an object to a JSON string. In this case, it serializes a
        # dictionary.
        return json.dumps({"deviceId": self.device_id,
                           "deviceType": self.device_type,
                           "measurement": self.measurement})


class Cep2WebClient:
    """ Represents a local web client that sends events to a remote web service.
    """

    def __init__(self, host: str) -> None:
        """ Default initializer.

        Args:
            host (str): an URL with the address of the remote web service
        """
        self.__host = host

    def send_event(self, event: str) -> int:
        """ Sends a new event to the web service.

        Args:
            event (str): a string with the event to be sent.

        Raises:
            ConnectionError: if the connection to the web service fails

        Returns:
            int: the status code of the request
        """
        try:
            # A new event is sent as an HTTP POST request.
            response = requests.post(self.__host, data=event)

            return response.status_code
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Error connecting to {self.__host}")
