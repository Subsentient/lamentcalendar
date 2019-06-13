
from datetime import date

Weekdays = { 0 : 'Sun', 1 : 'Mon', 2 : 'Tue', 3 : 'Wed', 4 : 'Thu', 5 : 'Fri', 6 : 'Sat' }

def GetWeekdayFromDate(Year, Month, Day):
	Year, Month, Day = int(Year), int(Month), int(Day)
	
	WDay = date(Year, Month, Day).weekday()
	
	WeekdayCalc = WDay + 1 if WDay < 6 else 0

	return WeekdayCalc

	
def DoubleDigitFormat(String):
	List = String.split(',')

	for Inc, Item in enumerate(List):
		List[Inc] = '0' + Item if len(Item) == 1 and Item != '*' else Item

	return ','.join(List)

def WeekdayFormat(String):
	List = String.split(',')

	for Inc, Item in enumerate(List):
		if Item == '*': continue

		assert Item.isdigit()
		if int(Item) not in Weekdays:
			print('WARNING: No weekday with numeric value ' + Item + ' exists.')
			continue

		List[Inc] = Weekdays[int(Item)]

	return ','.join(List)

