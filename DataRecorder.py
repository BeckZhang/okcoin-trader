#!/usr/bin/python
#-*-coding:utf8-*-

from utils import *
from SqliteUtils import *
from CalculateParams import *
from OkcoinInfos import *

kDBFileName = 'kline_okcoin.db'

class MACDData():
	"""
	这个类就是为了给DataRecorder提供支持
	两个方法: 刚开头时计算macd值, 和有了新数据时更新指标
	"""
	def __init__(self):
		self.diff = 0
		self.dea = 0
		self.ema12 = 0
		self.ema26 = 0
		self.bar = 0
		return None

	def First(self, close_list):
		diff, dea, bar, ema12, ema26 = MACD(close_list)
		self.diff = diff[-1]
		self.dea = dea[-1]
		self.bar = bar[-1]
		self.ema12 = ema12[-1]
		self.ema26 = ema26[-1]
		return True

	def Refresh(self, close_price):
		last_ema12 = self.ema12
		last_ema26 = self.ema26
		last_dea = self.dea
		self.ema12 = last_ema12*11.0/13.0 + close_price*2.0/13.0
		self.ema26 = last_ema26*25.0/27.0 + close_price*2.0/27.0
		self.diff = self.ema12-self.ema26
		self.dea = last_dea*0.8 + self.diff*0.2
		self.bar = 2*(self.diff - self.dea)
		return True

class DataRecorder():
	def __init__(self, DBFileName, symbol):
		os.system('mv %s ./database_baks/%s_bak_%d' % (DBFileName, DBFileName, int(time.time())))
		self.db_file_name = DBFileName
		self.dbwriter = DBWriter(DBFileName)
#	需要把macd指标写入数据库
		self.dbwriter.Execute('create table %s(id INT, time INT, close FLOAT, high FLOAT, low FLOAT, vol FLOAT, ema12 FLOAT, ema26 FLOAT, dea FLOAT)' % (kTableName))
		self.symbol = symbol
		self.kline_last_time = 0
		self.macd_data = MACDData()
		return None

	def WriteKLine(self, num):
		"""发送请求, 得到当前k线数据
		"""
		kline_time = 0
		while kline_time - self.kline_last_time < 50:
			time.sleep(1)
			kline_data = GetKLine(self.symbol,'1min',1) 
			kline_time = int(kline_data[0][0])/1000
		self.kline_last_time = kline_time
		self.macd_data.Refresh(float(kline_data[0][4]))
		self.WriteKLineIntoDB(kline_data[0], num, self.macd_data.ema12, self.macd_data.ema26, self.macd_data.dea)
		return True

	def WriteKLineIntoDB(self, kline_data, num, ema12=0, ema26=0, dea=0):
		kline_time = int(kline_data[0])/1000
		kline_close = float(kline_data[4])
		kline_high = float(kline_data[2])
		kline_low = float(kline_data[3])
		kline_vol = float(kline_data[5])
		sql_str = 'insert into %s values(%d, %d, %.2f, %.2f, %.2f, %.2f, %f, %f, %f)'%(kTableName, num, kline_time, kline_close, kline_high, kline_low, kline_vol, ema12, ema26, dea)
		#print sql_str
		self.dbwriter.Execute(sql_str)
		self.kline_last_time = kline_time
		return True
		
	def FirstKLine(self):
		"""
		首次执行时, 把之前两天的k线数据都得到
		"""
		data = GetKLine(self.symbol, '1min', 2880)
		close_list = []
		#for item in data:
		ema12 = 0
		ema26 = 0
		dea = 0
		for i in range(len(data)):
			close_list.append(float(data[i][4]))
			if i == len(data)-1:
				self.macd_data.First(close_list)
				ema12 = self.macd_data.ema12
				ema26 = self.macd_data.ema26
				dea = self.macd_data.dea
			self.WriteKLineIntoDB(data[i], i+1, ema12, ema26, dea)
		return len(data)

	def Run(self):
		num_kline = self.FirstKLine()
#此时, 拿到了之前的2880条k线数据, 并且最后一条的macd指标已经算好
		while True:
			num_kline += 1
			time.sleep(50)
			self.WriteKLine(num_kline)

if __name__ == '__main__':
	data_recorder = DataRecorder(kDBFileName, 'btc_cny')
	data_recorder.Run()
