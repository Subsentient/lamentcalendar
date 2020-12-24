import sqlite3, sys, os, time
from enum import IntEnum, auto
#I could have just used pickle I guess, but I wanted something portable and recoverable.

class FieldType(IntEnum):
	TEXT = 0
	TIMEFORMAT = 1
	FILEPATH = 2
	BOOLEAN = 3

class ItemField(IntEnum):
	NAME = 1
	DESCRIPTION = auto()
	YEAR = auto()
	MONTH = auto()
	DAY = auto()
	WEEKDAY = auto()
	HOURS = auto()
	MINUTES = auto()
	ALERTFILE = auto()
	REPEATALARM = auto()

FieldNames = \
		{	ItemField.NAME : 'name',
			ItemField.DESCRIPTION : 'description',
			ItemField.YEAR : 'year',
			ItemField.MONTH : 'month',
			ItemField.DAY : 'day',
			ItemField.WEEKDAY : 'weekday',
			ItemField.HOURS : 'hours',
			ItemField.MINUTES : 'minutes',
			ItemField.ALERTFILE : 'alert_file',
			ItemField.REPEATALARM : 'repeat_alarm_sound',
		}

FieldDBTypes = \
		{	ItemField.NAME : FieldType.TEXT,
			ItemField.DESCRIPTION : FieldType.TEXT,
			ItemField.YEAR : FieldType.TIMEFORMAT,
			ItemField.MONTH : FieldType.TIMEFORMAT,
			ItemField.DAY : FieldType.TIMEFORMAT,
			ItemField.WEEKDAY : FieldType.TIMEFORMAT,
			ItemField.HOURS : FieldType.TIMEFORMAT,
			ItemField.MINUTES : FieldType.TIMEFORMAT,
			ItemField.ALERTFILE : FieldType.FILEPATH,
			ItemField.REPEATALARM : FieldType.BOOLEAN
		}

def NewEmptyItem():
	RetVal = {}
	
	for f in FieldDBTypes:
		if FieldDBTypes[f] == FieldType.TEXT:
			RetVal[f] = ''
		elif FieldDBTypes[f] == FieldType.TIMEFORMAT:
			RetVal[f] = '*'
		elif FieldDBTypes[f] == FieldType.FILEPATH:
			RetVal[f] = 'null'
		elif FieldDBTypes[f] == FieldType.BOOLEAN:
			RetVal[f] = '0'

	return RetVal

