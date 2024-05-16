import time
from LogicController import LogicController
from DeviceModel import DeviceModel, ZigbeeDevice
import json
import paho.mqtt.client as mqtt
from Logger import Logger


def start_system():
    
    controller = LogicController(device_model=device_model)
    controller.Start_System()

    while controller.IS_RUNNING:
        time.sleep(1)

    idle()

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode('utf-8'))
    print(payload)
    #But is this necesarry?? underneath with turn on Actuator.
    if "occupancy" in payload and payload["occupancy"] == True: ##To make sure that actuator is on when client enters kitchen. in case it was turned of by system only if actuator is off
        client.publish(topic=f"zigbee2mqtt/Actuator/set", payload=json.dumps({"state": "ON"}))
        # TestLog.logCitizenEnteredKitchen()
        client.unsubscribe("zigbee2mqtt/Sensor 0")
        print("Client has entered kitchen - Actuator is turned on")
    if "power" in payload and payload["power"] >= 6: #! Does this need flag to avoid double logs and system
        TestLog.logStoveOn()
        print("Stove has been turned on! Closing idle mode")
        client.disconnect()
        print("Surveillance has been activated!")
        start_system()
        
            
        

def idle():
    print("Idle mode is now Active")
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe("zigbee2mqtt/Actuator")
    client.subscribe("zigbee2mqtt/Sensor 0")
    
    client.loop_forever()
    print("now listening")


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
    
    print("------------- SYSTEM ACTIVATED --------------")
    
    TestLog = Logger()
    
    idle()
    
   
    #initialize controller in main
    
    
    
    # TestLog.logCitizenEnteredKitchen()
    
    # TestLog.logCitizenLeftKitchen()
    
    # TestLog.logStoveOn()
    
    # TestLog.logStoveOff()
    
    # TestLog.logSystemTurnsStoveOff()
    
    # TestLog.logSystemTurnsStoveOn()    
    
    print("!!!!!!!!!!!!!!!!!! Somehow system ended !!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    
    










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

