#!/usr/bin/python
#-*-coding:utf8-*-

import time

from SqliteUtils import *

dbwriter = DBWriter('kline_okcoin.db')
while True:
	res = dbwriter.GetOneResult('select * from kline_1min order by id desc')
	print res
	print int(time.time())
	time.sleep(1)
