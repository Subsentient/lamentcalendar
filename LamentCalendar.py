#!/usr/bin/env python3
import sys, time
sys.path.append('core')
import GUI, DB, Alert

class PrimaryLoopObj(GUI.MainWindow):
	DB_FILEPATH = 'events.db'
	
	def __init__(self):
		GUI.MainWindow.__init__(self, {'monthchanged' : (self.OnMonthChange,),
										'dayclick': (self.OnDayClick,),
										'newitem' : (self.NewItemClicked,),
										'listallclicked' : (self.OnListAllClick,), }
								)
		Dates = [*self.Calendar.get_date()]
		Dates[1] += 1
		
		self.DB = DB.DBObject(PrimaryLoopObj.DB_FILEPATH)

		self.OnMonthChange(*Dates)
		self.Notifications = {}
		
	def OnListAllClick(self, *Unused):
		DayList = [self.DB[Item] for Item in self.DB] #DBObject is iterable like a dict

		DayViewObj = GUI.DayView('*', '*', '*', DayList, { 'editclicked' : (self.OnEditClick, self),
															'newclicked' : (self.OnNewButtonClick, self) } )
		DayViewObj.show_all()
		
	def OnDayClick(self, Year, Month, Day):
		DayList = self.DB.SearchByDate(Year, Month, Day, GUI.GetWeekdayFromDate(Year, Month, Day))
		
		DayViewObj = GUI.DayView(Year, Month, Day, DayList, { 'editclicked' : (self.OnEditClick, self),\
															'newclicked' : (self.OnNewButtonClick, self) })
		DayViewObj.show_all()
		
	def OnMonthChange(self, Year, Month, Day):
		self.Calendar.clear_marks()
		
		DayList = self.DB.SearchByDate(Year, Month, '*', '*')

		for Event in DayList:
			for Day in Event['day'].split(','):
				if not Day.isnumeric():
					continue
					
				self.Calendar.mark_day(int(Day))

	def NewItemClicked(self):
		Year, Month, Day = self.Calendar.get_date()
		Month += 1

		EventObj = GUI.EventView(DB.NewEmptyItem(), { 'saveclose' : (self.OnSaveClick, self, None), \
													'delclose' : (self.OnSaveClick, self, None) } )
		EventObj.show_all()
		
	@staticmethod
	def OnSaveClick(Dict, OriginalName, ForcedSelf, DayViewDialog):
		if OriginalName != Dict['name'] and OriginalName in ForcedSelf.DB:
			del ForcedSelf.DB[OriginalName]
			
		ForcedSelf.DB[Dict['name']] = Dict
		
		if DayViewDialog:
			WDay = GUI.GetWeekdayFromDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day)
			DayViewDialog.Repopulate(ForcedSelf.DB.SearchByDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day, WDay))
		
	@staticmethod
	def OnDeleteClick(Dict, OriginalName, ForcedSelf, DayViewDialog):
		if not OriginalName in ForcedSelf.DB:
			return

		del ForcedSelf.DB[OriginalName]
		
		if DayViewDialog:
			WDay = GUI.GetWeekdayFromDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day)
			DayViewDialog.Repopulate(ForcedSelf.DB.SearchByDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day, WDay))

	@staticmethod
	def OnEditClick(Widget, EventName, DayViewDialog, ForcedSelf):
		CallbackDict = { 'saveclose' : (ForcedSelf.OnSaveClick, ForcedSelf, DayViewDialog),
						'delclose' : (ForcedSelf.OnDeleteClick, ForcedSelf, DayViewDialog) }
		EventObj = GUI.EventView(ForcedSelf.DB[EventName], CallbackDict)
		EventObj.show_all()

	@staticmethod
	def OnNewButtonClick(Widget, EventName, DayViewDialog, ForcedSelf):
		CallbackDict = { 'saveclose' : (ForcedSelf.OnSaveClick, ForcedSelf, DayViewDialog),
						'delclose' : (ForcedSelf.OnDeleteClick, ForcedSelf, DayViewDialog) }
		TempObj = DB.NewEmptyItem()
		
		TempObj['name'] = 'New Event'
		
		TempObj['year'], TempObj['month'], TempObj['day'] = str(DayViewDialog.Year), str(DayViewDialog.Month), str(DayViewDialog.Day)
		
		EventObj = GUI.EventView(TempObj, CallbackDict)
		EventObj.show_all()

	@staticmethod
	def CheckTimesFunc(MainObj):
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
		
		TodayItems = MainObj.DB.SearchByDate(TimeStruct.tm_year, TimeStruct.tm_mon, TimeStruct.tm_mday, WeekdayCalc)

		for Item in TodayItems:
			if FieldMatches(Item['hours'], TimeStruct.tm_hour) and FieldMatches(Item['minutes'], TimeStruct.tm_min) \
				and Item['name'] not in MainObj.Notifications \
				and TimeStruct.tm_sec == 0:
					MainObj.SpawnNotification(Item)
				
		return True

	@staticmethod
	def DismissNotification(**Args):
		Obj = Args['mainobj']
		Name = Args['instancename']
		
		del Obj.Notifications[Name]
		
	def SpawnNotification(self, Item):
		
		Title = 'Event "{0}" time activation triggered'.format(Item['name'])
		Msg = 'Time activation triggered for event "{0}" on '.format(Item['name']) + time.ctime() \
				+ '\nEvent description:\n\n' + Item['description']

		self.Notifications[Item['name']] = NotifObj = GUI.Notification(Title,
																		Msg,
																		Item['alert_file'] if Item['alert_file'] != 'null' else None,
																		int(Item['repeat_alarm_sound']),
																		callback=self.__class__.DismissNotification,
																		instancename=Item['name'],
																		mainobj=self)
		NotifObj.show_all()

		return True
		
MainObj = PrimaryLoopObj()
MainObj.show_all()

GUI.GLib.timeout_add(200, PrimaryLoopObj.CheckTimesFunc, MainObj)

GUI.Gtk.main()
