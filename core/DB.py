import sqlite3, sys, os

#I could have just used pickle I guess, but I wanted something portable and recoverable.
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
				raise RuntimeError('Unable to setup new database at ' + FilePath + '!')

		self.Data = self.GetList()

		if type(self.Data) is not dict:
			raise RuntimeError('SQlite database opened, but unable to load contents to memory!')
	def __del__(self):
		self.Conn.commit()
		self.Conn.close()
		
	def __getitem__(self, Key):
		if not Key in self.Data:
			raise KeyError("No such key " + Key + " in database.")
		return self.Data[Key]
		
	def __setitem__(self, Key, Value):
		self.Delete(Key)
		assert self.Insert(Value)
		self.Data[Key] = Value
		
	def __delitem__(self, Key):
		if not Key in self.Data:
			raise KeyError('No key ' + Key + ' in database!')
		assert self.Delete(Key)
		del self.Data[Key]
		
	def __iter__(self):
		for Item in self.Data:
			yield Item

	def __len__(self):
		return len(self.Data)
	
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
	def Insert(self, InfoDict):
		assert type(InfoDict) is dict and 'name' in InfoDict
		
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
	def Delete(self, ItemName):
		assert type(ItemName) is str

		Cursor = self.Conn.cursor()

		try:
			Cursor.execute("delete from events where name=?;", (ItemName,))
			return True
		except Exception as Err:
			return False
	def GetList(self):
		Cursor = self.Conn.cursor()

		try:
			Cursor.execute('select * from events;')

			Data = Cursor.fetchall()
			
		except Exception as Err:
			print('Error fetching list of entries, caught ' + type(Err).__name__)
			return None

		Results = {}
		for Tuple in Data:
			Item = {}
			Item['name'], \
			Item['year'], \
			Item['month'], \
			Item['day'], \
			Item['weekday'], \
			Item['hours'], \
			Item['minutes'] = Tuple
			
			Results[Item['name']] = Item
		
		return Results

	@staticmethod
	def DateCmp(Val1, Val2):
		Val1s = Val1.split(',')
		Val2s = Val2.split(',')
	
		for v1 in Val1s:
			for v2 in Val2s:
				if v1 == v2 or v1 == '*' or v2 == '*':
					return True
		return False
	
	def SearchByDate(self, Year, Month, Day, Weekday):
		"""I suppose I could just use multiple dictionaries to hold these for faster searching,
		but speed doesn't matter for a calendar and I can't be bothered."""
		Year = str(Year)
		Month = str(Month)
		Day = str(Day)
		Weekday = str(Weekday)
		
		Results = []
		
		for Sub in self.Data:
			Item = self.Data[Sub]
			
			if self.DateCmp(Year, Item['year']) \
			and self.DateCmp(Month, Item['month']) \
			and self.DateCmp(Day, Item['day']) \
			and self.DateCmp(Weekday, Item['weekday']):
				Results.append(Item)
				
		return Results
