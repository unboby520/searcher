#coding:utf8
'''
Created on 2013-10-21

@author: xiaobei
'''

import pika
import ujson as _json
import time

EXCHANGETYPE_FANOUT = 'fanout'
EXCHANGETYPE_DIRECT = 'direct'

#===============================================================================
# sender
#===============================================================================

class MQServer(object):
    def __init__(self, host):
        self.host = host
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                        host= host, port=5672))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)


    def sendMessage(self, exchange, message):
        try:
            self.channel.basic_publish(exchange=exchange,
                                       routing_key='',                                   
                                       body=message,
                                       properties=pika.BasicProperties(delivery_mode = 2)
                                       )
        except Exception as e:
            print 'pika closed'
            self.reconnect()
            self.channel.basic_publish(exchange=exchange,
                       routing_key='',                                   
                       body=message,
                       properties=pika.BasicProperties(delivery_mode = 2)
                       )
                

    def reconnect(self):
        self.stop()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                        host = self.host, port=5672))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)


    def stop(self):
        try:
            self.connection.close()
        except Exception as e:
            pass
        

#===============================================================================
# receiver 
#===============================================================================
class MQClientBase(object):
    def __init__(self, host, exchange, queue_name): 
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host = host, port=5672))
        self.channel = connection.channel()
        
        #self.channel.exchange_declare(exchange=exchange,
        #                              exchange_type=EXCHANGETYPE_FANOUT)

        self.queue_name = queue_name    
        #self.channel.queue_declare(queue=queue_name, exclusive=True)
        
        self.channel.queue_bind(
                                exchange=exchange,
                                queue=self.queue_name,
                                routing_key=''
                                )


    def callback(self, ch, method, properties, body):
        #
        print 'implemented in the concrete subclasses'


    def startConsume(self):
        self.channel.basic_consume(self.callback,
                              queue=self.queue_name,
                              no_ack=True)
        
        self.channel.start_consuming()    

