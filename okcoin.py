# -*- coding: utf-8 -*-
# OKCoin api
# https://www.okcoin.com/t-1000097.html
# https://www.okcoin.com/t-1000052.html

import httplib
import urllib
import json
#import md5
import md5
import time

class OKCoin():
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def __signature(self, params):
        s = ''
        for k in sorted(params.keys()):
            if len(s) > 0:
                s += '&'
            s += k + '=' + str(params[k])
        return md5.new(s + self.api_secret).hexdigest().upper()

    def __tapi_call(self, method, params={}):
        params["partner"] = self.api_key
        params["sign"] = self.__signature(params)
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        conn = httplib.HTTPSConnection("www.okcoin.com", timeout=10)
        params = urllib.urlencode(params)
        conn.request("POST", "/api/%s.do" % method, params, headers)
        response = conn.getresponse()
        data = json.load(response)
        conn.close()
        #print data
        res = data.get("result")
        if res == "true" or res == True:
            return data
        else:
            raise Exception("error code %s" % data["errorCode"])

    def __api_call(self, method, pair):
        conn = httplib.HTTPSConnection("www.okcoin.com", timeout=10)
        conn.request("GET", "/api/%s.do?symbol=%s" % (method, pair))
        response = conn.getresponse()
        #data = json.load(response)
        data = response.read()
        conn.close()
        return data

    def get_ticker(self, pair):
        # https://www.okcoin.com/api/ticker.do?symbol=ltc_cny
        data = self.__api_call("ticker", pair)
        if "ticker" in data:
            return {
                "last": data["ticker"]["last"],
                "buy": data["ticker"]["buy"],
                "sell": data["ticker"]["sell"],
                "vol": data["ticker"]["vol"]
            }
        else:
            raise Exception("Error when get ticker")

    def get_depth(self, pair):
        # https://www.okcoin.com/api/depth.do?symbol=ltc_cny
        return self.__api_call("depth", pair)

    def get_funds(self):
        return self.__tapi_call('userinfo')

    def get_orders(self, pair, order_id=-1):
        params = { "symbol"   : pair, "order_id" : order_id }
        result = self.__tapi_call('getorder', params)
        return result["orders"]

    def trade(self, tpair, ttype, price, amount):
        params = {
            "symbol" : tpair,
            "type"   : ttype,
            "rate"   : price,
            "amount" : amount
        }
        result = self.__tapi_call('trade', params)
        return result["order_id"]

    def buy(self, pair, price, amount):
        result = self.trade(pair, "buy", price, amount)
        return result

    def sell(self, pair, price, amount):
        result = self.trade(pair, "sell", price, amount)
        return result

    def cancel(self, pair, order_id):
        params = { "symbol": pair, "order_id" : order_id }
        return type(self.__tapi_call('cancelorder', params)) == dict

