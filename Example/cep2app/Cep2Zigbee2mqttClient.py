from __future__ import annotations
import json
from dataclasses import dataclass
from enum import Enum
from queue import Empty, Queue
from threading import Event, Thread
from time import sleep
from typing import Any, Callable, List, Optional
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe


class Cep2Zigbee2mqttMessageType(Enum):
    """ Enumeration with the type of messages that zigbee2mqtt publishes.
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


@dataclass
class Cep2Zigbee2mqttMessage:
    """ This class represents a zigbee2mqtt message. The fields vary with the topic, so not all
    attributes might have a value. If the message does not have a field, its value defaults to None.
    """

    # A note about dataclasses: this is a Python feature that allows to simplify the implementation
    # of a class by only declaring its attributes (or fields) and respective types. In the
    # background, an initializer is created that receives as arguments the declared attributes. This
    # can be observed in the parse() method, where instances of Cep2Zigbee2mqttMessage are created
    # with varying arguments, depending on the topic and message received.
    # If a field is not declared with a default value, then it is mandatory in the initializer;
    # otherwise, a value does not need to be given as argument. For this class, the topic and type_
    # fields do not have a default value, therefore they have to be given as arguments to the
    # initializer. All other values are optional.

    topic: str
    type_: Cep2Zigbee2mqttMessageType
    data: Any = None
    event: Any = None
    message: Any = None
    meta: Any = None
    status: str = None
    state: str = None

    @classmethod
    def parse(cls, topic: str, message: str) -> Cep2Zigbee2mqttMessage:
        """ Parse a zigbee2mqtt JSON message, based on the received topic.

        Args:
            topic (str): message's topic
            message (str): JSON message that will be parsed

        Returns:
            Cep2Zigbee2mqttMessage: an object with the parsed message values
        """
        # A note about class methods: these methods can be used to instantiate the class where it is
        # declared. In this case, this method returns an instance of Cep2Zigbee2mqttMessage based on
        # the topic and message that are given as arguments.
        # In Python, like other object oriented languages, a method can be an instance method
        # (called from an object), a static method (called from the class), or a class method
        # (similar to static methods, but receives the class it instantiates as the first argument).
        # This is a Python feature that is usually not found in other languages and is an
        # implementation of the factory design pattern. More information can be found in the
        # following links:
        #     - Class methods: https://stackabuse.com/pythons-classmethod-and-staticmethod-explained/
        #     - Factory design pattern: https://refactoring.guru/design-patterns/factory-method

        if topic == "zigbee2mqtt/bridge/state":
            instance = cls(type_=Cep2Zigbee2mqttMessageType.BRIDGE_STATE,
                           topic=topic,
                           state=message)
        elif topic in ["zigbee2mqtt/bridge/event", "zigbee2mqtt/bridge/logging"]:
            type_ = {"zigbee2mqtt/bridge/event": Cep2Zigbee2mqttMessageType.BRIDGE_EVENT,
                     "zigbee2mqtt/bridge/log": Cep2Zigbee2mqttMessageType.BRIDGE_LOG}.get(topic)
            message_json = json.loads(message)
            instance = cls(type_=type_,
                           topic=topic,
                           data=message_json.get("data"),
                           message=message_json.get("message"),
                           meta=message_json.get("meta"))
        elif topic in ["zigbee2mqtt/bridge/config",
                       "zigbee2mqtt/bridge/info",
                       "zigbee2mqtt/bridge/devices",
                       "zigbee2mqtt/bridge/groups",
                       "zigbee2mqtt/bridge/request/health_check",
                       "zigbee2mqtt/bridge/response/health_check"]:
            instance = None
        else:
            instance = cls(type_=Cep2Zigbee2mqttMessageType.DEVICE_EVENT,
                           topic=topic,
                           event=json.loads(message))

        return instance


class Cep2Zigbee2mqttClient:
    """ This class implements a simple zigbee2mqtt client.

    By default it subscribes to all events of the default topic (zigbee2mqtt/#). No methods for
    explicitly publishing to zigbee2mqtt are provided, since the class can provide higher level
    abstraction methods for this. An example implemented example is this class' check_health().

    Since all events from zigbee2mqtt are subscribed, the events filtering and management are up to
    the class user. For that, a callback can be set in the initializer (on_message_clbk) for
    processing the received messages. This callback is blocking, i.e. once the subscriber receives
    an event and invokes the callback, no new events will be processed. Careful should be taken with
    methods that might take too much time to process the events or that might eventually block (for
    example, sending an event to another service).
    """
    ROOT_TOPIC = "zigbee2mqtt/#"

    def __init__(self,
                 host: str,
                 on_message_clbk: Callable[[Optional[Cep2Zigbee2mqttMessage]], None],
                 port: int = 1883,
                 topics: List[str] = [ROOT_TOPIC]):
        """ Class initializer where the MQTT broker's host and port can be set, the list of topics
        to subscribe and a callback to handle events from zigbee2mqtt.

        Args:
            host (str): string with the hostname, or IP address, of the MQTT broker.
            on_message_clbk (Callable[[Zigbee2mqttMessage], None]): a function that is called when
                a message is received from zigbee2mqtt. This returns None if the 
            port (int): network port of the MQTT broker. Defaults to 1883.
            topics (List[str], optional): a list of topics that the client will subscribe to.
                Defaults to ["zigbee2mqtt/#"].
        """
        self.__client = MqttClient()
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_message = self.__on_message
        self.__connected = False
        self.__events_queue = Queue()
        self.__host = host
        self.__on_message_clbk = on_message_clbk
        self.__port = port
        self.__stop_worker = Event()
        self.__subscriber_thread = Thread(target=self.__worker,
                                          daemon=True)
        self.__topics = topics

    def connect(self) -> None:
        """ Connects to the MQTT broker specified in the initializer. This is a blocking function.
        """
        # In the client is already connected then stop here.
        if self.__connected:
            return

        # Connect to the host given in initializer.
        self.__client.connect(self.__host,
                              self.__port)
        self.__client.loop_start()
        # Subscribe to all topics given in the initializer.
        for t in self.__topics:
            self.__client.subscribe(t)
        # Start the subscriber thread.
        self.__subscriber_thread.start()

    def change_state(self, device_id: str, state: str) -> None:
        if not self.__connected:
            raise RuntimeError("The client is not connected. Connect first.")

        self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set",
                              payload=json.dumps({"state": f"{state}"}))

    def check_health(self) -> str:
        """ Allows to check whether zigbee2mqtt is healthy, i.e. the service is running properly.
        
        Refer to zigbee2mqtt for more information. This is a blocking function that waits for a
        response to the health request.

        Returns:
            A string with a description of zigbee2mqtt's health. This can be 'ok' or 'fail'. 
        """
        health_status = "fail"
        health_response_received = Event()

        # This function will run the subscriber on a thread. The subscriber must be started first,
        # so that the health_check message is received, even if the broker does not have message
        # persistence active. This should also avoid that messages with QoS 0 are not received.
        # Also, if the subscriber is started after, it could happen the message to be received by
        # another subscriber and never by this one.
        # More information can be found in
        # https://pagefault.blog/2020/02/05/how-to-set-up-persistent-storage-for-mosquitto-mqtt-broker
        def health_check_subscriber():
            message = subscribe.simple(hostname=self.__host,
                                       port=self.__port,
                                       topics="zigbee2mqtt/bridge/response/health_check")

            if message:
                # Decode and parse JSON payload.
                payload = message.payload.decode("utf-8")
                health = json.loads(payload)

                # The nonlocal keyword is used to set the variable health_status that is not defined
                # in this function's scope. For more information got to
                # https://www.programiz.com/python-programming/global-local-nonlocal-variables
                nonlocal health_status
                health_status = health.get("status", "fail")
                # Set the flag so that the function exits.
                health_response_received.set()

        # Start a thread with the subscriber that will wait for the response of the health_check.
        Thread(target=health_check_subscriber, daemon=True).start()
        # Wait for the subscriber to establish a connection with the broker.
        sleep(.5)
        # Publish the health_check request.
        publish.single(hostname=self.__host,
                       port=self.__port,
                       topic="zigbee2mqtt/bridge/request/health_check")
        # Wait until the response is received. If it is not received within 5 seconds, then return
        # the default state: "fail".
        health_response_received.wait(timeout=5)

        return health_status

    def disconnect(self) -> None:
        """ Disconnects from the MQTT broker.
        """
        self.__stop_worker.set()
        self.__client.loop_stop()
        # Unsubscribe from all topics given in the initializer.
        for t in self.__topics:
            self.__client.unsubscribe(t)
        self.__client.disconnect()

    def __on_connect(self, client, userdata, flags, rc) -> None:
        """ Callback invoked when a connection with the MQTT broker is established.

        Refer to paho-mqtt documentation for more information on this callback:
        https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#callbacks
        """

        # Set connected flag to true. This is later used if multiple calls to connect are made. This
        # way the user does not need to very if the client is connected.
        self.__connected = True
        print("MQTT client connected")

    def __on_disconnect(self, client, userdata, rc) -> None:
        """ Callback invoked when the client disconnects from the MQTT broker occurs.

        Refer to paho-mqtt documentation for more information on this callback:
        https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#callbacks
        """

        # Set connected flag to false. This is later used if multiple calls to connect are made.
        # This way the user does not need to very if the client is connected.
        self.__connected = False
        print("MQTT client disconnected")

    def __on_message(self, client, userdata, message: MQTTMessage) -> None:
        """ Callback invoked when a message has been received on a topic that the client subscribed.

        Refer to paho-mqtt documentation for more information on this callback:
        https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#callbacks
        """

        # Push a message to the queue. This will later be processed by the worker.
        self.__events_queue.put(message)

    def __worker(self) -> None:
        """ This method pulls zigbee2mqtt messages from the queue of received messages, pushed when
        a message is received, i.e. by the __on_message() callback. This method will be stopped when
        the instance of zigbee2mqttClient disconnects, i.e. disconnect() is called and sets the
        __stop_worker event.
        """
        while not self.__stop_worker.is_set():
            try:
                # Pull a message from the queue.
                message = self.__events_queue.get(timeout=1)
            except Empty:
                # This exception is raised when the queue pull times out. Ignore it and retry a new
                # pull.
                pass
            else:
                # If a message was successfully pulled from the queue, then process it.
                # NOTE: this else condition is part of the try and it is executed when the action
                # inside the try does not throws and exception.
                # The decode() transforms a byte array into a string, following the utf-8 encoding.
                if message:
                    self.__on_message_clbk(Cep2Zigbee2mqttMessage.parse(message.topic,
                                                                        message.payload.decode("utf-8")))
