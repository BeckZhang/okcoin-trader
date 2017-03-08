#!/usr/bin/python
#-*-coding:utf8-*-

import socket
import time

if __name__=='__main__':
	num = 0
	buf = ''
	print 'message format: buy_amt_price or newprice'
	while True:
		buf = raw_input('input order msg: ')
		if buf == '':
			break
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(('localhost', 46587))
		sock.send(buf)
		print sock.recv(1024)
		sock.close()
		num += 1
	print num
