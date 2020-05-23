import threading, time, datetime
from Meter import Meter
from PV_simulator import PV_simulator

# Get time frame from user
timeNow = datetime.datetime.now().time()
print("The time is now: "+str(timeNow)+"\nWhat time of day do you want to stop streaming from the Meter?"+
        "\n\tInput Format (HH:MM:SS):\n\t\tExample = 23:59:59 ")
timeToStop = raw_input("Enter stop time: ")
format = '%H:%M:%S'
timeToStop = datetime.datetime.strptime(timeToStop,format)
# Initialize, append and start threads
threads = []
PV_thread = PV_simulator()
meter_thread = Meter()
threads.append(meter_thread)
threads.append(PV_thread)
PV_thread.start()
meter_thread.start()
# Run loop until stop time is reached
while(True):
    timeNow = str(datetime.datetime.now().time()).split(".")[0]
    if timeToStop>=datetime.datetime.strptime(timeNow,format):
        time.sleep(1)
    else:
        meter_thread.proceed = False
        PV_thread.proceed = False
        for thread in threads:
            thread.join()
        break
