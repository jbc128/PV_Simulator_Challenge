import threading, pika, random, time


class Meter(threading.Thread):
    def __init__(self):
        self.proceed = True
        super(Meter, self).__init__()

    # All function calls are made in run()
    def run(self):
        self.setupMQ()
        self.publishWatts()

    # Sets up RabbitMQ connection, channel and queue
    def setupMQ(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='meterStream')

    # Sends RabbitMQ messages containing a watt value
    def publishWatts(self):
        while(self.proceed):
            watts = random.randint(0,9000)
            self.channel.basic_publish(exchange='', routing_key='meterStream', body=str(watts))
        self.channel.basic_publish(exchange='', routing_key='meterStream', body="end")
        self.connection.close()
