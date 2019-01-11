#!/usr/bin/env python3
import sys
sys.path.append('core')
import GUI, DB

class PrimaryLoopObj(GUI.MainWindow):
	DB_FILEPATH = 'events.db'
	
	def __init__(self):
		GUI.MainWindow.__init__(self, {'dayclick':self.OnDayClick})
		self.DB = DB.DBObject(PrimaryLoopObj.DB_FILEPATH)
		
	def OnDayClick(self, Year, Month, Day):
		DayList = self.DB.SearchByDate(Year, Month, Day, '*')
		
		DayViewObj = GUI.DayView(Year, Month, Day, DayList, { 'editclicked' : (self.OnEditClick, self) })
		DayViewObj.show_all()

	@staticmethod
	def OnEditClick(Widget, ForcedSelf, EventName):
		EventObj = GUI.EventView(ForcedSelf.DB[EventName])
		EventObj.show_all()
		
MainObj = PrimaryLoopObj()
MainObj.show_all()

GUI.Gtk.main()
