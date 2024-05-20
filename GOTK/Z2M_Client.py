import queue
import json
from typing import Callable, List, Optional
from threading import Thread, Event
from paho.mqtt.client import Client as MqttClient, MQTTMessage

from Z2M_Message import Z2M_Message


class Z2M_Client:
    """
        This class implements a Zigbee2Mqtt client, which subscribes to the events in the root topic "zigbee2mqtt/#" and starts a subscriber thread.
        When it receives a message from a topic it puts the message in the event queue. If there are messages in the event queue, 
        a callback is set to process the received messages. This callback is blocking, meaning once the subscriber receives
        an event and invokes the callback, no new events will be processed.
    """
    
    # Default topic
    ROOT_TOPIC = "zigbee2mqtt/#"
    
    def __init__(self, host: str, on_message_callback: Callable[[Optional[Z2M_Message]], None], port: int = 1883, topics: List[str] = [ROOT_TOPIC]):
        """
            Initializes the Z2M Client with the specified MQTT broker's host and port, the list of topics
            to subscribe and a callback to handle events from zigbee2mqtt.
        """
        
        self.__client = MqttClient()
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_message = self.__on_message
        self.__connected = False
        self.__events_queue = queue.Queue()
        self.__host = host
        self.__port = port
        self.__on_message_callback = on_message_callback        
        self.__stop_worker = Event()
        self.__topics = topics
        
    def connect(self):
        """
            Connects to the MQTT broker specified in the initializer.
        """
        # Checks whether or not the client is already connected. Returns if already connected.
        if self.__connected:
            return
        
        # Connects to the host.
        self.__client.connect(self.__host, self.__port)
        self.__client.loop_start()
        
        # Subscribe to all topics given in initializer.
        for t in self.__topics:
            self.__client.subscribe(t)

        #Clears __stop_worker event flag, initializes subscriber thread, and starts the thread 
        self.__stop_worker.clear()
        self.__subscriber_thread = Thread(target=self.__worker, daemon=True)
        self.__subscriber_thread.start()
        
    
    def disconnect(self):
        """
            Disconnects from the MQTT broker.
        """
        # Sets event and thereby stops worker.
        self.__stop_worker.set()
        self.__client.loop_stop()
        
        #Test if thread is dealt with ----
        if self.__subscriber_thread.is_alive():
            print("Sub Thread is alive - join!")
            self.__subscriber_thread.join()
        else:
            print("Worker Should be stopped")
                
        # Unsubscribe from all topics given in initializer.
        for t in self.__topics:
            self.__client.unsubscribe(t)
        
        # Disconnects client
        self.__client.disconnect()
          
    def Actuator_Controls(self, device_id : str, state : str):
        """
            Method to publish changes to the Actuator state.  The device_id is used to publish to the right topic
            and sets the state to the specified state.
        """
        if not self.__connected:
            pass
        
        self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", payload=json.dumps({"state": f"{state}"}))
    
    def Light_Controls(self, light_state : str, device_id : str):
        """
            Method to publish changes to the Light devices. The method uses the device_id to identify which device to publish to
            and the light_state to choose which settings the light should be given.
        """
        if not self.__connected:
            pass
        
        if light_state == "Dim": 
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 10, "effect": "finish_effect"}))
            
        elif light_state == "Limit":
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 10, "effect": "breathe"}))
    
        elif light_state == "Notify":
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 5, "effect": "breathe"}))
    
        elif light_state == "On":
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 1, "effect": "finish_effect"}))
            
        elif light_state == "Off":
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 0, "effect": "finish_effect"}))

    def __on_message(self, client, userdata, message: MQTTMessage):
        """ Callback invoked when a message has been received on a topic that the client subscribed.
        """
        #Push a message to the queue
        self.__events_queue.put(message)

    def __on_connect(self, client, userdata, flags, rc):
        """ Callback invoked when a connection with the MQTT broker is established. """
        # Set connected flag to true.
        self.__connected = True
        
    def __on_disconnect(self, client, userdata, rc):
        """ Callback invoked when the client disconnects from the MQTT broker. """
        # Set connected flag to false.
        self.__connected = False
    
    def __worker(self):
        """
        This method pulls zigbee2mqtt messages from the queue of received messages. This method will be stopped when
        the instance of zigbee2mqttClient disconnects, i.e. disconnect() is called and sets the
        __stop_worker event.
        """
        #Runs while the __stop_worker event is not set.
        while not self.__stop_worker.is_set():
            try:
                message = self.__events_queue.get(timeout=1)
            except queue.Empty:
                # This exception is raised when the queue pull times out. Ignore it and retry
                pass
            else: 
                # If a message was successfully pulled from the queue, then process it.
                if message:
                    self.__on_message_callback(Z2M_Message(message.topic, message.payload.decode("utf-8")))