class DBObject(object):
	DB_FILEPATH = 'events.db'
	
	def __init__(self):
		
		if not os.path.isfile(self.DB_FILEPATH):
			NeedInit = True
		else:
			NeedInit = False
			
		self.Conn = sqlite3.connect(self.DB_FILEPATH)

		if not self.Conn:
			raise RuntimeError('Failed to open SQlite database ' + self.DB_FILEPATH + '!')

		if NeedInit:
			if not self.SetupDB(self.DB_FILEPATH):
				raise RuntimeError('Unable to setup new database at ' + self.DB_FILEPATH + '!')
		self.LoadDB()
		
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

	def __contains__(self, Name):
		return Name in self.Data

	def __iter__(self):
		for Item in self.Data:
			yield Item

	def __len__(self):
		return len(self.Data)
	def LoadDB(self):
		RemainingAttempts = 3
		Data = None
		MT = None
		
		for Inc in range(0, RemainingAttempts):
			try:
				self.Conn = sqlite3.connect(self.DB_FILEPATH)
				Data = self.GetList()
				MT = os.stat(self.DB_FILEPATH)
				break
			except:
				time.sleep(0.5)
				continue
			
		if Data is None or MT is None:
			raise RuntimeError('Unable to load SQLite database!')

		self.Data = Data
		self.ModTime = MT.st_mtime

	def SetupDB(self, FilePath):
		Cursor = self.Conn.cursor()

		#These fields are text so we can split them by commas to do cron-style formatting
		try:
			Cursor.execute("create table events "
						"(name text not null unique,"
						"description text not null,"
						"year text not null,"
						"month text not null,"
						"day text not null,"
						"weekday text not null,"
						"hours text not null,"
						"minutes text not null,"
						"alert_file text not null,"
						"repeat_alarm_sound text not null);")
			self.Conn.commit()
			return True
		except Exception as Err:
			print('Error executing database setup operation, caught ' + type(Err).__name__ + ' attempting to execute().')
			return False
	def Insert(self, InfoDict):
		assert type(InfoDict) is dict and ItemField.NAME in InfoDict

		#print(InfoDict)
		
		Cursor = self.Conn.cursor()
		try:
			Cursor.execute("insert into events "
							"(name, "
							"description, "
							"year, "
							"month, "
							"day, "
							"weekday, "
							"hours, "
							"minutes, "
							"alert_file, "
							"repeat_alarm_sound) "
							"values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
							(InfoDict[ItemField.NAME],
							InfoDict[ItemField.DESCRIPTION],
							InfoDict[ItemField.YEAR],
							InfoDict[ItemField.MONTH],
							InfoDict[ItemField.DAY],
							InfoDict[ItemField.WEEKDAY],
							InfoDict[ItemField.HOURS],
							InfoDict[ItemField.MINUTES],
							InfoDict[ItemField.ALERTFILE],
							InfoDict[ItemField.REPEATALARM]))
			self.Conn.commit()
			return True
		except Exception as Err:
			print('Error storing item ' + InfoDict[ItemField.NAME] + " into database.")
			return False
	def Delete(self, ItemName):
		assert type(ItemName) is str

		Cursor = self.Conn.cursor()

		Ok = False
		
		for Inc in range(0, 3):
			try:
				Cursor.execute("delete from events where name=?;", (ItemName,))
				self.Conn.commit()
				Ok = True
				break
			except:
				time.sleep(0.5)

		return Ok
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
			Item[ItemField.NAME], \
			Item[ItemField.DESCRIPTION], \
			Item[ItemField.YEAR], \
			Item[ItemField.MONTH], \
			Item[ItemField.DAY], \
			Item[ItemField.WEEKDAY], \
			Item[ItemField.HOURS], \
			Item[ItemField.MINUTES], \
			Item[ItemField.ALERTFILE], \
			Item[ItemField.REPEATALARM] = Tuple
			
			Results[Item[ItemField.NAME]] = Item
		
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
			
			if self.DateCmp(Year, Item[ItemField.YEAR]) \
			and self.DateCmp(Month, Item[ItemField.MONTH]) \
			and self.DateCmp(Day, Item[ItemField.DAY]) \
			and self.DateCmp(Weekday, Item[ItemField.WEEKDAY]):
				Results.append(Item)

		if Results:
			Results.sort(key = lambda Var : Var[ItemField.NAME].lower())
		
		return Results

	def CheckReload(self):
		S = None

		for _ in range(0, 3):
			try:
				S = os.stat(self.DB_FILEPATH)
				break
			except:
				time.sleep(0.5)

		if S is None: #Silently fail.
			return

		if S.st_mtime > self.ModTime:
			self.LoadDB()
		
	def CheckTriggers(self, NotificationCallback, *CallbackArgs):
		def FieldMatches(Times, T2):
			if Times == '*':
				return True
			for Time in Times.split(','):
				if int(Time) != int(T2):
					continue
				return True
		
		TimeStruct = time.localtime()
		
		#Python's time module uses Monday for the week start... ugh. Compensate for that.
		WeekdayCalc = TimeStruct.tm_wday + 1 if TimeStruct.tm_wday < 6 else 0
		
		TodayItems = self.SearchByDate(TimeStruct.tm_year, TimeStruct.tm_mon, TimeStruct.tm_mday, WeekdayCalc)
	
		for Item in TodayItems:
			if FieldMatches(Item[ItemField.HOURS], TimeStruct.tm_hour) \
				and FieldMatches(Item[ItemField.MINUTES], TimeStruct.tm_min) \
				and TimeStruct.tm_sec == 0:
					NotificationCallback(Item, *CallbackArgs)

		return True

