from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class Cep2ZigbeeDevice:
    """ This class represents a Zigbee device. It has an ID and type, both strings that the user can
    assign at its will. Since this is used as a companion class of the zigbee2mqtt client, the id_
    can be the device address (or friendly name) and the type_ can be user custom.
    """

    # A note on the name of these class attributes: id and type are names of Python built-in
    # functions. If an attribute called id is declared by the user, this will hide the built-in
    # id() function. This might break code that uses id() or type(), therefore it is advisable to
    # avoid these keywords for naming variables and functions. Thus the name id_ and type_ are used.
    # For more information check:
    # https://stackoverflow.com/questions/77552/id-is-a-bad-variable-name-in-python

    id_: str
    type_: str


class Cep2Model:
    """ The model class is responsible for representing and managing access to data. In this case,
    the class is a basic dictionary that uses the devices's ID as key to reference the device
    object. This is a very simplistic database and more evolved approaches can be used. For example,
    this class might abstract the access to a database such as MySQL.
    """

    def __init__(self):
        self.__devices = {}

    @property
    def actuators_list(self) -> List[Cep2ZigbeeDevice]:
        return list(filter(lambda s: s.type_ in {"led", "power plug"},
                           self.__devices.values()))

    @property
    def devices_list(self) -> List[Cep2ZigbeeDevice]:
        return list(self.__devices.values())

    @property
    def sensors_list(self) -> List[Cep2ZigbeeDevice]:
        return list(filter(lambda s: s.type_ in {"pir"},
                           self.__devices.values()))

    def add(self, device: Union[Cep2ZigbeeDevice, List[Cep2ZigbeeDevice]]) -> None:
        """ Add a new devices to the database.

        Args:
            device (Union[Cep2ZigbeeDevice, List[Cep2ZigbeeDevice]]): a device object, or a list of
            device objects to store.
        """
        # If the value given as argument is a Cep2ZigbeeDevice, then create a list with it so that
        # later only a list of objects has to be inserted.
        list_devices = [device] if isinstance(device, Cep2ZigbeeDevice)\
            else device

        # Insert list of devices, where the device ID is the key of the dictionary.
        for s in list_devices:
            self.__devices[s.id_] = s

    def find(self, device_id: str) -> Optional[Cep2ZigbeeDevice]:
        """ Retrieve a device from the database by its ID.

        Args:
            device_id (str): ID of the device to retrieve.

        Returns:
            Optional[Cep2ZigbeeDevice]: a device. If the device is not stored, then None is returned
        """
        # Use the bult-in function filter to get the device. The output of filter is a filter object
        # that is then casted to a list. The, the first result, if any, is returned; otherwise None.
        # Instead of None, am exception can also be raised.
        devices = list(filter(lambda kv: kv[0] == device_id,
                              self.__devices.items()))

        return devices[0][1] if len(devices) >= 1 else None