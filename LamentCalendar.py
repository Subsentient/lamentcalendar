#!/usr/bin/env python3
import sys
sys.path.append('core')
import GUI, DB, Alert

class PrimaryLoopObj(GUI.MainWindow):
	DB_FILEPATH = 'events.db'
	
	def __init__(self):
		GUI.MainWindow.__init__(self, {'monthchanged' : (self.OnMonthChange,),
										'dayclick': (self.OnDayClick,),
										'newitem' : (self.NewItemClicked,) }
								)
		Dates = [*self.Calendar.get_date()]
		Dates[1] += 1
		
		self.DB = DB.DBObject(PrimaryLoopObj.DB_FILEPATH)

		self.OnMonthChange(*Dates)
		
	def OnDayClick(self, Year, Month, Day):
		DayList = self.DB.SearchByDate(Year, Month, Day, '*')
		
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
			DayViewDialog.Repopulate(ForcedSelf.DB.SearchByDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day, '*'))
		
	@staticmethod
	def OnDeleteClick(Dict, OriginalName, ForcedSelf, DayViewDialog):
		if not OriginalName in ForcedSelf.DB:
			return

		del ForcedSelf.DB[OriginalName]
		
		if DayViewDialog:
			DayViewDialog.Repopulate(ForcedSelf.DB.SearchByDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day, '*'))

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

MainObj = PrimaryLoopObj()
MainObj.show_all()

GUI.Gtk.main()
