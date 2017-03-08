#!/usr/bin/python
#-*-coding:utf8-*-

import json
import httplib
import socket
import time
import os
import sys

def PrintData(data, indent=0, header = True):
	kIndent = 3
	if isinstance(data, list):
		if header:
			PrintData('[', indent)
		for i in range(len(data)):
			PrintData(data[i], indent)
		PrintData(']',indent)
	elif isinstance(data, dict):
		if header:
			PrintData('{', indent)
		for key in sorted(data.keys()):
			if isinstance(data[key], list):
				print ' '*indent, key,': ['
				PrintData(data[key], indent+kIndent, False)
			elif isinstance(data[key], dict):
				print ' '*indent, key,': {'
				PrintData(data[key], indent+kIndent, False)
			else:
				print ' '*indent, key, ':', data[key]
		PrintData('}',indent)
	else:
		print ' '*indent, data

# 二选一的flag
def BiSelection(flag, str1, str2):
	if flag == str1:
		return True
	elif flag == str2:
		return False
	else:
		print >> sys.stderr, 'Message Format Wrong!\nFORMAT: (%s), (%s)\nACTUAL: (%s)' % (str1, str2, flag)
		return None

def StringToDict(dic_str):
	dic = json.loads(dic_str)
	return dic

def RefreshLastPrice(symbol, conn=-174234):
	num = 0
	while True:
		try:
			close_flag = False
			if conn == -174234:
				close_flag = True
				conn = httplib.HTTPSConnection("www.okcoin.cn", timeout=10)
			conn.request("GET", "/api/v1/ticker.do?symbol=%s"%(symbol))
			response = conn.getresponse()
			res_str = response.read()
			if close_flag:
				conn.close()
			data = StringToDict(res_str)
			return data
		except Exception as e:
			print str(e)
			num += 1
		if num == 3:
			break
	return False

def RefreshLastPriceInternational(symbol, conn=-174234):
	num = 0
	while True:
		try:
			close_flag = False
			if conn == -174234:
				close_flag = True
				conn = httplib.HTTPSConnection("www.okcoin.cn", timeout=10)
			conn.request("GET", "/api/v1/ticker.do?symbol=%s"%(symbol))
			response = conn.getresponse()
			res_str = response.read()
			if close_flag:
				conn.close()
			data = StringToDict(res_str)
			return data
		except Exception as e:
			print str(e)
			num += 1
		if num == 3:
			break
	return False

def RefreshExchangeRatio():
	num = 0
	while True:
		try:
			conn = httplib.HTTPSConnection("www.okcoin.com", timeout=10)
			conn.request("GET", "/api/v1/exchange_rate.do")
			response = conn.getresponse()
			res_str = response.read()
			conn.close()
			data = StringToDict(res_str)
			return data
		except Exception as e:
			print str(e)
			num += 1
		if num == 3:
			break
	return False

def testkline():
	kline_data = GetKLine('btc_cny', '1min', 1)
	print kline_data[0][0], int(time.time())

def GetFutureKLine(symbol, ttype, size, contract_type, since=0):
	num = 0
	while True:
		try:
			ttime = int(time.time())
			conn = httplib.HTTPSConnection("www.okcoin.com", timeout=10)
			if since == 0:
				conn.request("GET", "/api/v1/future_kline.do?symbol=%s&type=%s&size=%d&contract_type=%s"%(symbol, ttype, int(size), contract_type))
			else:
				conn.request("GET", "/api/v1/future_kline.do?symbol=%s&type=%s&size=%d&since=%d&contract_type=%s"%(symbol, ttype, int(size), since, contract_type))
			response = conn.getresponse()
			res_str = response.read()
			conn.close()
			data = StringToDict(res_str)
			return data
		except Exception as e:
			print str(e)
			num += 1
		if num == 3:
			break
	return False


def GetKLine(symbol, ttype, size, station='cn',since=0):
	num = 0
	while True:
		try:
			ttime = int(time.time())
			conn = httplib.HTTPSConnection("www.okcoin.%s"%station, timeout=10)
			if since == 0:
				conn.request("GET", "/api/v1/kline.do?symbol=%s&type=%s&size=%d"%(symbol, ttype, int(size)))
			else:
				conn.request("GET", "/api/v1/kline.do?symbol=%s&type=%s&size=%d&since=%d"%(symbol, ttype, int(size), since))
			response = conn.getresponse()
			res_str = response.read()
			conn.close()
			data = StringToDict(res_str)
			return data
		except Exception as e:
			print str(e)
			num += 1
		if num == 3:
			break
	return False

def SendMessage(msg, port=46587):
	num = 0
	while True:
		try:
			num += 1
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect(('localhost', port))
			sock.send(msg)
			msg_recv = sock.recv(1024)
			sock.close()
			return msg_recv
		except Exception as e:
			print "SOCKET SEND MESSAGE ERROR:", str(e)
			if num == 3:
				print >> sys.stderr, "SOCKET SEND MESSAGE ERROR FOR 3 TIMES, Check network"
				return False
			continue

def WriteArrayIntoFile(_array, _file_name):
	os.system('rm %s' % (_file_name))
	fid = open(_file_name, 'w')
	for i in _array:
		fid.write(str(i)+'\n')
	fid.close()
	return True

def MACDBoundary(ema26, ema12, dea):
	return (25.0*ema26/27.0 - 11.0*ema12/13.0+dea)/(2.0/13.0 - 2.0/27.0)

def CurrentMACDBar(old_ema26, old_ema12, old_dea, last_price):
	ema12 = old_ema12*11.0/13.0 + last_price*2.0/13.0
	ema26 = old_ema26*25.0/27.0 + last_price*2.0/27.0
	diff = ema12 - ema26
	dea = old_dea*0.8 + diff*0.2
	return 2*(diff - dea)

if __name__=='__main__':
	testkline()
