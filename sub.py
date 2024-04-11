import paho.mqtt.client as mqtt
import json, time
from threading import Thread

#client.publish("zigbee2mqtt/LED-strip grp2/set", '{"brightness" : "ON"}')
#client.publish("zigbee2mqtt/LED-strip grp2/set", '{"color" : {"hue":0,"saturation":100,"x":0.7006,"y":0.2993} }')

system_on = False

def run():
    timer = time.time()
    print("Time is: ", timer)



def on_message(client, userdata, msg):
    global system_on, timer
    topic = msg.topic
    payload = msg.payload
    payload = json.loads(payload.decode('utf-8'))
    if topic == "zigbee2mqtt/Actuator grp2":
        print("Besked fra actuator")
        
        if system_on == False and payload["power"] > 10:
            run()
            print("System is on")
            timer = time.time()
            print("Time is: ", timer)
            system_on = True
    if system_on:
        if topic == "zigbee2mqtt/Sensor grp2":
            print("Besked fra Køkken")
            timer = time.time()
            print("timer is reset")

        if topic == "zigbee2mqtt/Sensor 3 grp2":
            print("Besked fra Stue")
            if time.time() > timer + 30:
                client.publish("zigbee2mqtt/Actuator grp2/set", '{"state": "OFF"}')
                print("Timer exceeded maximum: slukker pc")

    
    #elif timer > 30:
    #    system_on = False
    
    
    #if payload["occupancy"] == False:
    #    client.publish("zigbee2mqtt/Actuator grp2/set", '{"state": "OFF"}')
    #    print("slukker pc")
    #else:
    #    client.publish("zigbee2mqtt/Actuator grp2/set", '{"state": "ON"}')
    #    print(payload["occupancy"])
    #print(f"topic = {msg.topic}, payload = {msg.payload}")



client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("zigbee2mqtt/Sensor 3 grp2")
client.subscribe("zigbee2mqtt/Sensor grp2")
client.subscribe("zigbee2mqtt/Actuator grp2")
client.loop_forever()


