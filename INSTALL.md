# **Installation Guide**

Follow these steps to set up the Kitchen Guard system:

## **Hardware Setup**

1. Connect the Raspberry Pi 5 to a power source and network.

2. Attach the Sonoff Zigbee USB Dongle to the Raspberry Pi.

3. Place the Aqara Motion Sensors in strategic locations in all the different rooms to detect user presence.

4. Connect the Immax Neo Smart Plug to a power outlet and to the stove.

5. Install the Ikea TRÅDFRI light bulbs in all rooms.


## **Software Setup**

1. Ensure that the Raspberry Pi is set up and running as specified in *Tutorial 1: Setting up a Raspberry Pi*.

2. Open a terminal and update the package list:
```bash
sudo apt update
```

3. Install the necessary dependencies:
```bash
sudo apt install python3 python3-pip git
```

4. Clone the Kitchen Guard repository:
```bash
git clone https://github.com/C-Bretton/CEProject-2.git
cd CEProject-2
```

5. Install the required Python packages:
```bash
pip3 install -r requirements.txt
```

6. Install and Set up Zigbee2MQTT as specified in both *Tutorial 2: Getting started with MQTT* and *Tutorial 3: Setting up Zigbee2Mqtt*. Eventually, refer to [Zigbee2MQTT Documentation](https://www.zigbee2mqtt.io/).


## **Configuration**

1. Pair all needed devices with Zigbee2MQTT.

2. Inside `GOTK.py`, update the list of devices to match your hardware setup.

<br/>

# **Running the System**

Once the installation is complete, follow these steps to run the Kitchen Guard system:

1. Open up two different terminals. In the first terminal, navigate to your Zigbee2MQTT folder and start it with the command:
```bash
npm start
```

2. Start up the PHP server. Please refer to [GOTKPHPServer Repository](https://github.com/Losmobilos3/GOTKPHPServer).

3. In the second terminal, navigate to the repository and run the Kitchen Guard system:
```bash
python3 GOTK/GOTK.py
```
