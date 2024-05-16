from __future__ import annotations
import json
import re
from copy import deepcopy
from dataclasses import dataclass, replace as dataclass_replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Union
from uuid import UUID


class HeucodEventType(Enum):
    def __new__(cls, type_: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = type_
        obj.description = description

        return obj

    def __int__(self):
        return self.value

    def __repr__(self) -> str:
        return self.description

    def __str__(self) -> str:
        return self.description

    BasicEvent = (81325, "OpenCare.EVODAY.BasicEvent") #!

    EDL = (80542, "OpenCare.EVODAY.EDL.EDL")
    BedOccupancyEvent = (82043, "OpenCare.EVODAY.EDL.BedOccupancyEvent")
    BathroomOccupancyEvent = (82604, "OpenCare.EVODAY.EDL.BathroomOccupancyEvent")
    ToiletOccupancy = (81887, "OpenCare.EVODAY.EDL.ToiletOccupancy")
    ChairOccupancyEvent = (82263, "OpenCare.EVODAY.EDL.ChairOccupancyEvent")
    ToothBrushingSession = (82429, "OpenCare.EVODAY.EDL.ToothBrushingSession")
    RoomMovementEvent = (82099, "OpenCare.EVODAY.EDL.RoomMovementEvent") #! 
    CouchOccupancyEvent = (82274, "OpenCare.EVODAY.EDL.CouchOccupancyEvent")
    HandWashingEvent = (81943, "OpenCare.EVODAY.EDL.HandWashingEvent")
    SoapDispensnig = (81776, "OpenCare.EVODAY.EDL.SoapDispensnig")
    TelevisionUseEvent = (82202, "OpenCare.EVODAY.EDL.TelevisionUseEvent")
    ApplianceUseEvent = (82053, "OpenCare.EVODAY.EDL.ApplianceUseEvent")
    FallDetectedEvent = (82028, "OpenCare.EVODAY.EDL.FallDetectedEvent")
    WalkingDetected = (81848, "OpenCare.EVODAY.EDL.WalkingDetected")
    EnterHomeEvent = (81746, "OpenCare.EVODAY.EDL.EnterHomeEvent")
    LeaveHomeEvent = (81729, "OpenCare.EVODAY.EDL.LeaveHomeEvent")
    LighingtChangedEvent = (82347, "OpenCare.EVODAY.EDL.LighingtChangedEvent") #!
    LighingtSettingChangedEvent = (83081, "OpenCare.EVODAY.EDL.LighingtSettingChangedEvent") 
    UserIsHomeEvent = (81839, "OpenCare.EVODAY.EDL.UserIsHomeEvent")

    ADL = (80538, "OpenCare.EVODAY.ADL.ADL")
    Sleeping = (81152, "OpenCare.EVODAY.ADL.Sleeping")
    Resting = (81061, "OpenCare.EVODAY.ADL.Resting")
    Toileting = (81272, "OpenCare.EVODAY.ADL.Toileting")
    Bathing = (81030, "OpenCare.EVODAY.ADL.Bathing")
    Hygiene = (81042, "OpenCare.EVODAY.ADL.Hygiene")
    GroomingHair = (81551, "OpenCare.EVODAY.ADL.GroomingHair")
    Brushing = (81163, "OpenCare.EVODAY.ADL.Brushing")
    Eating = (80929, "OpenCare.EVODAY.ADL.Eating")
    Dressing = (81160, "OpenCare.EVODAY.ADL.Dressing")
    Transferring = (81598, "OpenCare.EVODAY.ADL.Transferring")
    Socializing = (81477, "OpenCare.EVODAY.ADL.Socializing")
    WatchingTV = (81320, "OpenCare.EVODAY.ADL.WatchingTV")
    Exericising = (81475, "OpenCare.EVODAY.ADL.Exericising")

    IADL = (80611, "OpenCare.EVODAY.IADL.IADL")
    Shopping = (81169, "OpenCare.EVODAY.IADL.Shopping")
    Housekeeping = (81584, "OpenCare.EVODAY.IADL.Housekeeping")
    ManagingMoney = (81651, "OpenCare.EVODAY.IADL.ManagingMoney")
    FoodPreparation = (81878, "OpenCare.EVODAY.IADL.FoodPreparation")
    Telephone = (81261, "OpenCare.EVODAY.IADL.Telephone")
    Transportation = (81841, "OpenCare.EVODAY.IADL.Transportation")

    AE = (80463, "OpenCare.EVODAY.AE.AE")
    FallDetected = (81514, "OpenCare.EVODAY.AE.FallDetected")
    BathroomFall = (81540, "OpenCare.EVODAY.AE.BathroomFall")
    LowGeneralActivityLevel = (82686, "OpenCare.EVODAY.AE.LowGeneralActivityLevel")
    LowHydrationLevel = (82085, "OpenCare.EVODAY.AE.LowHydrationLevel")
    SparseToiletUse = (81877, "OpenCare.EVODAY.AE.SparseToiletUse")
    FrequentToiletUse = (82097, "OpenCare.EVODAY.AE.FrequentToiletUse")
    MissedToothbrushing = (82334, "OpenCare.EVODAY.AE.MissedToothbrushing")
    MissedMedication = (81963, "OpenCare.EVODAY.AE.MissedMedication")
    MissedHygiene = (81655, "OpenCare.EVODAY.AE.MissedHygiene")

    TechnicalEvent = (81750, "OpenCare.EVODAY.TechnicalEvent.TechnicalEvent")
    HeartBeat = (81209, "OpenCare.EVODAY.TechnicalEvent.HeartBeat")
    BatteryPowerLOW = (81827, "OpenCare.EVODAY.TechnicalEvent.BatteryPowerLOW")
    DeviceNeedsMaintenance = (82539, "OpenCare.EVODAY.TechnicalEvent.DeviceNeedsMaintenance")

    DeviceUsageEvent = (81936, "OpenCare.EVODAY.DeviceUsageEvent.DeviceUsageEvent")
    AppliancenDeviceUsage = (82441, "OpenCare.EVODAY.DeviceUsageEvent.AppliancenDeviceUsage")
    TVUsage = (81000, "OpenCare.EVODAY.DeviceUsageEvent.TVUsage")
    RadioUsage = (81325, "OpenCare.EVODAY.DeviceUsageEvent.RadioUsage")
    ComputerUsage = (81677, "OpenCare.EVODAY.DeviceUsageEvent.ComputerUsage")
    PhonerUsage = (81450, "OpenCare.EVODAY.DeviceUsageEvent.PhonerUsage")
    SmartPhonerUsage = (81969, "OpenCare.EVODAY.DeviceUsageEvent.SmartPhonerUsage")
    RehabiliationDeviceUsage = (82761, "OpenCare.EVODAY.DeviceUsageEvent.RehabiliationDeviceUsage")
    CookingDeviceUsage = (82136, "OpenCare.EVODAY.DeviceUsageEvent.CookingDeviceUsage") #!
    FridgeUsage = (81423, "OpenCare.EVODAY.DeviceUsageEvent.FridgeUsage")

    MedicalObservations = (82295, "OpenCare.EVODAY.MedicalObservations.MedicalObservations")
    Observation = (81493, "OpenCare.EVODAY.MedicalObservations.Observation")
    BloodPressureMeasurement = (82840,
                                "OpenCare.EVODAY.MedicalObservations.BloodPressureMeasurement")
    WeightMeasurement = (82103, "OpenCare.EVODAY.MedicalObservations.WeightMeasurement")
    SaturationtMeasurement = (82669, "OpenCare.EVODAY.MedicalObservations.SaturationtMeasurement")
    TemperatureMeasurement = (82653, "OpenCare.EVODAY.MedicalObservations.TemperatureMeasurement")

    Notifications = (81699, "OpenCare.EVODAY.Notifications.Notifications")
    HandwashingFollowingToiletingComplete = (84174,
                                             "OpenCare.EVODAY.Notifications.HandwashingFollowingToiletingComplete")
    RememberSoapAndHandwashAfterToilet = (83759,
                                          "OpenCare.EVODAY.Notifications.RememberSoapAndHandwashAfterToilet")
    RememberSoapBeforeHandwashAfterToilet = (84079,
                                             "OpenCare.EVODAY.Notifications.RememberSoapBeforeHandwashAfterToilet")
    RememberWashingHandsAsLastTask = (83346,
                                      "OpenCare.EVODAY.Notifications.RememberWashingHandsAsLastTask")
    HandwashingAfterToiletForgotten = (83536,
                                       "OpenCare.EVODAY.Notifications.HandwashingAfterToiletForgotten")
    PossibleFallDetected = (82347, "OpenCare.EVODAY.Notifications.PossibleFallDetected")
    LowActivityWarning = (82206, "OpenCare.EVODAY.Notifications.LowActivityWarning")
    ReplaceBatteries = (81960, "OpenCare.EVODAY.Notifications.ReplaceBatteries") #!
    SuboptimalSleep = (81890, "OpenCare.EVODAY.Notifications.SuboptimalSleep")
    SupoptimalBrushing = (82233, "OpenCare.EVODAY.Notifications.SupoptimalBrushing")
    GeneralNotification = (82286, "OpenCare.EVODAY.Notifications.GeneralNotification") #!
    MovementInHomeWhileUserNotHome = (83366,
                                      "OpenCare.EVODAY.Notifications.MovementInHomeWhileUserNotHome")
    #! We added our own eventtypes below
    StoveTurnsOn = (100000, "OpenCare.EVODAY.Notifications.StoveTurnsOn")
    StoveTurnsOff = (100001, "OpenCare.EVODAY.Notifications.StoveTurnsOff")
    SystemTurnsStoveOn = (100002, "OpenCare.EVODAY.Notifications.SystemTurnsStoveOn")
    SystemTurnsStoveOff = (100003, "OpenCare.EVODAY.Notifications.SystemTurnsStoveOff")
    CitizenLeftKitchen = (100004, "OpenCare.EVODAY.Notifications.CitizenLeftKitchen")
    CitizenEnteredKitchen = (100005, "OpenCare.EVODAY.Notifications.CitizenEnteredKitchen")


class HeucodEventJsonEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202
        def to_camel(key):
            # Convert the attribtues names from snake case (Python "default") to camel case.
            return "".join([key.split("_")[0].lower(), *map(str.title, key.split("_")[1:])])

        if isinstance(obj, HeucodEvent):
            result = deepcopy(obj.__dict__)
            keys_append = {}
            keys_remove = set()
            camel_name = {}

            for k, v in result.items():
                # Check if the name must be changed to camel case
                first, *others = k.split("_")

                if first != "id" and len(others) > 0 and v is not None:
                    camel_name[k] = to_camel(k)
                    keys_remove.add(k)

                # Remove value if it is None
                if v is None:
                    keys_remove.add(k)
                # Change the attribute "id_" to "id"
                elif k == "id_":
                    keys_append["id"] = str(v) if not isinstance(v, str) else v
                    keys_remove.add(k)
                elif isinstance(v, UUID):
                    result[k] = str(v)
                elif isinstance(v, datetime):
                    result[k] = int(v.timestamp())
                elif isinstance(v, HeucodEventType):
                    result[k] = str(v)

            for k, v in camel_name.items():
                result[v] = result[k]
            for k in keys_remove:
                result.pop(k)
            for k, v in keys_append.items():
                result[k] = v
        # Attributes to ignore
        elif isinstance(obj, HeucodEventJsonEncoder):
            pass
        else:
            # Base class default() raises TypeError:
            return json.JSONEncoder.default(self, obj)

        return result


@dataclass
class HeucodEvent:
    # --------------------  General event properties --------------------
    # The unique ID of the event. Usually a GUID or UUID but one is free to choose.
    id_: Union[UUID, str] = None
    # The type of the event. This should preferably match the name of the "class" of the device
    # following the HEUCOD ontology in enumeration HeucodEventType.
    event_type: str = None #!
    # The type of the event as an integer. This should prefaribly match the name of the "class" of
    # the device following the HEUCOD ontology in enumeration HeucodEventType.
    event_type_enum: int = None
    # This field supports adding a prose description of the event - which can e.g. by used for
    # audit and logging purposes.
    description: str = None
    # This field can contain advanced or composite values which are well-known to the specialized
    # vendors.
    advanced: str = None
    # The timestamp of the event being created in the UNIX Epoch time format.
    timestamp: int = None #!
    # Start of the observed event.
    start_time: int = None #!
    # End of the observerd event.
    end_time: int = None #!
    # The length of the event period - in milliseconds. For example, if a PIR sensor has detected
    # movement and it covers 90 seconds, it would be 90000 ms.
    length: int = None
    # For how long is the sensor blind, in seconds. forexample, a PIR sensor will detect movement
    # and then send it. After this, it will be "blind" typically between 10 and 120 seconds. This is
    # important for the classification services.
    sensor_blind_duration: int = None
    # The primary value (as a long). If the value is not a number, use the description field instead.
    value: Any = None
    # The unit of the device. The unit can be a simple unit of the SI system, e.g. meters, seconds,
    # grams, or it could be a custom unit.
    unit: str = None
    # The secondary value. If there are more than 3 values, use the advanced field to add data.
    value2: Any = None
    # The unit of the second value from the device. The unit can be a simple unit of the SI system,
    # e.g. meters, seconds, grams, or it could be a custom unit.
    unit2: str = None
    # The tertariy value. If there are more than 3 values, use the advanced field to add data.
    value3: Any = None
    # The unit of the third value from the device. The unit can be a simple unit of the SI system,
    # e.g. meters, seconds, grams, or it could be a custom unit.
    unit3: str = None
    # Is this a direct event? This mean there is no gateway involved.
    direct_event: bool = None
    sending_delay: int = None
    advanced: str = None
    # -------------------- Patient details --------------------
    # ID of the user or patient to whom this event belongs.
    patient_id: str = None
    # ID of the caregiver - e.g. one helping with a rehab or care task that is reported.
    caregiver_id: int = None
    # The ID that can be used to monitor events of this person.
    monitor_id: str = None
    # Location can be an addres or apartment ID.
    location: str = None
    street_adress: str = None
    city: str = None
    postal_code: str = None
    # Could be the name or identifier of the care facility or care organization.
    site: str = None
    # Name of the room where the event occured (if any).
    room: str = None
    # -------------------- Sensor details --------------------
    # All sensors should have a unique ID which they continue to use to identify themselves.
    sensor_id: str = None
    # The type of sensor used.
    sensor_type: str = None
    sensor_location: str = None
    sensor_rtc_clock: bool = None
    # The model of the device.
    device_model: str = None
    # The vendor of the device.
    device_vendor: str = None
    # The ID of a gatway who is either relaying the event from a sensor or if the event is generated
    # by the gateway itself.
    gateway_id: str = None
    # The ID of the service generating the event. A service can be a sensor monitoring service, or
    # it could be a higher level service - interpreting data from one or more sensors and even from
    # several sensors, and maybe historical data.
    service_id: str = None
    # The average power consumption of the device in watts. Use together with the length attribute
    # to calcualte the value in kWh (kilowatt/hour).
    power: int = None
    # The battery level in percentage (0-100). A battery alert service may use this information to
    # send alerts at 10% or 20 % battery life - and critical alerts at 0%.
    battery: int = None
    # Sensor RSSI (Received Signal Strength Indicator). It is often used with radio based networks,
    # including WiFi, BLE, Zigbee and Lora.
    rssi: float = None
    # Measured Power indicates what’s the expected RSSI at a distance of 1 meter to the beacon.
    # Combined with RSSI, it allows to estimate the distance between the device and the beacon.
    measured_power: float = None
    # Signal-to-noise ratio(abbreviated SNR or S/N) is a measure used in science and engineering
    # that compares the level of a desired signal to the level of background noise.SNR is defined as
    # the ratio of signal power to the noise power, often expressed in decibels.
    signal_to_noise_ratio: float = None
    # The self-reproted accuracy of the sensor or service event. For example, a sensor may be 99%
    # sure that it has detected a fall, while a classification service may be 88% sure.
    accuracy: int = None
    # Link Quality (LQ) is the quality of the real data received in a signal. This is a value from 0
    # to 255, being 255 the best quality. Typically expect from 0 (bad) to 50-90 (good). It is
    # related to RSSI and SNR values as a quality indicator.
    link_quality: float = None
    # -------------------- Python class specific attributes --------------------
    json_encoder = HeucodEventJsonEncoder

    @classmethod
    def from_json(cls, event: str) -> HeucodEvent:
        if not event:
            raise ValueError("The string can't be empty or None")

        try:
            json_obj = json.loads(event)
        except json.JSONDecodeError as ex:
            raise ex from None

        instance = cls()

        # Convert the names of the JSON attributes to snake case (from camel case).
        obj_dict = {}
        for k, v in json_obj.items():
            if k != "id":
                key_tokens = re.split("(?=[A-Z])", k)
                obj_dict["_".join([t.lower() for t in key_tokens])] = v
            else:
                # The id_ attribtues is an exception of the naming standard. In Python, id is a
                # reserved word and its use for naming variables/attribtues/... should be avoided.
                # Thus the name id_.
                obj_dict["id_"] = v

        instance = dataclass_replace(instance, **obj_dict)

        return instance

    def to_json(self):
        if not self.json_encoder:
            raise TypeError("A converter was not specified. Use the converter attribute to do so.")

        # The dumps function looks tries to serialize the JSON string based in the JSON encoder that
        # is passed in the second argument. In this case, it will be the class HeucodEventJsonEncoder,
        # that inherits json.JSONEncoder. It has only the default() function this is called by
        # dumps() when serializing the class.
        return json.dumps(self, cls=self.json_encoder)
