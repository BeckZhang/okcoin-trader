#!/usr/bin/python
#-*-coding:utf8-*-

from utils import *

data = GetKLine('btc_cny', '1min', 10000)
kline_time = []
kline_open = []
kline_high = []
kline_low = []
kline_close = []
kline_vol = []
for item in data:
	kline_time.append(int(item[0])/1000)
	kline_open.append(float(item[1]))
	kline_high.append(float(item[2]))
	kline_low.append(float(item[3]))
	kline_close.append(float(item[4]))
	kline_vol.append(float(item[5]))

WriteArrayIntoFile(kline_time, 'matlab_files/ktime.txt')
WriteArrayIntoFile(kline_open, 'matlab_files/kopen.txt')
WriteArrayIntoFile(kline_high, 'matlab_files/khigh.txt')
WriteArrayIntoFile(kline_low, 'matlab_files/klow.txt')
WriteArrayIntoFile(kline_close, 'matlab_files/kclose.txt')
WriteArrayIntoFile(kline_vol, 'matlab_files/kvol.txt')
