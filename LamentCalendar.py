#!/usr/bin/env python3
import sys
sys.path.append('core')
import GUI, DB

class PrimaryLoopObj(GUI.MainWindow):
	DB_FILEPATH = 'events.db'
	
	def __init__(self):
		GUI.MainWindow.__init__(self, {'dayclick': (self.OnDayClick,), 'newitem' : (self.NewItemClicked,) })
		self.DB = DB.DBObject(PrimaryLoopObj.DB_FILEPATH)
		
	def OnDayClick(self, Year, Month, Day):
		DayList = self.DB.SearchByDate(Year, Month, Day, '*')
		
		DayViewObj = GUI.DayView(Year, Month, Day, DayList, { 'editclicked' : (self.OnEditClick, self) })
		DayViewObj.show_all()

	def NewItemClicked(self):
		Year, Month, Day = self.Calendar.get_date()
		Month += 1

		EventObj = GUI.EventView(DB.NewEmptyItem(), self.OnSaveClick, (self,))
		EventObj.show_all()
		
	@staticmethod
	def OnSaveClick(Dict, OriginalName, ForcedSelf, DayViewDialog):
		if OriginalName != Dict['name'] and OriginalName in ForcedSelf.DB:
			del ForcedSelf.DB[OriginalName]
			
		ForcedSelf.DB[Dict['name']] = Dict
		
		DayViewDialog.Repopulate(ForcedSelf.DB.SearchByDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day, '*'))
		
	@staticmethod
	def OnEditClick(Widget, EventName, DayViewDialog, ForcedSelf):
		EventObj = GUI.EventView(ForcedSelf.DB[EventName], ForcedSelf.OnSaveClick, (ForcedSelf, DayViewDialog))
		EventObj.show_all()
		
MainObj = PrimaryLoopObj()
MainObj.show_all()

GUI.Gtk.main()
