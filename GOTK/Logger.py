# url = "http://127.0.0.1/writeToDB/"
import requests
import json
import time
from heucod import HeucodEventType, HeucodEvent, HeucodEventJsonEncoder

class Logger:
    def __init__(self, ServerHost : str):
        """
            url: the url should be the endpoint, which the post request should be made to.
            
            The endpoint of our webserver should be: "http://<addrOfServerHost>/writeToDB/".

            The last "/" is very important, since it tells the request that it is looking for a directory and not a file.
        """
        self.url = f"http://{ServerHost}/writeToDB/"

    def send_log(self, timeStamp: int, eventType: HeucodEventType):
        """
            Creates a log of an event.

            timeStamp: Given as an integer of seconds since 1. january 1930 00:00:00. (time.time())

            eventType: A string describing the event type.

            Event types could be: 
            "..." to be continued...
        """

        data : HeucodEvent = HeucodEvent()

        data.event_type = eventType

        data.timestamp = timeStamp
        
        #! Tilføj evt patient_id 
        try:
            # Creates a post request for the HTTP-server.
            # Redirects are not allowed, since this causes the post request to be turnt into a get request.
            jsonData = json.loads(data.to_json()) #! The to_json() function creates a str containing a json, we just want the dictionary of the json. Thus we use json.loads()
            response = requests.post(self.url, json=jsonData, allow_redirects=False)
        except Exception as error:
            # If something goes wrong, mainly no connection, raise the error.
            raise error

    #!This is test logger, when server is not running.
    # def send_log(self, timeStamp: int, eventType: HeucodEventType): 
    #     print("\n -------------- this is test server host!!!! ---------------- \n\n ", self.url,"\n Type is:", type(self.url), "\n\n")
    #     print("has logged")

    def logStoveOn(self):
        self.send_log(timeStamp = int(time.time()), eventType=HeucodEventType.StoveTurnsOn)
            
    def logStoveOff(self):
        self.send_log(timeStamp = int(time.time()), eventType = HeucodEventType.StoveTurnsOff)

    def logSystemTurnsStoveOn(self):
        self.send_log(timeStamp = int(time.time()), eventType=HeucodEventType.SystemTurnsStoveOn)
        
    def logSystemTurnsStoveOff(self):
        self.send_log(timeStamp = int(time.time()), eventType=HeucodEventType.SystemTurnsStoveOff)

    def logCitizenLeftKitchen(self):
        self.send_log(timeStamp = int(time.time()), eventType=HeucodEventType.CitizenLeftKitchen)

    def logCitizenEnteredKitchen(self):
        self.send_log(timeStamp = int(time.time()), eventType=HeucodEventType.CitizenEnteredKitchen)
        
