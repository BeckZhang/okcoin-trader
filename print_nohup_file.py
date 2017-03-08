#!/usr/bin/python
#-*-coding:utf8-*-

import os
import commands
import sys
import time

def GetFileLineNum(file_name):
	res = commands.getoutput('wc -l %s' % (file_name))
	cols = res.split()
	return int(cols[0])

if __name__=='__main__':
	file_name = str(sys.argv[1])
	os.system('tail %s' % (file_name))

	line_num_old = GetFileLineNum(file_name)
	while True:
		time.sleep(1.0)
		line_num_new = GetFileLineNum(file_name)
		if line_num_new != line_num_old:
			os.system("sed -n '%d,%dp' %s" % (line_num_old+1, line_num_new, file_name))
			line_num_old = line_num_new
