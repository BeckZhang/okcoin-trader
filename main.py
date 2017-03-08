#!/usr/bin/python
#-*-coding:utf8-*-

import urllib2
import httplib
import time
import os
import sys
import socket
from CalculateParams import *
from OkcoinInfos import *
from SqliteUtils import *
from utils import *
from OKTrader import *

sys_time = 0
last_price = 0
stage = 0 # 持仓的等级为 0,1,2,3,4, 分别代表有i/4的钱买成比特币了

class BollinMACD():
	def __init__(self, DBFileName):
		self.max_stage = 4
		self.db_file_name = DBFileName
		self.dbreader = DBWriter(DBFileName)
		self.ema12 = 0
		self.ema26 = 0
		self.dea = 0
		self.diff = 0
		self.bar = []
		self.boll_mean = 0
		self.boll_std = 0
		self.last_price = 0
		self.sys_time = 0
		self.stage = 0
		self.frozen_stage = 0
		self.oktrader = OKTrader(kApiKey, kSecretKey, 'btc_cny') 
		self.stop_trade_time = 0
		self.stop_macd = False
		self.macd_redgreen_bound = 0 #这个变量表示价格和macd的红绿交叉点. 如果收盘时超过这个点, 则macd是绿的, 如果收盘时低于这个值, 则macd是红的
		self.continous_red = 0
		self.conn = httplib.HTTPSConnection("www.okcoin.cn", timeout=10)
		self.current_bar = 0
		return None

	def RefreshMacdAndBoll(self):
		kline_time = 0
		while True:
			data = self.dbreader.GetResult("select * from %s where time>=%d order by id desc" % (kTableName, int(time.time() - 23*60)))
			kline_time = int(data[0][1])
			print kline_time, int(time.time())
			if kline_time - int(time.time()) > -50:
				break
			time.sleep(0.2)
		self.ema12 = float(data[0][6])
		self.ema26 = float(data[0][7])
		self.dea = float(data[0][8])
		self.macd_redgreen_bound = MACDBoundary(self.ema26, self.ema12, self.dea)
		self.diff = self.ema12 - self.ema26
		self.bar.append(2*(self.diff - self.dea))
		if len(self.bar) == 101:
			del self.bar[0]

		#如果上一步是绿, 就把变量continous_red减一, 如果上一步是红, 就把变量continous_red加一, 然后打印出来
		if self.bar[-1] > 0:
			self.continous_red -= 1
		elif self.bar[-1] < 0:
			self.continous_red += 1
		print 'continous_red value:', self.continous_red 
		#end

		close_array = []
		vol_array = []
		for i in range(20):
			close_array.append(float(data[i][4]))
			vol_array.append(float(data[i][5]))
		self.boll_mean, self.boll_std = MeanAndStd(close_array, vol_array) 
		self.PrintMACDandBoll()
		return True

	def PrintMACDandBoll(self):
		print ''
		print 'DIFF:%.3f\tDEA:%.3f\tBAR:%.3f\tBOLL_MEAN:%.3f\tBOLL_STD:%.3f' % (self.diff, self.dea, self.bar[-1], self.boll_mean, self.boll_std)
		return None

	def RefreshPrice(self):
		global last_price
		while True:
			ticker_res = RefreshLastPrice('btc_cny', self.conn)
			if ticker_res == False:
				continue
			else:
				break
		self.last_price = float(ticker_res['ticker']['last'])
		self.sys_time = int(ticker_res['date'])
		last_price = self.last_price
		
		#判断此时continous_red是否要归零
		if self.continous_red>0 and self.last_price>self.macd_redgreen_bound:
			self.continous_red = 0
		if self.continous_red<0 and self.last_price<self.macd_redgreen_bound:
			self.continous_red = 0

		#更新current_bar
		self.current_bar = CurrentMACDBar(self.ema26, self.ema12, self.dea, self.last_price)
		return True

	def MACDSpeedDown(self):
		"""该函数用于判断macd红柱是否形成了加速向下趋势
		判断标准如下:
		continous_red >= 3
		(bar[-1]-bar[-2]) <0
		(bar[-2]-bar[-3]) <0
		(bar[-1]-bar[-2]) < (bar[-2]-bar[-3])
		current_bar < bar[-1]
		"""
		if self.continous_red<0:
			return False
		if not ((self.bar[-1] - self.bar[-2]) < 0):
			return False
		if not ((self.bar[-2] - self.bar[-3]) < 0):
			return False
		if not ((self.bar[-1]-self.bar[-2]) < (self.bar[-2]-self.bar[-3])):
			return False
		if not (self.current_bar < self.bar[-1]):
			return False
		return True

	def NeedTrade(self):
		"""该函数返回交易信号: 
			0:	不交易
			1:	正常买入
		   -1:	正常卖出
			2:	满仓
		   -2:	清仓
		"""
		if self.continous_red>=0 and self.continous_red<=2:
			return 0
		if time.time() < self.stop_trade_time:
			return 0
		if self.MACDSpeedDown():
			return 0
		if self.last_price < self.boll_mean - 1.9*self.boll_std and self.stage<self.max_stage:
			return 1
		elif self.last_price > self.boll_mean + 1.9*self.boll_std and self.stage>0:
			return -1
		else:
			return 0

	def Trade(self, nt):
		if nt == -1:
			res = SendMessage('sell_%f_%f' % (self.position/self.stage, self.last_price-0.04))
			if res != False:
				self.frozen_stage = -1
				return res
		if nt == 1:
			print 'self.cash=',self.cash
			print 'self.stage=', self.stage
			print 'last_price=', self.last_price
			res = SendMessage('buy_%f_%f' % ((self.cash-1)/((self.max_stage-self.stage)*(self.last_price+0.04)), self.last_price+0.04))
			if res != False:
				self.frozen_stage = 1
				return res
		return False

	def RefreshUserInfo(self):
		num = 0
		while True:
			try:
				user_info = self.oktrader.check_user_info()
				break
			except Exception as e:
				print 'ERROR while checking user info', str(e)
				num += 1
				if num == 3:
					user_info = None
					break
				continue
		cash = user_info['info']['funds']['free']['cny']
		position = user_info['info']['funds']['free']['btc']
		self.cash = float(cash)
		self.position = float(position)
		return True

	def CommitStage(self, flag):
		"""
		用于查看成交之后的确认, 
		如果成交了, flag给True, 该函数把变化了的stage加到self.stage上
		如果没成交, 就把frozen_stage归零
		"""
		if flag:
			self.stage += self.frozen_stage
		self.frozen_stage = 0
		return True

	def Run(self):
		self.RefreshUserInfo()
		self.RefreshMacdAndBoll()
		last_macd_time = 0
		while True:
			self.RefreshPrice()
			print '%.2f' % self.last_price,
			nt = self.NeedTrade()
			if nt != 0:
				order_id = self.Trade(nt)
				if order_id == False:
					continue
				time.sleep(8)
				order_info = self.oktrader.check_order(order_id)
				if int(order_info['orders'][0]['status']) == -1:
					success_flag = False
				else:
					success_flag = True
				success_flag = not (int(order_info['orders'][0]['status']) == -1)
				self.CommitStage(success_flag)
				if success_flag:
					self.RefreshUserInfo()
					self.stop_trade_time = int(time.time()) + 90
			if self.sys_time%60>4 and self.sys_time%60<=14 and self.sys_time>last_macd_time+30:
				self.RefreshMacdAndBoll()
				last_macd_time = self.sys_time
			time.sleep(0.3)

if __name__ == '__main__':
	boll_macd = BollinMACD(kLineDBFileName)
	boll_macd.Run()
