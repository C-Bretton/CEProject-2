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
            Initializes the message object. It assigns the message topic, timestamp and type_. Depending on the message topic,
            specific variables will be assigned values. 
        """
        
        self.topic = topic
        self.timeStamp = time.time()
        self.type_: Z2M_MessageType
        
        #When topic is bridge/state, the state is assigned to the message
        if topic == "zigbee2mqtt/bridge/state":
            self.type_= Z2M_MessageType.BRIDGE_STATE 
            self.state = message
        
        #Topics bridge/event and bridge/logging, assigns variables data, message, and meta
        elif topic in ["zigbee2mqtt/bridge/event", "zigbee2mqtt/bridge/logging"]:
            self.type_ = {"zigbee2mqtt/bridge/event": Z2M_MessageType.BRIDGE_EVENT,
                        "zigbee2mqtt/bridge/logging": Z2M_MessageType.BRIDGE_LOG}.get(topic)
            
            message_json = json.loads(message)
            self.data = message_json.get("data")
            self.message = message_json.get("message")
            self.meta = message_json.get("meta")

        #These topics there is not any additional variables assigned
        elif topic in ["zigbee2mqtt/bridge/config",
                       "zigbee2mqtt/bridge/info",
                       "zigbee2mqtt/bridge/devices",
                       "zigbee2mqtt/bridge/groups",
                       "zigbee2mqtt/bridge/request/health_check",
                       "zigbee2mqtt/bridge/response/health_check"]:
            pass

        #For sensor messages the occupancy variable is assigned.
        elif "Sensor" in topic:
            message_json = json.loads(message)        
            self.source = f"Sensor {topic[19]}"
            
            self.occupancy = message_json.get("occupancy")

        #For the Actuator messages the power and state variables are assigned.
        elif "Actuator" in topic:
            message_json = json.loads(message)
            self.source = "Actuator"
            self.power = message_json.get("power")
            self.state = message_json.get("state")



