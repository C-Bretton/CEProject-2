import time
from LogicController import LogicController
from DeviceModel import DeviceModel, ZigbeeDevice
import json
import paho.mqtt.client as mqtt
from Logger import Logger

#Initializes and starts the logic controller which handles the logic when the stove is on
def start_controller():
    
    controller.Start()

    #Loop while the controller is running, when stove is not in use it exits this loop
    while controller.Controller_Mode:
        time.sleep(1)

    #When stove is not in use and loop is exited, the system goes into idle mode again.
    idle()

#Idle mode: Checks messages from kitchen sensor and actuator, if activity in kitchen and actuator detects power flow it starts the controller
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode('utf-8'))
    print(payload)
    
    #Check that there has been movement in kitchen before controller can be started again. 
    if "occupancy" in payload and payload["occupancy"] == True:
        #Ensures that actuator is on when citizen enters kitchen
        client.kitchen_movement = True
        client.publish(topic=f"zigbee2mqtt/Actuator/set", payload=json.dumps({"state": "ON"}))
        client.unsubscribe("zigbee2mqtt/Sensor 0")
        print("Client has entered kitchen - Actuator is turned on")
        
    elif "power" in payload and payload["power"] >= 6 and client.kitchen_movement == True:
        print("Stove has been turned on! Closing idle mode")
        client.disconnect()
        
        #Assigns the received actuator values to the Actuator Dictionary, containing last detected actuator values.
        controller.actuator_dict["State"] = payload["state"]
        controller.actuator_dict["Power"] = payload["power"] 
        controller.actuator_dict["PowerWasRegistered"] = True
        
        print("Starting the Controller!")
        start_controller()
        
#Idle mode for the system while the stove is not in use
def idle(): 
    print("Idle mode is now Active")
    client = mqtt.Client()
    client.kitchen_movement = False
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe("zigbee2mqtt/Actuator")
    client.subscribe("zigbee2mqtt/Sensor 0")
    
    client.loop_forever()
    print("now listening")


#Main Initializing device model and starts idle mode
if __name__ == "__main__":
    
    device_model = DeviceModel()
    device_model.add([ZigbeeDevice("Sensor 0", "pir"),
                      ZigbeeDevice("Sensor 1", "pir"),
                      ZigbeeDevice("Sensor 2", "pir"),
                      ZigbeeDevice("Sensor 3", "pir"),
                      ZigbeeDevice("Sensor 4", "pir"),
                      ZigbeeDevice("Bulb 1", "light"),
                      ZigbeeDevice("Bulb 2", "light"),
                      ZigbeeDevice("Bulb 3", "light"),
                      ZigbeeDevice("Bulb 4", "light"),
                      ZigbeeDevice("Actuator", "power plug")])
    controller = LogicController(device_model=device_model)
    
    print("------------- SYSTEM ACTIVATED --------------")

    idle()
    
    #System should keep running going between the idle and controller mode

    
    










# def on_message(client: mqtt.Client, userdata, msg):
#     payload = msg.payload
#     payload = json.loads(payload.decode('utf-8'))    
#     if payload["power"] > 10:
#         system_on = True
#         client.disconnect()

    #while True:

        #client = mqtt.Client()
        #client.on_message = on_message
        #client.connect("localhost", 1883)
        #client.subscribe("zigbee2mqtt/Actuator")
        #client.loop_start()

        #while client:
            #print("Stove is off")

