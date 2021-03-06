#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64, json, time, datetime, pika
import Constant as cons
import sys, os, inspect
pathapp = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(pathapp + "/config")
sys.path.append(pathapp + "/util")

import Prop as env
import rabbitmq as rabbit
import mongodb as mongo


class Worker(object):
	
	def __init__(self):
		self.credentials = pika.PlainCredentials(env.RABBIT_USER, env.RABBIT_PASS)
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(env.RABBIT_HOST, env.RABBIT_PORT, env.RABBIT_VHOST, self.credentials))
		self.channel = self.connection.channel()

	# Send task to queue rabbitmq
	def publisher(self):
		self.msg = {
			'eid' : 1,
			'action' : 'action something',
			'data' : 'Data something'
		}
		self.message = json.dumps(self.msg)
		print self.message
		rabbit.RabbitMQ().send_data(cons.key_queue_send, self.message)
	
	def consumer(self):
		self.channel.queue_declare(cons.key_queue_send)
		print "[*] Waiting for messages. To exit press CTRL+C"

		self.channel.basic_qos(prefetch_count = 1)
		# Callback method action queue
		self.channel.basic_consume(actionqueue, queue = cons.key_queue_send)
		self.channel.start_consuming()

# Action queue from rabbitmq
def actionqueue(ch, method, properties, body):
		print '\nCrawl send content to rabbitmq beforafter save'
		print " Received %r" % (body)
		print '[*] Start action Taks'
		data = json.loads(body)
		mongo.MongoDb().insert('collection_name', data)
                print '[*] Saved data into mongo db'
		print '[*] End action Taks'
		ch.basic_ack(delivery_tag = method.delivery_tag)
