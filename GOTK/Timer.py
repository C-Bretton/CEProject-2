import time
from threading import Thread, Event

class Timer:
    def __init__(self):
        """
            Creates a timer class.
            The notify threshold is set to 15 minutes after the current time.
            The time limit is set to 20 minutes after the current time.

            To start the timer, use the start() fucntion.
        """
        # Timer values
        self.notify_period = 30  #15 * 60
        self.time_limit_period = 60  #20 * 60
        self.super_time_limit_period = 120  #60 * 60 #!
        self.power_timer = 30 # 60 

        # Timer variables, set to -1 to indicate that the timer is not running.
        self.start_time = -1
        self.notify_threshold = -1
        self.time_limit = -1
        self.super_time_limit = -1
        self.timer_active = False
        
        # Thread for checking the timer
        #self.thread = Thread(target = self.check_timer(), daemon = True)

    def time_now(self):

        return int(time.time())

    def start(self):
        """
            Creates an "away-from_kitchen"-timer from the current time.
            Starts the thread that checks the timer.
        """

        self.start_time = int(time.time())
        self.notify_threshold = self.start_time + self.notify_period
        self.time_limit = self.start_time + self.time_limit_period
        self.super_time_limit = self.start_time + self.super_time_limit_period
        
        self.timer_active = True
   

    def reset(self):
        """
            Resets the timer by setting values to -1.
        """
        self.start_time = -1
        self.notify_threshold = -1
        self.time_limit = -1
        self.super_time_limit = -1
        self.timer_active = False


    #Cant the two following methods be merged into one????

    def notify(self) -> bool:
        """
            Call this function to check if the notification threshold has been reached.
            If so, it does "something"
        """

        if(int(time.time()) >= self.notify_threshold) and (self.notify_threshold != -1):
            # send signal to blink lamp
            print("these are the notify times: ", int(time.time()), self.notify_threshold)
            return True
        else:
            return False

    def limit_exceeded(self) -> bool:
        """
            Call this function to check if the time limit has been exceeded.
            If so, it does "something".
        """
        if(int(time.time()) >= self.time_limit) and (self.time_limit != -1):
            # send signal to turn off stove
            print("these are the limit_exceeded times: ", int(time.time()), self.time_limit)
            return True
        else:
            return False
    
    def super_limit(self) -> bool:
        """
            Call this function to check if the super time limit has been exceeded.
            If so, it does "something".
        """
        if(int(time.time()) >= self.super_time_limit) and (self.super_time_limit != -1):
            # send signal to turn off stove
            print("The super limit times: ", int(time.time()), self.super_time_limit)
            return True
        else:
            return False
    
    
    def stop(self):
        """
            Stops the timer when time limit is exceeded.
            Resets the timer and makes the thread stop checking the timer.
        """
        self.reset()
        self.timer_active = False


    def check_timer(self):
        """
            Checks the timer every ???. return values 0, nothing, 1 notify, 2 limit exceeded
        """
        #this loops runs forever and doesnt run client concurrently
        # while True:
        
        if self.super_limit():
            print("Upper Limit exceeded")
            self.stop()
            return "Upper"
        
        elif(self.limit_exceeded()):
            print("Limit exceeded")
            return "Limit"
        
        elif(self.notify()):
            print("bruh notify")
            return "Notify"
        
        return "Normal"
