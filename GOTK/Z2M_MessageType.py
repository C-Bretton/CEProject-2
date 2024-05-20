from enum import Enum

class Z2M_MessageType(Enum):
    """
        Defines message types, and the different types of messages we can have.
    """
    
    BRIDGE_EVENT = "bridge_event"
    BRIDGE_INFO = "bridge_info"
    BRIDGE_LOG = "bridge_log"
    BRIDGE_STATE = "bridge_state"
    DEVICE_ANNOUNCE = "device_announce"
    DEVICE_ANNOUNCED = "device_announced"
    DEVICE_CONNECTED = "device_connected"
    DEVICE_EVENT = "device_event"
    DEVICE_INTERVIEW = "device_interview"
    DEVICE_JOINED = "device_joined"
    DEVICE_LEAVE = "device_leave"
    DEVICE_PAIRING = "pairing"
    UNKNOWN = None