import time
import json
from typing import Any, Callable, List, Optional

from Z2M_MessageType import Z2M_MessageType


class Z2M_Message:
    """
    Message object
    """
    def __init__(self, topic, message : str):
        """
        Takes a raw message from
        """
        self.topic = topic
        self.timeStamp = time.time()
        self.type_: Z2M_MessageType

        #filter for the different message types

        if topic == "zigbee2mqtt/bridge/state":
            self.type_= Z2M_MessageType.BRIDGE_STATE 
            self.state = message
        
        elif topic in ["zigbee2mqtt/bridge/event", "zigbee2mqtt/bridge/logging"]:
            self.type_ = {"zigbee2mqtt/bridge/event": Z2M_MessageType.BRIDGE_EVENT,
                        "zigbee2mqtt/bridge/logging": Z2M_MessageType.BRIDGE_LOG}.get(topic)
            
            # print("\nWhat is this message: \n", message, "\nThe topic is: ", self.topic ,"\nType is: ", self.type_)
            # print("\nThe topic is: ", self.topic) #! this is just logging or event message
            message_json = json.loads(message)
            self.data = message_json.get("data")
            self.message = message_json.get("message")
            self.meta = message_json.get("meta")

        elif topic in ["zigbee2mqtt/bridge/config",
                       "zigbee2mqtt/bridge/info",
                       "zigbee2mqtt/bridge/devices",
                       "zigbee2mqtt/bridge/groups",
                       "zigbee2mqtt/bridge/request/health_check",
                       "zigbee2mqtt/bridge/response/health_check"]:
            pass
            #return none?

        elif "Sensor" in topic:
            # print("\nThis is topic: Sensor", topic)
            message_json = json.loads(message)        
            self.source = f"Sensor {topic[19]}"
            
            self.occupancy = message_json.get("occupancy")

        elif "Actuator" in topic:
            # print("\nThis is topic: Actuator")
            message_json = json.loads(message)
            self.source = "Actuator"
            self.power = message_json.get("power")
            self.state = message_json.get("state")
            # print("This is power: ", self.power)

        elif "LED" in topic or "Bulb" in topic:
            # print("\nThis is topic: ", topic)
            message_json = json.loads(message)
            self.source = "Light"
            self.brightness = message_json.get("brightness")
            self.effect = message_json.get("effect")
            # print("This is brightness: ", self.brightness)

        
        
        
        
    # cls gives the class
    #def parse(cls, topic, message) -> Z2M_Message:
    #    payload = json.loads(message.payload.decode('utf-8'))
