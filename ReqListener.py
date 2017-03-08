#!/usr/bin/python
#-*-coding:utf8-*-

import urllib2
import json
import time
import sys
import threading
import socket
import os
from OKTrader import *
from utils import *
from SqliteUtils import *
from CalculateParams import *
from OkcoinInfos import *
from DataRecorder import *


kListenTime = 5
kOrderWaitTime = 7

class ReqListener():
	def __init__(self, api_key, api_secret, symbol, port, station='cn'):
#这里, port是指监听端口
		self.trader = OKTrader(api_key, api_secret, symbol, station)
		self.port = port
		return None

	def ParseSocketInfo(self, msg):
		"""
		格式为: buy_amt_price
		"""
		cols = msg.split('_')
		bsflag = cols[0]
		amt = float(cols[1])
		price = float(cols[2])
		return bsflag, amt, price
	
	def thread_func(self, order_id):
		time.sleep(kOrderWaitTime)
		self.trader.cancel_order(order_id)
		return True

#TODO: 还有一些

	def ProcessSocketInfo(self, msg):
		bsflag, amt, price = self.ParseSocketInfo(msg)
		order_id = self.trader.trade(bsflag, price, amt)
		t = threading.Thread(target=self.thread_func, args=(order_id,))
		t.setDaemon(True)
		t.start()
		return str(order_id)

	def Run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(('localhost', self.port))
		sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		sock.listen(kListenTime)
		while True:
#			1print 'waiting connection...'
			connection, address = sock.accept()
#			print 'connection accepted from address:', address
			try:
				connection.settimeout(kListenTime)
				msg = connection.recv(1024)
				msg_back = self.ProcessSocketInfo(msg)
				connection.send(msg_back)
			except socket.timeout:
				print 'time out'
			connection.close()

if __name__=='__main__':
	listener = ReqListener(kApiKey, kSecretKey, 'btc_cny', 46587)
	data_recorder = DataRecorder(kLineDBFileName, 'btc_cny')
	t1 = threading.Thread(target=listener.Run)
	t1.setDaemon(True)
	t1.start()
	data_recorder.Run()
