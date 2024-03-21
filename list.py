import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883)
client.publish("zigbee2mqtt/Actuator grp2/set", '{"state" : "ON"}')
client.disconnect()