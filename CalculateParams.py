#!/usr/bin/python
#-*-coding:utf8-*-

from SqliteUtils import *
import time
from math import *
from utils import *

sql = 'select * from id_time_price where time%60=0;'
kFileName = 'id_time_price.db'

def MACD(close_list):
	diff = [0]
	dea = [0]
	ema12 = [close_list[0]]
	ema26 = [close_list[0]]
	bar = [0]
	for i in range(1,len(close_list)):
		ema12.append(ema12[i-1]*11.0/13.0 + close_list[i]*2.0/13.0)
		ema26.append(ema26[i-1]*25.0/27.0 + close_list[i]*2.0/27.0)
		diff.append(ema12[i]-ema26[i])
		dea.append(dea[i-1]*0.8+diff[i]*0.2)
		bar.append(2*(diff[i]-dea[i]))
	return diff, dea, bar, ema12, ema26

def MeanAndStd(num_list, p_list=0):
	n = len(num_list)
	if sum(p_list)==0 or len(p_list)==0:
		p_list = [1.0/n] * n
	else:
		sum_p = sum(p_list)
		for i in range(len(p_list)):
			p_list[i] = p_list[i]/sum_p
	mean = 0.0
	div = 0.0
	for i in range(len(num_list)):
		mean += num_list[i]*p_list[i]
	for i in range(len(num_list)):
		div += p_list[i]*((num_list[i]-mean)**2)
	std = sqrt(div)
	return mean, std

def CalcuBoll(symbol, ttype):
	data = GetKLine(symbol, ttype, 20)
	close_array = []
	vol_array = []
	for item in data:
		close_array.append(item[4])
		vol_array.append(item[5])
	mean, std = MeanAndStd(close_array, vol_array)
	return data, mean, std


def CalcuBollOld(DBFileName):
	t1 = int(time.time())
# 这种方法是取每分钟的末尾作为参考
	#sql = 'select * from id_time_price where time%%60=%d and time > %d' % (t1%60, t1-19*60-1)
# 以下这种方法是取每秒成交数据作为参考
	sql = 'select * from id_time_price where time > %d' % (t1-20*60)
	print sql
	fid = DBWriter(DBFileName)
	res = fid.GetResult(sql)
	#此时, res存的是int型的二维数组, 格式为:
# [(id, time, last_price),(id, time, last_price),...]
	old_time = res[0][1]
	old_price = res[0][2]
	price_list = []
	for item in res:
		if item[1] != old_time:
			price_list.append(old_price)
			old_time = item[1]
		old_price = item[2]
	price_list.append(res[-1][2])
	return MeanAndStd(price_list)

if __name__=='__main__':
	mean, std = CalcuBoll('btc_cny','1min')
	print mean
	print std
