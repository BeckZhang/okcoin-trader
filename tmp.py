#!/usr/bin/python
#-*-coding:utf8-*-

import os
from utils import *

def test1():
	conn = httplib.HTTPSConnection("www.okcoin.cn", timeout=10)
	while True:
		conn.request("GET", "/api/v1/ticker.do?symbol=%s"%('btc_cny'))
		response = conn.getresponse()
		res_str = response.read()
		data = StringToDict(res_str)
		print time.time()
		PrintData(data)
		time.sleep(0.5)
	return True

if __name__=='__main__':
	test1()
