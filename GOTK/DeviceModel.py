from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class ZigbeeDevice:
    """ This class represents a Zigbee device. It has an ID and a type, both are strings which the 
    user can assign at its will. The id_ can be the device address or friendly name, and the type_ can be customized by the user.
    
    """

    id_: str
    type_: str

class DeviceModel:
    """ The DeviceModel Class is responsible for representing and managing acces to data.
    Its a dictionary that uses the devices's ID as key, to reference to a specific device object.
    
    """

    #initializes dictionary for devices
    def __init__(self):
        self.__devices = {}

    #returns list with all devices
    @property
    def devices_list(self) -> List[ZigbeeDevice]:
        return list(self.__devices.values())

    #returns list with the actuators (Lights and powerplug actuator)
    @property
    def actuators_list(self) -> List[ZigbeeDevice]:
        return list(filter(lambda s: s.type_ in {"power plug"},
                            self.__devices.values()))
    
    #returns list with the sensors
    @property
    def sensors_list (self) -> List[ZigbeeDevice]:
        return list(filter(lambda s: s.type_ in {"pir"},
                            self.__devices.values()))
    
    #lights "led" - removed from actuator list and put in this light list, if remove change this
    @property
    def lights_list(self) -> List[ZigbeeDevice]:
        return list(filter(lambda s: s.type_ in {"light"},
                            self.__devices.values()))
    
    
    #adds a new device
    def add(self, device: Union[ZigbeeDevice, List[ZigbeeDevice]]) -> None:
        """ Add new device
        Args:
            device (Union[ZigbeeDevice, List[ZigbeeDevice]]): a device object, or a list of
            device objects to store.
        """ 
        # If the value given as argument is a ZigbeeDevice, then create a list with it so that
        # later only a list of objects has to be inserted.
        list_devices = [device] if isinstance(device, ZigbeeDevice)\
            else device

        # Insert list of devices, where the device ID is the key of the dictionary.
        for s in list_devices:
            self.__devices[s.id_] = s

    def find(self, device_id: str) -> Optional[ZigbeeDevice]:
        """ Retrieve device from database by ID
        Args:
            device_id(str): ID of the devices to be retrived.

        Returns:
            Optional[ZigbeeDevice]: a device is returned. If the device is not stored, None is returned

        """
        # Use the bult-in function filter to get the device. The output of filter is a filter object
        # that is then casted to a list. The, the first result, if any, is returned; otherwise None.
        # Instead of None, am exception can also be raised.
        devices = list(filter(lambda d: d[0] == device_id,
                                self.__devices.items()))

        return devices[0][1] if len(devices) >= 1 else None