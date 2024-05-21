import time
from threading import Thread, Event

class Timer:
    def __init__(self):
        """
            Creates a Timer class.
            The Timer Class includes multiple thresholds
            
            For the Away Timer these are:
            The Notify threshold is set to 15 minutes after the start time
            The Limit Threshold is set to 20 minutes after the start time.
            The Upper Threshold is set to 60 minutes after the start time.
            
            The Actuator Timer has one threshold, Power Threshold is set to 30 seconds.
        """
        
        #Threshold Periods for Away Timer
        self.Notify_Period = 15 #15 * 60 for 15 minutes
        self.Limit_Period = 20 #20 * 60 for 20 minutes
        self.Upper_Period = 60  #60 * 60 for 60 minutes
        
        #Threshold Value for Actuator Timer
        self.Actuator_Period = 30 

        # Timer variables initialised to -1 to indicate that the timer is not running.
        self.Start_Time = -1
        self.Notify_Threshold = -1
        self.Limit_Threshold = -1
        self.Upper_Threshold = -1
        self.Actuator_Threshold = -1
        self.Timer_Active = False

    def Time_Now(self):
        """
            Returns the current time as an integer
        """

        return int(time.time())

    def Time_Passed(self):
        """ Returns time since the timer was started 
        """
        return self.Time_Now() - self.Start_Time

    def Start(self):
        """
            Start Timer:
            Assign Start_Time as the current time and updates the different thresholds,
            using the Start_Time and the Threshold Periods, and set Timer_Active as true.
        """

        self.Start_Time = self.Time_Now()
        self.Notify_Threshold = self.Start_Time + self.Notify_Period
        self.Limit_Threshold = self.Start_Time + self.Limit_Period
        self.Upper_Threshold = self.Start_Time + self.Upper_Period
        self.Actuator_Threshold = self.Start_Time + self.Actuator_Period
        self.Timer_Active = True
        
    def Stop(self):
        """
            Stops and resets the timer by setting values to -1 and set Timer_Active to False.
        """
        self.Start_Time = -1
        self.Notify_Threshold = -1
        self.Limit_Threshold = -1
        self.Upper_Threshold = -1
        self.Actuator_Threshold = -1
        self.Timer_Active = False

    def Check_Timer(self):
        """
            Checks the timer:
            Returns a timer state corresponding to the latest threshold that is exceeded. If no threshold is exceeded the timer state it "On" 
        """
        
        #Upper Threshold
        if(self.Time_Now() >= self.Upper_Threshold) and (self.Upper_Threshold != -1):
            # print("Upper Threshold exceeded", "\nCurrent time: ", self.Time_Now(), "\nUpper Threshold", self.Upper_Threshold)
            return "Upper"
        
        #Limit Threshold
        elif(self.Time_Now() >= self.Limit_Threshold) and (self.Limit_Threshold != -1):
            # print("Limit Threshold exceeded", "\nCurrent time: ", self.Time_Now(), "\nLimit Threshold", self.Limit_Threshold)
            return "Limit"
        
        #Notify Threshold
        elif(self.Time_Now() >= self.Notify_Threshold) and (self.Notify_Threshold != -1): 
            # print("Notify Threshold exceeded", "\nCurrent time: ", self.Time_Now(), "\nNotify Threshold", self.Notify_Threshold)
            return "Notify"
        
        return "On"

