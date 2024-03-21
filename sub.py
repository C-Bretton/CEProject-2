import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"topic = {msg.topic}, payload = {msg.payload}")
    
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("zigbee2mqtt/Sensor 3 grp2")
client.loop_forever()