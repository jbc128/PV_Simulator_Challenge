import threading, pika, datetime, time


class PV_simulator(threading.Thread):
    def __init__(self):
        self.proceed = True
        self.body = []
        self.threads = []
        super(PV_simulator, self).__init__()

    def run(self):
        self.setupMQ()
        # Sends a thread to consume all messages on the queue
        self.consumeMeter_thread = threading.Thread(target= self.consumeMeterStream)
        self.threads.append(self.consumeMeter_thread)
        self.consumeMeter_thread.start()
        self.processBody()

    # Sets up RabbitMQ connection, channel and queue
    def setupMQ(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='meterStream')

    # Executes every time a message is put on the queue
    def callback(self, ch, method, properties, body):
        # If an "end" is received, then stop consuming and close connection
        if body == "end":
            self.connection.close()
            return
        # Only pull Meter value every couple of seconds, the rest of the messages are dropped
        timeDifference = datetime.datetime.now() - self.timeA
        self.timeStamp = datetime.datetime.now().time()
        daySeconds = 24*60*60
        secondsDifference = divmod(timeDifference.days * daySeconds + timeDifference.seconds, 60)
        if int(secondsDifference[1])>=2:
            self.timeA = datetime.datetime.now()
            self.body.append(body)

    # child thread consumes all messages on the queue
    def consumeMeterStream(self):
        self.channel.basic_consume(
            queue='meterStream', on_message_callback=self.callback, auto_ack=True)
        self.timeA = datetime.datetime.now()
        self.channel.start_consuming()

    # When a Meter value is pulled, put it on a child thread to carry on
    # This function runs until self.proceed is False and there are no more pulled values
    def processBody(self):
        while(True):
            if self.proceed==False and len(self.body)<=0:
                self.exitGracefully()
                return
            elif (len(self.body)>0):
                self. buildOutput_thread = threading.Thread(target= self.buildOutput)
                self.threads.append(self.buildOutput_thread)
                self.buildOutput_thread.body = self.body.pop(0)
                self.buildOutput_thread.start()
            time.sleep(1.5)

    # Threads holding Meter values will assemble variables needed in Output file
    def buildOutput(self):
        meterWatts = int(self.buildOutput_thread.body)
        meterkW = float(meterWatts/1000.0)
        self.getPVpower()
        PVpower = self.buildOutput_thread.PVpower
        timeStamp = self.buildOutput_thread.timeStamp
        combinedPower = (meterkW + PVpower)
        self.pushOutput(meterWatts,PVpower,timeStamp,combinedPower)

    # Convert the time into a number so it can be used as an X to find Y values for PV formula
    def getPVpower(self):
        self.buildOutput_thread.timeStamp = self.timeStamp
        hours = self.buildOutput_thread.timeStamp.hour
        minutes = self.buildOutput_thread.timeStamp.minute
        seconds = self.buildOutput_thread.timeStamp.second
        timeConverted = (hours + (float((minutes*60)+seconds)/3600.0))
        self.findTimePeriod(timeConverted)

    # Assign PV values based on the output curve given in the challenge
    def findTimePeriod(self, timeConverted):
        # If time is between 12am and 5:50am or 9pm and 24 (24 will never be reached)
        if 0.0<timeConverted<=5.83333333333 or 21.0<timeConverted<=24:
            self.buildOutput_thread.PVpower = 0.0
        # If time is between 5:50 and 8am
        elif 5.83333333333<timeConverted<=8.0:
            # Linear line formula
            self.buildOutput_thread.PVpower = ((0.16154*timeConverted)-0.9423)
        # If time is between 8am and 2pm
        elif 8.0<timeConverted<=14.0:
            # Parabula formula
            self.buildOutput_thread.PVpower = ((-0.0806*((timeConverted-14.0)**2))+3.25)
        # If time is between 2pm and 8pm
        elif 14.0<timeConverted<=20.0:
            # Parabula formula
            self.buildOutput_thread.PVpower = ((-0.08472*((timeConverted-14.0)**2))+3.25)
        # If time is between 8pm and 9pm
        elif 20.0<timeConverted<=21.0:
            # Linear line formula
            self.buildOutput_thread.PVpower = ((-0.2*timeConverted)+4.2)

    # Write data to file then close
    def pushOutput(self,meterWatts,PVpower,timeStamp,combinedPower):
        output_file = open("Output.txt","a+")
        output_file.write("TimeStamp: "+str(timeStamp)+" , Meter power value: "+str(meterWatts) +
            " Watts , Photovoltaic power value: "+str(PVpower)+ " kW , Combined power (meter + PV): "+str(combinedPower)+" kW\n")
        output_file.close()

    # Called before exit
    def exitGracefully(self):
        for thread in self.threads:
            thread.join()
