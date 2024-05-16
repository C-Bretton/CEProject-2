#import paho.mqtt.client as mqtt

#client = mqtt.Client()
#client.connect("localhost", 1883)
#client.publish("zigbee2mqtt/Actuator grp2/set", '{"state" : "ON"}')
#client.disconnect()

import time
import json
import paho.mqtt.client as mqtt




def start_system():
    print("starting system")

    while True:
        time.sleep(1)
        print("running")
    
    idle()
    

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode('utf-8'))
    print(msg)
    if payload["power"] > 10:
        print("power detected! destroying fake client...")
        client.disconnect()
        print("starting the controller")
        start_system()


def idle():
    print("starting fake client...")
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe("zigbee2mqtt/Actuator")
    client.loop_forever()
    print("now listening")
    

if __name__ == "__main__":
    idle()





#def start_system():
#    device_model = DeviceModel()
#    device_model.add([ZigbeeDevice("Sensor 0", "pir"),
#                      ZigbeeDevice("Sensor 3", "pir"),
#                      ZigbeeDevice("0x680ae2fffec0cbba", "led"),
#                      ZigbeeDevice("Actuator", "power plug")])
      
#    controller = LogicController(device_model=device_model)
#    controller.Start_System()

#    while True:
#        time.sleep(1)
    
#    idle()
    

#def on_message(client, userdata, msg):
#    payload = json.loads(msg.payload.decode('utf-8'))
#    if payload["power"] > 10:
#        client.disconnect()
#        start_system()


#def idle():
#    client = mqtt.Client()
#    client.on_message = on_message
#    client.connect("localhost", 1883)
#    client.subscribe("zigbee2mqtt/Actuator grp2")
#    client.loop_forever()


#if __name__ == "__main__":
#    idle()