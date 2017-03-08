#!/usr/bin/python
#-*-coding:utf8-*-

from utils import *
from OkcoinInfos import *
import OKTrader
from CalculateParams import *

def btc_vs_ltc():
	btc_cn = GetKLine('btc_cny', '1min', 2880)
	ltc_cn = GetKLine('ltc_cny', '1min', 2880)
	for item in ltc_cn:
		print '%d \t%f \t%F \t%f \t%f \t%f' % (item[0], item[1], item[2], item[3], item[4], item[5])

def spot_vs_future():
	btc_spot = GetKLine('btc_cny', '1min', 2880)
	btc_future = GetFutureKLine('btc_usd', '1min', 2880, 'this_week')
	for item in btc_spot:
		print '%d \t%f \t%F \t%f \t%f \t%f' % (item[0], item[1], item[2], item[3], item[4], item[5])

def this_vs_next_week():
	this_week = GetFutureKLine('btc_usd', '1min', 2880, 'this_week')
	next_week = GetFutureKLine('btc_usd', '1min', 2880, 'next_week')
	for item in this_week:
		print '%d \t%f \t%F \t%f \t%f \t%f' % (item[0], item[1], item[2], item[3], item[4], item[5])

def Speculate():
	btc_cn_price = []
	btc_com_price = []
	ltc_cn_price = []
	ltc_com_price = []
	exch_rate = []

	while True:
		data1 = RefreshLastPrice('btc_cny')
		data2 = RefreshLastPriceInternational('btc_usd')

		data3 = RefreshLastPrice('ltc_cny')
		data4 = RefreshLastPriceInternational('ltc_usd')

		rate = RefreshExchangeRatio()
		btc_cn_price.append(float(data1['ticker']['last']))
		btc_com_price.append(float(data2['ticker']['last']))
		ltc_cn_price.append(float(data3['ticker']['last']))
		ltc_com_price.append(float(data4['ticker']['last']))
		exch_rate.append(float(rate['rate']))

		print 'BTC: cn/com: %.4f\tLTC: cn/com: %.4f\tRMB/USD: %.4f' % (btc_cn_price[-1]/btc_com_price[-1], ltc_cn_price[-1]/ltc_com_price[-1], exch_rate[-1])
	WriteArrayIntoFile(btc_cn_price, 'matlab_files/btc_cn_price.txt')
	WriteArrayIntoFile(btc_com_price, 'matlab_files/btc_com_price.txt')
	WriteArrayIntoFile(ltc_com_price, 'matlab_files/ltc_com_price.txt')
	WriteArrayIntoFile(ltc_cn_price, 'matlab_files/ltc_cn_price.txt')
	WriteArrayIntoFile(exch_rate, 'matlab_files/exch_rate.txt')

	return btc_cn_price, btc_com_price, ltc_cn_price, ltc_com_price, exch_rate

def TestMACD(file_name):
	fid = open(file_name, 'r')
	close_list = []
	for item in fid.readlines():
		close_list.append(float(item))
	fid.close()
	diff, dea, bar, ema12, ema26 = MACD(close_list)
	WriteArrayIntoFile(diff, 'matlab_files/diff.txt')
	WriteArrayIntoFile(dea, 'matlab_files/dea.txt')
	WriteArrayIntoFile(bar, 'matlab_files/bar.txt')
	return True

def GetBtcLtcTicker():
	conn = httplib.HTTPSConnection("www.okcoin.cn", timeout=10)
	while True:
		data = RefreshLastPrice('btc_cny', conn)
		btc_price = data['ticker']['last']
		data = RefreshLastPrice('ltc_cny', conn)
		ltc_price = data['ticker']['last']
		time_int = int(time.time())
		print time_int, btc_price, ltc_price
		time.sleep(0.8)

if __name__ == '__main__':
	GetBtcLtcTicker()
