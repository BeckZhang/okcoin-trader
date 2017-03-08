#!/usr/bin/python
#-*-coding:utf8-*-

import httplib
import urllib
import json
import hashlib
import time
from utils import *

t1 = time.time()
t2 = time.time()
data = GetKLine('btc_cny', '1min', 100)
PrintData(data)

close_array = []
vol_array = []
for item in data:
	close_array.append(item[4])
	vol_array.append(item[5])

WriteArrayIntoFile(close_array, 'matlab_files/closes.txt') 
WriteArrayIntoFile(vol_array, 'matlab_files/vols.txt') 

print t2
