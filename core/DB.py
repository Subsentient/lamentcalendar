import sqlite3, sys, os

class DBObject(object):
	def __init__(self, FilePath):
		
		if not os.path.isfile(FilePath):
			NeedInit = True
		else:
			NeedInit = False
			
		self.Conn = sqlite3.connect(FilePath)

		if not self.Conn:
			raise RuntimeError('Failed to open SQlite database ' + FilePath + '!')

		if NeedInit:
			if not self.SetupDB(FilePath):
				sys.exit(1)
			
	def SetupDB(self, FilePath):
		Cursor = self.Conn.cursor()

		#These fields are text so we can split them by commas to do cron-style formatting
		try:
			Cursor.execute("create table events "
						"(name text not null unique,"
						"year text not null,"
						"month text not null,"
						"day text not null,"
						"weekday text not null,"
						"hours text not null,"
						"minutes text not null);")
			return True
		except Exception as Err:
			print('Error executing database setup operation, caught ' + type(Err).__name__ + ' attempting to execute().')
			return False
	def Insert(InfoDict):
		assert type(InfoDict).__name__ == 'dict' and "name" in InfoDict
		
		Cursor = self.Conn.cursor()
		try:
			Cursor.execute("insert into events "
							"(name, "
							"year, "
							"month, "
							"day, "
							"weekday, "
							"hours, "
							"minutes) "
							"values (?, ?, ?, ?, ?, ?, ?);",
							(InfoDict["name"],
							InfoDict["year"],
							InfoDict["month"],
							InfoDict["day"],
							InfoDict["weekday"],
							InfoDict["hours"],
							InfoDict["minutes"]))

			return True
		except Exception as Err:
			print('Error storing item ' + InfoDict["name"] + " into database.")
			return False
		
