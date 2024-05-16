import queue
import json
from typing import Callable, List, Optional
from threading import Thread, Event
from paho.mqtt.client import Client as MqttClient, MQTTMessage

from Z2M_Message import Z2M_Message


class Z2M_Client:
    """
    \_(-_-)_/
    """
    
    # Default topic
    ROOT_TOPIC = "zigbee2mqtt/#"

    def __init__(self, host: str, on_message_callback: Callable[[Optional[Z2M_Message]], None], port: int = 1883, topics: List[str] = [ROOT_TOPIC]):
        """
        ಠ╭╮ಠ
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
        # self.__subscriber_thread = Thread(target=self.__worker, daemon=True)
        self.__topics = topics
        
    
    def connect(self):
        """
        ༼ つ ಥ_ಥ ༽つ
        nemt, done!
        """
        
        # Checks whether or not the client is already connected. Returns if already connected.
        print("Forbindelse oprettet")
        if self.__connected:
            return
        
        # Connects to the host.
        self.__client.connect(self.__host, self.__port)
        self.__client.loop_start()
        
        # Subscribe to all topics given in initializer.
        for t in self.__topics:
            self.__client.subscribe(t)
    
        self.__subscriber_thread = Thread(target=self.__worker, daemon=True)  #Initialize thread
        self.__stop_worker.clear()  #stop_worker flag needs to be reset (clear()) for it to send messages again
        
        # Starts subscriber thread.
        self.__subscriber_thread.start()
        
    
    def disconnect(self):
        """
        (▀̿Ĺ̯▀̿ ̿)
        """
        
        # Sets event and thereby stops worker.
        self.__stop_worker.set()
        self.__client.loop_stop()
        
        #Test if thread is dealt with ----
        if self.__subscriber_thread.is_alive():
            print("Sub Thread is alive - join!")
            self.__subscriber_thread.join()
        
        # Unsubscribe from all topics given in initializer.
        for t in self.__topics:
            self.__client.unsubscribe(t)
        
        # Disconnects client
        self.__client.disconnect()
        
        
    def Actuator_Controls(self, device_id : str, state : str):
        if not self.__connected:
            print("\n --Actuator not connected-- \n")
            pass
        print("\n --Actuator connected-- \n")
        self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", payload=json.dumps({"state": f"{state}"}))
    
    
    def Light_Control(self, light_state : str, device_id : str):
        if not self.__connected:
            pass
        
        #Ændre til at det er de rum hvor der er occupancy i der får lys
        
        if light_state == "Shutdown":
            # print("\n----- Light_state: ", light_state, " -------- Switch This light: ", device_id)
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 10, "effect": "finish_effect"}))
            
        elif light_state == "Limit":
            # print("\n----- Light_state: ", light_state, " -------- Switch This light: ", device_id)
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 10, "effect": "breathe"}))
    
        elif light_state == "Notify":
            # print("\n----- Light_state: ", light_state, " -------- Switch This light: ", device_id)
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 5, "effect": "breathe"}))
    
        elif light_state == "On":
            # print("\n----- Light_state: ", light_state, " -------- Switch This light: ", device_id)
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 1, "effect": "finish_effect"}))
            
        elif light_state == "Off":
            # print("\n----- Light_state: ", light_state, " -------- Switch This light: ", device_id)
            self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", 
                                  payload=json.dumps({"brightness": 0, "effect": "finish_effect"}))
        
        
        # self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set", payload=json.dumps({"brightness": brightness, "color": color, "effect": effect}))
    
    
    
    def __on_message(self, client, userdata, message: MQTTMessage):
        
        self.__events_queue.put(message)

    
    def __on_connect(self, client, userdata, flags, rc):
        print("connected set to true")
        self.__connected = True
        
        
    def __on_disconnect(self, client, userdata, rc):
        self.__connected = False
    
    
    def __worker(self):
        """
        ̿̿ ̿̿ ̿̿ ̿'̿'\̵͇̿̿\з= ( ▀ ͜͞ʖ▀) =ε/̵͇̿̿/’̿’̿ ̿ ̿̿ ̿̿ ̿̿
        """
        
        while not self.__stop_worker.is_set():
            try:
                message = self.__events_queue.get(timeout=1)
            except queue.Empty:
                pass
            else:
                if message:
                    self.__on_message_callback(Z2M_Message(message.topic, message.payload.decode("utf-8")))
