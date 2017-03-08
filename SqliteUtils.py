#!/usr/bin/python
#-*-coding:utf8-*-

import sqlite3

class DBWriter():
	def __init__(self, db_file_name):
		self.fid = db_file_name
		self.cx = sqlite3.connect(db_file_name)
		self.cu = self.cx.cursor()
	
	def Execute(self, sql_str):
		self.cx.execute(sql_str)
		self.cx.commit()
		return True
	
	def GetResult(self, sql_str):
		self.cu.execute(sql_str)
		res = self.cu.fetchall()
		return res

	def GetOneResult(self, sql_str):
		self.cu.execute(sql_str)
		res = self.cu.fetchone()
		return res

if __name__=='__main__':
	kFileName = 'test_data.db'

	cx = sqlite3.connect(kFileName)
	cu = cx.cursor()

#cu.execute('create table catalog(id integer primary key, pid integer,name varchar(10) UNIQUE)')

#cu.execute("insert into catalog values(2, 24, 'name2')")
#cu.execute("insert into catalog values(3, 1345, 'world')")

	cx.commit()

	fid = DBWriter(kFileName)
#	fid.Execute("insert into catalog values(8,2456,'beck')")
#	fid.Execute("insert into catalog values(7,2455,'zhang')")
	res = fid.GetResult("select * from catalog")
	print res
