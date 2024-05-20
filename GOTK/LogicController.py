from DeviceModel import DeviceModel
from Timer import Timer
from threading import Thread
import time
from Logger import Logger

from Z2M_Client import Z2M_Client
from Z2M_Message import Z2M_Message
from Z2M_MessageType import Z2M_MessageType

class LogicController:
    """
    The logic controller is the main driver for the GOTK system. When the stove is active it listens to the messages from the 
    devices and holds the logic that actuates based on the messages received from the Z2M_Client.
    """

    HTTP_HOST = "http://localhost:8000"
    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883

    #Initializes the controller
    def __init__(self, device_model: DeviceModel) -> None:
        """
            Write something good here #! Do this!!!
        """
        self.__device_model = device_model
        self.__z2m_client = Z2M_Client(host = self.MQTT_BROKER_HOST,
                                       port = self.MQTT_BROKER_PORT,
                                       on_message_callback=self.__zigbee2mqtt_event_received)
        
        #Initialise Logger and Timers
        self.System_Logger = Logger()
        self.__clock_away = Timer()
        self.__clock_actuator = Timer()
        
        #Initialise dictionaries for sensors and lights in each room. Create room occupancy dictionary and actuator dictionary
        self.room_sensor = {"Sensor 0": "Kitchen", "Sensor 1": "Room 1", "Sensor 2": "Room 2", "Sensor 3": "Room 3", "Sensor 4": "Room 4"}
        self.room_light = {"Room 1": "Bulb 1", "Room 2": "Bulb 2", "Room 3": "Bulb 3", "Room 4": "Bulb 4"}
        self.room_occupancy = {}        
        self.actuator_dict = {}
        
        
    def Start(self) -> None:
        """
        When the Controller is started, it connects to the Z2M-Client listening to the zigbee2mqtt messages. It 
        """
        print("System started")
        self.__z2m_client.connect()
        
        self.Controller_Mode = True
        
        #Start Actuator Clock
        self.__clock_actuator.Start()
        
        #Call Kitchen_Entered Method. Flag to maintain occupancy in room with last detected movement is initialized
        self.Kitchen_Entered()
        self.occupancy_flag = None
        
        #Initialise timer threads - Away Timer and Actuator Timer
        self.__Away_Timer_Thread = Thread(target = self.Away_Timer, daemon = True)
        self.__Actuator_Thread = Thread(target = self.Actuator_Timer, daemon = True)
        
        #Set boolean true, controlling the loop in Away Timer Thread and start the thread.
        self.Away_Thread_Running = True
        self.__Away_Timer_Thread.start()
        
        #Set boolean true, controlling the loop in Actuator Thread and start thread.
        self.Actuator_Thread_Running = True
        self.__Actuator_Thread.start()

    #Function to switch into idle mode
    def Go_Idle(self) -> None:
        """
        Stops listening to zigbee2mqtt messages, and stops the loop for the controller client. #!Controller mode?
        """
        print("Go Idle is called")
        #Make sure clocks are stopped and threads are stopped by setting their running flags to false. 
        self.__clock_actuator.Stop()
        self.__clock_away.Stop()
        self.Actuator_Thread_Running = False
        self.Away_Thread_Running = False
        
        #Disconnects the Z2M Client - stops listening to devices.
        self.__z2m_client.disconnect()
        print("Client is disconnected")
        
        #Change Boolean for controller loop to false.
        self.Controller_Mode = False
    
    def Away_Timer(self):
        """
            Thread for the Away From Kitchen Timer. When the timer is active, it checks the timer and notifies citizen,
            when certain thresholds are exceeded
        """
        print("---------Away Timer Thread has started!---------")
        #The Threads While-loop continues as long as the running flag is true
        while self.Away_Thread_Running:
            
            #Ensures that it only checks the timer when it is active.
            if self.__clock_away.Timer_Active:
                print("\n------------- Away Timer:", self.__clock_away.Time_Passed(), "-------------")
                #Check the timer and set state depending on time passed
                timer_state = self.__clock_away.Check_Timer()
                
                #The Upper Threshold - In case the kitchen is left for too long, it goes into idle mode, to save resources
                if timer_state == "Upper":
                    print("\n------------------------------------UPPER THRESHOLD EXCEEDED!!!!!!!--------------------")
                    
                    #Publish "Dim" state to all active lights
                    for device in self.active_lights:
                        self.__z2m_client.Light_Controls("Dim", device)
                    
                    #Stop Away Timer and go idle
                    self.__clock_away.Stop()
                    self.Go_Idle()
                
                #The Limit Threshold - System turns of the stove, if Away Timer exceeds limit threshold
                elif timer_state == "Limit":
                    print("\n------------------------------------LIMIT EXCEEDED!!!!!!!--------------------")
                    
                    #Turns off the Actuator if its on. Logs it to the database
                    if self.actuator_dict["State"] == "ON": 
                        self.System_Logger.logSystemTurnsStoveOff()
                        self.__z2m_client.Actuator_Controls("Actuator", "OFF")
                        
                        #Stops the Actuator Timer and sets its dictionary values
                        self.__clock_actuator.Stop()
                        self.actuator_dict["State"] = "OFF"
                        self.actuator_dict["PowerWasRegistered"] = False
                    
                    #Publish "Limit" state to all active lights
                    for device in self.active_lights:
                        self.__z2m_client.Light_Controls("Limit", device)    
                
                #The Notify Threshold - System starts notifying citizen, when the Away Timer exceeds Notify threshold
                elif timer_state == "Notify":
                    print("\n------------------------------------NOTIFY!!!!!!!--------------------")
                    
                    #Publish "Notify" state to all active lights
                    for device in self.active_lights:
                        self.__z2m_client.Light_Controls("Notify", device)
                        
                else:
                    #Else publish "On" state to all active lights
                    for device in self.active_lights:
                        self.__z2m_client.Light_Controls("On", device)
                        
            time.sleep(1)
        
        print("---------Away Timer Thread has been closed!---------")
    
    #Thread for Actuator Timer. To ensure that Actuator has time to update it power value when turned on by the system.
    #Used to optimize the certainty that the citizen turned off the stove.
    def Actuator_Timer(self):
        
        print("---------Actuator Thread has started!---------")
        #The Threads While-loop continues as long as the running flag is true
        while self.Actuator_Thread_Running:
            
            #If timer is active, thread checks if the stove is turned off by citizen. 
            #When detected it logs it, closes the threads, which then makes system go into idle mode through the Away Timer thread
            if self.__clock_actuator.Timer_Active:
                
                #If the timer exceeds 30 secs and power is still 0, system should recognize it as citizen has turned off the stove - go idle
                if self.actuator_dict["State"] == "ON" and self.actuator_dict["Power"] == 0 and self.__clock_actuator.Time_Now() >= self.__clock_actuator.Actuator_Threshold:
                    self.System_Logger.logStoveOff()
                    print("Citizen turned off the stove - after 30 sec")
                    self.__clock_actuator.Stop()
                    self.Go_Idle()

                    
                #If Power has been registered after actuator is turned on and power is 0. Then Citizen must have turned off the stove - go idle
                elif self.actuator_dict["State"] == "ON" and self.actuator_dict["Power"] == 0 and self.actuator_dict["PowerWasRegistered"] == True:
                    self.System_Logger.logStoveOff()
                    print("Citizen turned off the stove - before 30 sec")
                    self.__clock_actuator.Stop()
                    self.Go_Idle()
                
            time.sleep(1)
        
        print("---------Actuator Thread has been closed!---------")
    
    #This sets the occupancy in kitchen to true and the other rooms to false. This is used when kitchen is entered
    def Kitchen_Entered(self):
        """ 
            Method for when citizen enters kitchen. This logs that kitchen was entered, sets flag for citizen in_kitchen to true,
            sets room occupancy to only be true in kitchen, turns off all lights and assigns active lights as empty, and stops Away Timer
        """
        self.in_kitchen = True
        self.System_Logger.logCitizenEnteredKitchen()
        
        self.room_occupancy = {"Kitchen": True, "Room 1": False, "Room 2": False, "Room 3": False, "Room 4": False}
        
        #Turns off lights in all rooms, and sets active_lights list as empty
        for device in self.__device_model.lights_list:
            self.__z2m_client.Light_Controls("Off", device.id_)
        self.active_lights = []
            
        #Stop Away Timer
        self.__clock_away.Stop()
    
    #Handles the messages from the Z2M client
    def __zigbee2mqtt_event_received(self, message: Z2M_Message) -> None:
        """
        The Event Received in shape of a message. The Logic Controller handles the messages differently depending on the device type.

        Actuator Messages:  Saves the values received from actuator in the actuator dictionary
        Sensor Messages: #! #! DO THIS 
        """
        #Splits the topic string
        tokens = message.topic.split("/")
        if len(tokens) <= 1:
            return

        #the device_id is then tokens[1]
        device_id = tokens[1]
        device = self.__device_model.find(device_id)
        
        #Messages from Actuator - Extracts power and state from the actuator message
        if device in self.__device_model.actuators_list:
            try:
                power = message.power
                if power == None: 
                    power = 0
                state = message.state
            except KeyError:
                pass

            #Updates values in the actuator dictionary
            self.actuator_dict["State"] = state
            self.actuator_dict["Power"] = power
            
            #Checks if power registered when the actuator is switched on, after it has been switched off. 
            if self.actuator_dict["State"] == "ON" and self.actuator_dict["PowerWasRegistered"] == False and power > 0:
                self.actuator_dict["PowerWasRegistered"] = True
            
        #Messages from Sensors. Extracts occupancy from the sensor message and changes the room occupancy accordingly
        elif device in self.__device_model.sensors_list:
            try:
                occupancy = message.occupancy
            except KeyError:
                pass
            
            #The Room where the message was received from
            room = self.room_sensor[device_id]
            
            #Ensures occupancy in at least one room, if current room is the only room with occupancy, and its new occupancy value is false.
            if list(self.room_occupancy.values()).count(True) == 1 and self.room_occupancy[room] == True and occupancy == False:
                #Flags the room which is kept occupant
                self.occupancy_flag = room
            else:
                #Update room occupancy
                self.room_occupancy[room] = occupancy
                
                #If there is a Occupancy flag and the new message has occupancy true - Remove the flag, unless its the same room
                if isinstance(self.occupancy_flag, str) and occupancy == True:
                    if room != self.occupancy_flag:
                        self.room_occupancy[self.occupancy_flag] = False
                    self.occupancy_flag = None
            
            #Update the active lights list - depending on which rooms has Occupancy 
            if self.room_occupancy["Kitchen"] == False:
                for room in self.room_occupancy:
                        if room == "Kitchen":
                            continue
                        #Adds lights to active lights list
                        if self.room_occupancy[room] == True and (self.room_light[room] not in self.active_lights):
                            self.active_lights.append(self.room_light[room])
                        #Removes lights from active lights list
                        elif self.room_occupancy[room] == False and (self.room_light[room] in self.active_lights):
                            self.active_lights.remove(self.room_light[room])
                            self.__z2m_client.Light_Controls("Off", self.room_light[room]) #Sluk lys hvis rum ikke har occupancy
            
            print("Occupancy:", self.room_occupancy)
            
            #Kitchen detects occupancy and citizen was not in kitchen before. Citizen has then entered Kitchen.
            if self.room_occupancy["Kitchen"] == True and self.in_kitchen == False: 
                #Kitchen Entered and Calls Kitchen_Entered method to reset variables and lights
                self.Kitchen_Entered()
                
                #If Actuator is switched off, it is switched on again and system logs it. Actuator Timer starts
                if self.actuator_dict["State"] == "OFF":
                    self.actuator_dict["State"] = "ON"
                    self.__z2m_client.Actuator_Controls("Actuator", "ON")
                    self.System_Logger.logSystemTurnsStoveOn()
                    self.__clock_actuator.Start()
                    
            #Updates occupancy to false and Citizen was previously in kitchen. Citizen has then left Kitchen, system logs it and starts timer
            elif self.room_occupancy["Kitchen"] == False and self.in_kitchen == True:
                self.in_kitchen = False
                self.System_Logger.logCitizenLeftKitchen()
                self.__clock_away.Start()
