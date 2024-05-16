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
    The logic controller is the driver for the GOTK system. It controls when the system listens to messages or not
    and also holds the logic that actuates based on messages receives from the Z2M_client
    """

    HTTP_HOST = "http://localhost:8000"
    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883


    def __init__(self, device_model: DeviceModel) -> None:
        """
        
        """
        self.__device_model = device_model
        self.__z2m_client = Z2M_Client(host = self.MQTT_BROKER_HOST,
                                       port = self.MQTT_BROKER_PORT,
                                       on_message_callback=self.__zigbee2mqtt_event_received)
        
        self.System_Logger = Logger()
        self.__clock = Timer()
        self.__clock_actuator = Timer()
        
        self.room_dict = {"Sensor 0": "Kitchen", "Sensor 1": "Room 1", "Sensor 2": "Room 2", "Sensor 3": "Room 3", "Sensor 4": "Room 4"} #!use to reference sensors to which room
        
        self.room_light = {"Room 1": "Bulb 1", "Room 2": "Bulb 2", "Room 3": "Bulb 3", "Room 4": "Bulb 4"}

        self.active_lights = []
        
        self.room_occupancy = {}
        
        self.actuator_dict = {}
        
        self.occupancy_flag = None
        
        
    def Set_Occupancy(self):
        
        for device in self.__device_model.sensors_list:
            print(device)
            room = self.room_dict[device.id_]
            
            if room == "Kitchen":
                self.room_occupancy[room] = True
            else:
                self.room_occupancy[room] = False


    def Start_System(self) -> None:
        """
        Starts listening to zigbee2mqtt messages
        """
        print("System started")
        self.__z2m_client.connect()
        
        self.IS_RUNNING = True
        
        self.in_kitchen = True
        
        self.actuator_dict["State"] = "ON"
        self.actuator_dict["Power"] = 10 #Has to be atleast 10 to start system.
        self.actuator_dict["PowerWasRegistered"] = True
        
        # print(self.__device_model.lights_list)
        for device in self.__device_model.lights_list:
            self.__z2m_client.Light_Control("Off", device.id_) #To make sure all lights starts in "OFF" mode
        
        self.Set_Occupancy() #Set Occupancy
        
        print("-----------------------START THREAD--------------------------")
        
        self.__timer_thread = Thread(target = self.CHECKTHATTIMER, daemon = True) #To make sure we dont try to start the same thread again, as it is Not Allowed to start it more than once
        self.__stoveoff_thread = Thread(target = self.TIMER_ACTUATOR, daemon = True)
        
        self.thread_running = True
        self.__timer_thread.start()
        
        self.__clock_actuator.start()
        self.stove_thread_running = True
        self.__stoveoff_thread.start()

    #Rename go idle
    def Terminate_System(self) -> None:
        """
        Stops listening to zigbee2mqtt messages
        """

        print("Terminate system is called")
        self.__z2m_client.disconnect()
            
        print("Client is disconnected")
        self.IS_RUNNING = False
    
    
    def CHECKTHATTIMER(self):
        
        print("---------Timer Thread has started!---------")
        while self.thread_running:

            if self.__clock.timer_active:
                print("\n------------- Timer is:", self.__clock.time_now() - self.__clock.start_time, "-------------")
                timer_state = self.__clock.check_timer()
                    
                print("These are active lights:", self.active_lights)
                print("Current Occupancy:", self.room_occupancy)
                    
                if timer_state == "Upper":
                    print("\n------------------------------------UPPER LIMIT EXCEEDED!!!!!!!--------------------")
                    
                    for device in self.active_lights:
                        self.__z2m_client.Light_Control("Shutdown", device)

                    self.stove_thread_running = False
                    self.thread_running = False #This stops the thread loop
                    print("\nthread_running has been set to False and will stop running!!!\n")
                    
                elif timer_state == "Limit":
                    print("\n------------------------------------LIMIT EXCEEDED!!!!!!!--------------------")
                    
                    if self.actuator_dict["State"] == "ON":
                        self.System_Logger.logSystemTurnsStoveOff()
                        self.__z2m_client.Actuator_Controls("Actuator", "OFF")
                        
                        self.__clock_actuator.reset()
                        self.actuator_dict["State"] = "OFF"
                        self.actuator_dict["PowerWasRegistered"] = False
                        # print("This is power registered - Actuator is turned off by system: ", self.actuator_dict["PowerWasRegistered"], "\n")
                            
                    for device in self.active_lights:
                        self.__z2m_client.Light_Control("Limit", device)    
                    
                elif timer_state == "Notify":
                    print("\n------------------------------------NOTIFY!!!!!!!--------------------")
                        
                    for device in self.active_lights:
                        self.__z2m_client.Light_Control("Notify", device)
                        
                else:
                    for device in self.active_lights:
                        self.__z2m_client.Light_Control("On", device)
                        
                
            time.sleep(1)
        
        print("---------Timer Thread loop has been exited!---------")
        print("Test: Terminate system")
        self.Terminate_System() #! move this up to timer upper???? in case turned of by citizen then this will be done twice? + prints
    
    def TIMER_ACTUATOR(self):
        
        print("---------Stove Thread has started!---------")
        while self.stove_thread_running:
            
            if self.__clock_actuator.timer_active:
                print("----- this is actuator timer ----", self.__clock_actuator.time_now() - self.__clock_actuator.start_time)
                print("Power:", self.actuator_dict["Power"])
                print("State:", self.actuator_dict["State"])
                print("PowerWasRegistered:", self.actuator_dict["PowerWasRegistered"])
                
                if self.actuator_dict["State"] == "ON" and self.actuator_dict["Power"] == 0 and self.__clock_actuator.time_now() >= self.__clock_actuator.start_time + self.__clock_actuator.power_timer:
                    self.System_Logger.logStoveOff()
                    print("Citizen turned off the stove - after 30 sec")
                    self.stove_thread_running = False
                    self.thread_running = False
                    self.__clock_actuator.reset()
                elif self.actuator_dict["State"] == "ON" and self.actuator_dict["Power"] == 0 and self.actuator_dict["PowerWasRegistered"] == True: #!maybe set timer or sleep
                    self.System_Logger.logStoveOff()
                    print("Citizen turned off the stove - before 30 sec")
                    self.stove_thread_running = False
                    self.thread_running = False
                    self.__clock_actuator.reset()
                
            time.sleep(1) #!higher value?
        
        print("---------Stove Thread loop has been exited!---------")
        
        
    def __zigbee2mqtt_event_received(self, message: Z2M_Message) -> None:
        """
        Logic that drives the GOTK system
        """
        
        tokens = message.topic.split("/")
        if len(tokens) <= 1:
            return
        
        # print(tokens)
        
        device_id = tokens[1]

        # print(device_id)

        device = self.__device_model.find(device_id)
        
        
        if device in self.__device_model.actuators_list:
            try:
                power = message.power
                if power == None: 
                    power = 0
                state = message.state
            except KeyError:
                pass
            
            print("Actuator change detected", device_id)
            print("Power detected:", power)
            print("State:", state)
            print("PowerWasRegistered:", self.actuator_dict["PowerWasRegistered"])

            self.actuator_dict["State"] = state
            self.actuator_dict["Power"] = power

            if self.actuator_dict["State"] == "ON" and self.actuator_dict["PowerWasRegistered"] == False and power > 0:
                self.actuator_dict["PowerWasRegistered"] = True
                # print("This is power registered - after false and power larger than 0: ", self.actuator_dict["PowerWasRegistered"])
            
            
        if device in self.__device_model.sensors_list:
            try:
                occupancy = message.occupancy
            except KeyError:
                pass
            
            room = self.room_dict[device_id]
            
            # print("Count how many true occupancy", list(self.room_occupancy.values()).count(True), "\nThis is list:", self.room_occupancy)
            #! This is to make sure there is always one room with occupancy 
            if list(self.room_occupancy.values()).count(True) == 1 and self.room_occupancy[room] == True and occupancy == False:
                # print("Only this room occupied, so keep it true - Room:", room)
                self.occupancy_flag = room #!flag the room which is kept true
            
            else:
                self.room_occupancy[room] = occupancy
                
                #!remove flagged room to false here if occupancy is found elsewhere - if occupancy in flagged room it just removes flag
                if isinstance(self.occupancy_flag, str) and occupancy == True:
                    if room != self.occupancy_flag:
                        self.room_occupancy[self.occupancy_flag] = False
                    self.occupancy_flag = None
            
            
            #!Add and remove from active lights
            for room in self.room_occupancy:
                    if room == "Kitchen":
                        continue
                    if self.room_occupancy[room] == True and (self.room_light[room] not in self.active_lights):
                        self.active_lights.append(self.room_light[room])
                        # self.__z2m_client.Light_Control("On", self.room_light[room])
                    elif self.room_occupancy[room] == False and (self.room_light[room] in self.active_lights):
                        self.active_lights.remove(self.room_light[room])
                        self.__z2m_client.Light_Control("Off", self.room_light[room]) #Sluk lys hvis rum ikke har occupancy
                        
            
            print("Current Occupancy:", self.room_occupancy)
            
            if self.room_occupancy["Kitchen"] == True and self.in_kitchen == False: 
                self.in_kitchen = True
                self.System_Logger.logCitizenEnteredKitchen()
                
                self.Set_Occupancy() #! Reset list - If all sensors went false, then last occupied room is still true, but wont update as there is no message from it.
                
                if self.actuator_dict["State"] == "OFF":
                    self.actuator_dict["State"] = "ON"
                    self.__z2m_client.Actuator_Controls("Actuator", "ON")
                    self.System_Logger.logSystemTurnsStoveOn()
                    self.__clock_actuator.start()

                for device in self.__device_model.lights_list:
                    self.__z2m_client.Light_Control("Off", device.id_)
                    
                print("\nTime when enter kitchen:", self.__clock.time_now() - self.__clock.start_time)
                self.__clock.reset()
            
            
            if self.room_occupancy["Kitchen"] == False and self.in_kitchen == True:
                self.in_kitchen = False
                self.System_Logger.logCitizenLeftKitchen()
                
                print("Citizen has left Kitchen:", device_id)
                self.__clock.start()
