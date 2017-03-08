#!/usr/bin/python
#-*-coding:utf8-*-

import httplib
import urllib
import json
import hashlib
import time
from utils import *
from OkcoinInfos import *

class OKTrader():
	def __init__(self, api_key, api_secret, symbol, station='cn'):
		#这里api_key, api_secret是okcoin给的, symbol有两种选择: btc_cny和ltc_cny, station有两个选择: cn和com
		self.api_key = api_key
		self.api_secret = api_secret
		self.symbol = symbol
		self.station = station
		return None

	#需要签名
	def __signature(self, params={}):
		s = ''
		for k in sorted(params.keys()):
			if len(s)>0:
				s += '&'
			s += (k+'='+str(params[k]))
		s = s+'&secret_key='+self.api_secret
		m = hashlib.md5()
		m.update(s)
		return m.hexdigest().upper()
	
	def __api_call(self, method):
		conn = httplib.HTTPSConnection("www.okcoin.%s"%(self.station), timeout=10)
		conn.request("GET", "/api/v1/%s.do?symbol=%s" % (method, self.symbol))
		response = conn.getresponse()
		res_str = response.read()
		conn.close()
		data = json.loads(res_str)
		return data
	
	def __tapi_call(self, method, params={}):
		params['api_key'] = self.api_key
		params['sign']=self.__signature(params)
		headers = {"Content-type":"application/x-www-form-urlencoded"}
		conn = httplib.HTTPSConnection('www.okcoin.%s'%(self.station),timeout=10)
		params = urllib.urlencode(params)
		conn.request('POST','/api/v1/%s.do'%method, params, headers)
		response = conn.getresponse()
		res_str = response.read()
		conn.close()
		data = json.loads(res_str)
		res = data.get('result')
		if res == 'true' or res == True:
			return data
		else:
			raise Exception('error code %s' % data['error_code'])
	

	def trade(self,ttype,price,amt):
		params = {
				'symbol':self.symbol,
				'type':ttype,
				'price':str(price),
				'amount':str(amt)
		}
		print 'OKTRADER.trade(type=%s,price=%f,amt=%f)' % (ttype, price, amt)
		res = self.__tapi_call('trade',params)
		return res['order_id']

	def check_order(self, order_id):
#		status:-1:已撤销  0:未成交  1:部分成交  2:完全成交 4:撤单处理中
		params = {
				'symbol':self.symbol,
				'order_id':order_id,
		}
		print 'OKTRADER.check_order(order_id=%s),' % (str(order_id)),
		res = self.__tapi_call('order_info',params)
		print 'STATUS =',res['orders'][0]['status']
		#return res['orders'][0]['status']
		return res

	def cancel_order(self, order_id):
		params = {
				'symbol':self.symbol,
				'order_id':order_id,
		}
		print 'OKTRADER.CancelOrder(order_id=%s)'%(str(order_id))
		try:
			self.__tapi_call('cancel_order',params)
			res = True
			print 'SUCCEEDED!'
		except Exception as e:
			print 'ERROR:', str(e)
			res = False
		return res

	def check_user_info(self):
		return self.__tapi_call('userinfo', {})

if __name__=='__main__':
	oktrader = OKTrader(kApiKey, kSecretKey, 'btc_cny')
	#order_id = oktrader.trade('sell',2825,0.01)
	order_id = '1677509341'
	print 'order_id:',order_id
	PrintData(oktrader.check_order(order_id))

#	time.sleep(5)
#	PrintData(oktrader.check_knock(order_id))
	
	PrintData(oktrader.cancel_order(order_id))
	PrintData(oktrader.check_user_info())
	print 'process continue...'
