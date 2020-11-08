import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gtk, GdkPixbuf, GLib
import sys, os, time

from DB import FieldDBTypes, FieldType, FieldNames, ItemField
import DB
import Audio, DateCalc

IconPixmap = GdkPixbuf.Pixbuf.new_from_file('lament.png')
ActiveIconPixmap = GdkPixbuf.Pixbuf.new_from_file('active.png')

def SetWindowIcon(Window, Icon = IconPixmap):
	Window.set_icon(Icon)

class MainWindow(Gtk.Window):

	def DestroyStopwatch(self, Stopwatch):
		self.Stopwatches.remove(Stopwatch)
		Stopwatch.destroy()

	def __init__(self): #Yes, the same static-initialized list is indeed what we want.
		
		Gtk.Window.__init__(self, title='Lament Calendar')
		
		self.Notifications = {}
		self.Stopwatches = []
		
		self.set_default_size(640, 480)
		self.connect('destroy', self.TerminateApp)
		
		SetWindowIcon(self)
		
		self.VBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		self.add(self.VBox)

		# Create the menu bar
		self.MenuBarAlign = Gtk.Alignment(xalign=0.0, yalign=0.5, xscale=1.0, yscale=0.0)
		self.MenuBar = Gtk.MenuBar()
		self.MenuBarAlign.add(self.MenuBar)

		# Create file menu
		self.FileMenu = Gtk.Menu.new()
		self.FileTag = Gtk.MenuItem.new_with_mnemonic('_File')
		self.FileTag.set_submenu(self.FileMenu)
		self.MenuBar.append(self.FileTag)

		self.TimerMenu = Gtk.Menu.new()
		self.TimerTag = Gtk.MenuItem.new_with_mnemonic('_Timer')
		self.TimerTag.set_submenu(self.TimerMenu)
		self.MenuBar.append(self.TimerTag)

		#Populate file menu
		self.QuitItem = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_QUIT)
		self.QuitItem.connect('activate', self.TerminateApp)
		
		self.NewEventItem = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_NEW)
		self.NewEventItem.set_label("_New Event")
		self.NewEventItem.connect('activate', self.OnNewItemClick)
		
		self.ReloadDBItem = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_REFRESH)
		self.ReloadDBItem.set_label("_Reload database")
		self.ReloadDBItem.connect('activate', self.OnReloadDBClick)
		
		self.AllEventsItem = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_INDEX)
		self.AllEventsItem.set_label('List _all events')
		self.AllEventsItem.connect('activate', self.OnListAllClick)

		self.MinimizeToTrayItem = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_CLOSE)
		self.MinimizeToTrayItem.set_label("_Minimize to tray")
		self.MinimizeToTrayItem.connect('activate', self.OnSendToTrayClick)

		self.SilenceItem = Gtk.CheckMenuItem.new_with_mnemonic("_Silence alarms")
		self.SilenceItem.set_active(Audio.GetSilenced())
		self.SilenceItem.connect('activate', self.SilenceToggled)
		
		self.FileMenu.append(self.MinimizeToTrayItem)
		self.FileMenu.append(self.SilenceItem)
		self.FileMenu.append(self.NewEventItem)
		self.FileMenu.append(self.AllEventsItem)
		self.FileMenu.append(self.ReloadDBItem)
		self.FileMenu.append(self.QuitItem)

		#Populate timer menu
		self.StopwatchItem = Gtk.MenuItem.new_with_mnemonic('New s_topwatch')
		self.StopwatchItem.connect('activate', lambda *Discarded : self.SpawnStopwatch())
		self.TimerMenu.append(self.StopwatchItem)
		
		#Configure calendar display.
		self.Calendar = Gtk.Calendar()
		self.Calendar.connect('day-selected-double-click', self.DayClicked)
		self.Calendar.connect('month-changed', self.MonthChanged)
		
		#Add it all in
		self.VBox.pack_start(self.MenuBarAlign, False, True, 0)
		self.VBox.pack_start(self.Calendar, True, True, 0)
		
		#First callbacks we must manually invoke
		Dates = [*self.Calendar.get_date()]
		Dates[1] += 1
		
		self.DB = DB.DBObject(DB.DBObject.DB_FILEPATH)

		self.OnMonthChange(*Dates)

	def SpawnStopwatch(self):
		S = Stopwatch(self)
		
		self.Stopwatches.append(S)

		S.show_all()
		
	def TerminateApp(self, Widget):
		sys.exit(0)
		
	def SilenceToggled(self, MenuItem):
		OldState = Audio.GetSilenced()
		Audio.SetSilenced(not OldState)

		Methods = (Audio.AudioEvent.Unpause, Audio.AudioEvent.Pause)

		for Key in self.Notifications:
			Methods[not OldState](self.Notifications[Key].Noisemaker)

	def DayClicked(self, Calendar):
		assert Calendar is self.Calendar
		Dates = [*Calendar.get_date()]
		Dates[1] += 1

		self.OnDayClick(*Dates)

	def MonthChanged(self, Calendar):
		assert Calendar is self.Calendar

		Dates = [*self.Calendar.get_date()]
		Dates[1] += 1 #Change month to 1 to 12 instead of 0 to 11
			
		self.OnMonthChange(*Dates)
		
	def MarkDay(self, Day):
		self.Calendar.mark_day(Day)

	def UnmarkDay(self, Day):
		self.Calendar.unmark_day(Day)
		

	def OnReloadDBClick(self, *Unused):
		self.DB.LoadDB()
		
	def OnSendToTrayClick(self, *Unused):
		self.hide()
		
	def OnListAllClick(self, *Unused):
		DayList = [self.DB[Item] for Item in self.DB] #DBObject is iterable like a dict
		DayList.sort(key = lambda k : k[DB.ItemField.NAME].lower())
		
		DayViewObj = DayView('*', '*', '*', DayList, { 'editclicked' : (self.OnEditClick,),
													'newclicked' : (self.OnNewButtonClick,) } )
		DayViewObj.show_all()
		
	def OnDayClick(self, Year, Month, Day):
		DayList = self.DB.SearchByDate(Year, Month, Day, DateCalc.GetWeekdayFromDate(Year, Month, Day))
		
		DayViewObj = DayView(Year, Month, Day, DayList, { 'editclicked' : (self.OnEditClick,),\
														'newclicked' : (self.OnNewButtonClick,) })
		DayViewObj.show_all()
		
	def OnMonthChange(self, Year, Month, Day):
		self.Calendar.clear_marks()
		
		DayList = self.DB.SearchByDate(Year, Month, '*', '*')

		for Event in DayList:
			for Day in Event[DB.ItemField.DAY].split(','):
				if not Day.isnumeric():
					continue
					
				self.Calendar.mark_day(int(Day))

	def OnNewItemClick(self, *Discarded):
		Year, Month, Day = self.Calendar.get_date()
		Month += 1

		EventObj = EventView(DB.NewEmptyItem(), { 'saveclose' : (self.OnSaveClick, None), \
													'delclose' : (self.OnSaveClick, None) } )
		EventObj.show_all()
		
	def OnSaveClick(self, Dict, OriginalName, DayViewDialog):
		if OriginalName != Dict[DB.ItemField.NAME] and OriginalName in self.DB:
			del self.DB[OriginalName]
			
		self.DB[Dict[DB.ItemField.NAME]] = Dict
		
		if DayViewDialog:
			if DayViewDialog.Year.isnumeric() and DayViewDialog.Month.isnumeric() and DayViewDialog.Day.isnumeric():
				WDay = DateCalc.GetWeekdayFromDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day)
			else:
				WDay = '*'
			DayViewDialog.Repopulate(self.DB.SearchByDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day, WDay))
		
	def OnDeleteClick(self, Dict, OriginalName, DayViewDialog):
		if not OriginalName in self.DB:
			return

		del self.DB[OriginalName]
		
		if DayViewDialog:
			if DayViewDialog.Year.isnumeric() and DayViewDialog.Month.isnumeric() and DayViewDialog.Day.isnumeric():
				WDay = DateCalc.GetWeekdayFromDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day)
			else:
				WDay = '*'
			DayViewDialog.Repopulate(self.DB.SearchByDate(DayViewDialog.Year, DayViewDialog.Month, DayViewDialog.Day, WDay))

	def OnEditClick(self, Widget, EventName, DayViewDialog):
		CallbackDict = { 'saveclose' : (self.OnSaveClick, DayViewDialog),
						'delclose' : (self.OnDeleteClick, DayViewDialog) }
		EventObj = EventView(self.DB[EventName], CallbackDict)
		EventObj.show_all()

	def OnNewButtonClick(self, Widget, EventName, DayViewDialog):
		CallbackDict = { 'saveclose' : (self.OnSaveClick, DayViewDialog),
						'delclose' : (self.OnDeleteClick, DayViewDialog) }
		TempObj = DB.NewEmptyItem()
		
		TempObj[DB.ItemField.NAME] = 'New Event'
		
		TempObj[DB.ItemField.YEAR], TempObj[DB.ItemField.MONTH], TempObj[DB.ItemField.DAY] = str(DayViewDialog.Year), str(DayViewDialog.Month), str(DayViewDialog.Day)
		
		EventObj = EventView(TempObj, CallbackDict)
		EventObj.show_all()


	def DismissNotification(self, Name):
		del self.Notifications[Name]
		
	def SpawnNotification(self, Item):
		
		if Item[DB.ItemField.NAME] in self.Notifications:
			return False
		
		Title = 'Event "{0}" time activation triggered'.format(Item[DB.ItemField.NAME])
		Msg = 'Time activation triggered for event "{0}" on '.format(Item[DB.ItemField.NAME]) + time.ctime() \
				+ '\nEvent description:\n\n' + Item[ItemField.DESCRIPTION]

		self.Notifications[Item[DB.ItemField.NAME]] = NotifObj = Notification(Title,
																	Msg,
																	Item[DB.ItemField.ALERTFILE] if Item[DB.ItemField.ALERTFILE] != 'null' else None,
																	int(Item[DB.ItemField.REPEATALARM]),
																	self.DismissNotification,
																	Item[DB.ItemField.NAME])
		NotifObj.show_all()

		return True
		
	def SilenceSignalHandler(self, *Discarded):
		self.SilenceItem.set_active(not Audio.GetSilenced())
		
	def DismissAllSignalHandler(self, *Discarded):
		for Key in dict(self.Notifications): #Shallow copy because you can't iterate over it if you're deleting elements.
			Obj = self.Notifications[Key]
			Obj.DismissClicked()

class Stopwatch(Gtk.Window):
	def __init__(self, Parent = None, Title = 'Stopwatch', InitialSecs : float = 0.0):
		self.Running = False
		self.Parent = Parent
		self.TotalElapsed = 0
		self.CurTime = InitialSecs
		self.StartTime = 0

		Gtk.Window.__init__(self, title=Title)
		self.set_default_size(300, 100)

		SetWindowIcon(self)

		self.VBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		self.add(self.VBox)
		
		self.TimeLabel = Gtk.Label()
		self.VBox.pack_start(self.TimeLabel, True, False, 8)

		self.ToggleButton = Gtk.Button.new_with_mnemonic('_Start')
		self.ResetButton = Gtk.Button.new_with_mnemonic('_Reset')
		self.SaveButton = Gtk.Button.new_with_mnemonic('Sa_ve')

		self.HBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

		self.HBox.pack_start(self.ToggleButton, True, True, 4)
		self.HBox.pack_start(self.ResetButton, False, False, 4)
		self.HBox.pack_start(self.SaveButton, False, False, 4)
		
		self.VBox.pack_start(self.HBox, True, True, 0)

		self.ToggleButton.connect('clicked', lambda *Discarded : self.SetPaused(self.Running))
		self.ResetButton.connect('clicked', lambda *Discarded : self.OnResetClick())
		self.SaveButton.connect('clicked', lambda *Discarded : self.OnSaveClick())
		self.connect('destroy', lambda *D : self.Parent.DestroyStopwatch(self))

		self.ToggleButton.grab_focus()
		
		self.Wipe()
		
		GLib.timeout_add(100, self.UpdateTimer)
		
	def Wipe(self):
		self.CurTime = 0.0
		self.TotalElapsed = 0.0
		self.StartTime = time.time()
		self.Running = False
		self.ToggleButton.set_label('Start')
		self.DrawTimeLabel(0.0)

	def OnResetClick(self):
		self.set_title('Stopwatch')
		self.set_icon(IconPixmap)
		self.Wipe()
		
	def SetPaused(self, State):
		if State != self.Running:
			return True #Already in that state.

		self.set_icon(ActiveIconPixmap if not State else IconPixmap)
		
		if State:
			self.Running = False
			self.ToggleButton.set_label('Resume')
			self.set_title('Stopwatch')
			return True

		self.StartTime = time.time()
		self.TotalElapsed += self.CurTime - self.TotalElapsed
		self.Running = True
		self.ToggleButton.set_label('Pause')
		
		return True

	@property
	def TotalSecs(self):
		return self.CurTime

	def OnSaveClick(self):
		self.SetPaused(True)
		self.DumpToDisk()
		self.Wipe()

	def RunFileChooser(self):
		Chooser = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
										(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		Response = Chooser.run()

		Filename = None
		
		if Response == Gtk.ResponseType.OK:
			Filename = Chooser.get_filename()

		Chooser.destroy()

		return Filename

	def DumpToDisk(self):
		Path = self.RunFileChooser()

		if not Path:
			return

		DateFormat = time.strftime('%m/%d/%Y')
		TimeFormat = time.strftime('%H:%M:%S', time.gmtime(self.TotalSecs))

		with open(Path, 'a') as Desc:
			Desc.write(f'\n{DateFormat}\n{int(self.TotalSecs)}\t{TimeFormat}\n')

	def UpdateTimer(self):
		if not self.Running:
			return True
			
		self.CurTime = (time.time() - self.StartTime) + self.TotalElapsed
		
		self.DrawTimeLabel(self.CurTime)

		return True

	def DrawTimeLabel(self, TimeSecs : float):
		TVal = time.gmtime(TimeSecs)

		Fraction = TimeSecs % 1
		Fraction = int(Fraction * 100 if Fraction >= 0.1 else 0)

		SubTString = time.strftime('%H:%M:%S', TVal)
		TString =  f'{SubTString}.{str(Fraction)[0]}'
		self.TimeLabel.set_markup(f'<b><span font="22">{TString}</span></b>')
		
		if not Fraction and self.Running:
			self.set_title(f'{SubTString} - Stopwatch')
		
class DayView(Gtk.Window):
	def __init__(self, Year, Month, Day, DayList, Callbacks={}):
		self.Callbacks = Callbacks

		self.Year, self.Month, self.Day = str(Year), str(Month), str(Day)
		
		Gtk.Window.__init__(self, title='Events for ' + str(Year) + '-' +\
		DateCalc.DoubleDigitFormat(str(Month)) + '-' + \
		DateCalc.DoubleDigitFormat(str(Day)))
		SetWindowIcon(self)

		self.set_default_size(500, 300)
		self.VBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		self.add(self.VBox)

		self.CommandBarBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
		
		self.NewEventButton = Gtk.Button.new_with_mnemonic("_New")
		
		if 'newclicked' in self.Callbacks:
			self.NewEventButton.connect('clicked', self.Callbacks['newclicked'][0], '', self, *self.Callbacks['newclicked'][1:])
			
		self.NewEventButtonAlign = Gtk.Alignment.new(1.0, 0.0, 0.0, 0.0)
		self.NewEventButtonAlign.add(self.NewEventButton)
		self.CommandBarLabel = Gtk.Label()

		self.SetCommandBarStatus(DayList)
		
		self.CommandBarBox.pack_start(self.CommandBarLabel, False, False, 8)
		self.CommandBarBox.pack_start(self.NewEventButtonAlign, True, True, 0)
		
		self.VBox.pack_start(self.CommandBarBox, False, True, 8)
		self.VBox.pack_start(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), False, True, 0)
		
		self.WindowView = Gtk.ScrolledWindow.new()
		self.WindowView.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		WindowViewAlign = Gtk.Alignment.new(0.0, 0.0, 1.0, 1.0)
		WindowViewAlign.add(self.WindowView)
		self.VBox.pack_start(WindowViewAlign, True, True, 8)
		
		self.WindowViewBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		
		self.WindowView.add_with_viewport(self.WindowViewBox)
		
		for Value in DayList:
			self.AddItem(Value)

	def AddItem(self, Value):
		Label = Gtk.Label.new()

		Label.set_markup('<i>' + Value[DB.ItemField.NAME] + '</i>')
		
		HBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
		
		HBox.pack_start(Label, False, False, 4)
		HBox.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 4)
	
		TimeString = DateCalc.DoubleDigitFormat(Value[DB.ItemField.HOURS]) + ':' + DateCalc.DoubleDigitFormat(Value[DB.ItemField.MINUTES])
		
		HBox.pack_start(Gtk.Label(TimeString), False, False, 0)
		HBox.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 8)

		DateString = '<span foreground="#00cccc">' + DateCalc.DoubleDigitFormat(Value[DB.ItemField.YEAR]) + '</span>-' + \
					'<span foreground="#00cc00">' + DateCalc.DoubleDigitFormat(Value[DB.ItemField.MONTH]) + '</span>-' +\
					'<span foreground="#cccc00">' + DateCalc.DoubleDigitFormat(Value[DB.ItemField.DAY]) + '</span>   ' + \
					'<b>' + DateCalc.WeekdayFormat(Value[DB.ItemField.WEEKDAY]) + '</b>'

		DateLabel = Gtk.Label.new()
		DateLabel.set_markup(DateString)
		
		HBox.pack_start(DateLabel, False, False, 0)
		HBox.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 8)
		
		Button = Gtk.Button.new_with_label("Edit/View")
		ButtonAlign = Gtk.Alignment.new(1.0, 1.0, 0.0, 1.0)
		ButtonAlign.add(Button)
		
		if 'editclicked' in self.Callbacks:
			Button.connect('clicked', self.Callbacks['editclicked'][0], Value[DB.ItemField.NAME], self, *self.Callbacks['editclicked'][1:])

		HBox.pack_start(ButtonAlign, True, True, 0)
	
		
		self.WindowViewBox.pack_start(HBox, False, True, 0)
		self.WindowViewBox.pack_start(Gtk.Separator(), False, True, 0)

	def Wipe(self):
		self.WindowView.remove(self.WindowViewBox)
		self.WindowViewBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		self.WindowView.add(self.WindowViewBox)
	def Repopulate(self, DayList):
		self.Wipe()
		
		for Value in DayList:
			self.AddItem(Value)
			
		self.SetCommandBarStatus(DayList)
		self.show_all()
	def SetCommandBarStatus(self, DayList):
		self.CommandBarLabel.set_text('Found ' + str(len(DayList)) + ' matching events.')
		
class EventView(Gtk.Window):
	def RunChooser(self, Button, Key):
		Chooser = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
										(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		Response = Chooser.run()

		if Response == Gtk.ResponseType.OK:
			Filename = Chooser.get_filename()
			self.Fields[Key].set_label(Filename if len(Filename) < 25 else Filename[:20] + '...')
			self.Extra[Key] = Filename
		Chooser.destroy()
		
	def __CreateField(self, k):
		
		if FieldDBTypes[k] == FieldType.TEXT or FieldDBTypes[k] == FieldType.TIMEFORMAT:
			self.Fields[k] = Gtk.Entry.new_with_buffer(Gtk.EntryBuffer.new(self.Data[k], -1))

			IsText = FieldDBTypes[k] == FieldType.TEXT
			
			self.HBoxes[k].pack_start(self.Fields[k], IsText, IsText, 8)
			
			#Time formats also have a checkbox.
			if FieldDBTypes[k] == FieldType.TIMEFORMAT:
				self.Checkboxes[k] = Gtk.CheckButton.new_with_label("All")
			
				self.HBoxes[k].pack_start(self.Checkboxes[k], False, False, 8)
			
		elif FieldDBTypes[k] == FieldType.FILEPATH:
			Filename = self.Data[k] if self.Data[k] != 'null' else 'null'
			self.Fields[k] = Gtk.Button.new_with_label(Filename if len(Filename) < 25 else Filename[:20] + '...')
			self.Fields[k].connect('clicked', self.RunChooser, k)
			self.Extra[k] = Filename
			self.HBoxes[k].pack_start(self.Fields[k], True, False, 8)

		elif FieldDBTypes[k] == FieldType.BOOLEAN:
			self.Fields[k] = Gtk.CheckButton.new()

			self.HBoxes[k].pack_start(self.Fields[k], True, False, 8)
			


	def __init__(self, EventDict, Callbacks={}):
		assert DB.ItemField.NAME in EventDict
		
		self.OriginalName = EventDict[DB.ItemField.NAME]
		self.Callbacks = Callbacks
		
		Gtk.Window.__init__(self, title='Event "' + EventDict[DB.ItemField.NAME] + '"')
		
		SetWindowIcon(self)

		self.set_resizable(False)
		self.VBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		self.add(self.VBox)

		self.MainLabel = Gtk.Label.new('Configuration for event "' + EventDict[DB.ItemField.NAME] + '":')

		self.VBox.pack_start(self.MainLabel, False, True, 8)

		self.HBoxes = {}
		self.Fields = {}
		self.Checkboxes = {}
		self.ItemLabels = {}
		self.Extra = {}
		
		self.Data = EventDict
		#Populate fields
		for k in EventDict:
			self.ItemLabels[k] = Gtk.Label.new(FieldNames[k].replace('_', ' ').capitalize())
			self.HBoxes[k] = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

			LabelAlign = Gtk.Alignment.new(0.0, 0.0, 0.1, 1.0)
			LabelAlign.add(self.ItemLabels[k])
			
			self.HBoxes[k].pack_start(LabelAlign, True, True, 8)

			self.__CreateField(k)

			self.VBox.pack_start(self.HBoxes[k], True, True, 8)

			#Name field needs a separator
			if FieldDBTypes[k] == FieldType.TEXT:
				self.VBox.pack_start(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), True, True, 8)
				continue
				
			#Time fields need a checkbox
			if FieldDBTypes[k] == FieldType.TIMEFORMAT:
				if EventDict[k] == '*':
					self.Checkboxes[k].set_active(True)
					self.AnyBoxClicked(self.Checkboxes[k], k)
			
				self.HBoxes[k].pack_start(self.Checkboxes[k], False, False, 0)
				self.Checkboxes[k].connect('toggled', self.AnyBoxClicked, k)

			if FieldDBTypes[k] == FieldType.BOOLEAN:
				self.Fields[k].set_active(int(EventDict[k]))
				
		#Bottom controls
		self.DeleteButton = Gtk.Button.new_with_label('DELETE')
		self.DeleteButton.set_use_underline(True)
		
		self.AcceptButton = Gtk.Button.new_with_mnemonic('_Accept')
		self.CancelButton = Gtk.Button.new_with_mnemonic('_Cancel')
		
		self.AcceptButton.connect('clicked', self.StateClicked)
		self.CancelButton.connect('clicked', self.StateClicked)
		
		self.DeleteButton.connect('clicked', self.StateClicked)

		self.ButtonAlign = Gtk.Alignment.new(1.0, 1.0, 0.1, 1.0)
		self.ButtonHBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
		self.ButtonHBox.pack_start(self.DeleteButton, True, False, 48)
		self.ButtonHBox.add(self.CancelButton)
		self.ButtonHBox.add(self.AcceptButton)
		self.ButtonAlign.add(self.ButtonHBox)
		self.ButtonSpacer = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
		self.VBox.pack_start(self.ButtonSpacer, True, False, 8)
		self.VBox.pack_start(self.ButtonAlign, True, False, 8)

	def AnyBoxClicked(self, Checkbox, Key):
		self.Fields[Key].set_sensitive(not Checkbox.get_active())
		
	def StateClicked(self, Button):

		if Button is self.AcceptButton and 'saveclose' in self.Callbacks:
			Callback = self.Callbacks['saveclose']
		elif Button is self.DeleteButton and 'delclose' in self.Callbacks:
			Callback = self.Callbacks['delclose']
		else:
			self.destroy()
			return
			
		Dict = self.Data

		for k in self.Fields:
			if FieldDBTypes[k] == FieldType.TIMEFORMAT:

				if self.Checkboxes[k].get_active():
					Value = '*'
				else:
					Value = self.Fields[k].get_buffer().get_text()

			elif FieldDBTypes[k] == FieldType.TEXT:
				Value = self.Fields[k].get_buffer().get_text()
			elif FieldDBTypes[k] == FieldType.FILEPATH:
				Value = self.Extra[k]
			elif FieldDBTypes[k] == FieldType.BOOLEAN:
				Value = str(int(self.Fields[k].get_active()))
				
			Dict[k] = Value

		Callback[0](Dict, self.OriginalName, *Callback[1:])


		self.destroy()

class Notification(Gtk.Window):
	def __init__(self, Title, Message, AudioFile = None, Loop = False, Callback = None, *CallbackArgs):
		Gtk.Window.__init__(self, title=Title)
		SetWindowIcon(self)
		self.Callback = Callback
		self.CallbackArgs = CallbackArgs
		self.set_default_size(400, 150)
		self.VBox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		self.add(self.VBox)
		
		self.MsgText = Gtk.Label.new(Message)

		self.MsgHBox = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

		self.Icon = Gtk.Image.new_from_icon_name('appointment-soon', Gtk.IconSize.DIALOG)
		
		self.MsgHBox.pack_start(self.Icon, False, True, 8)
		self.MsgHBox.pack_start(self.MsgText, False, True, 8)
		
		MsgHBoxAlign = Gtk.Alignment.new(0.0, 0.0, 0.0, 0.0)
		
		MsgHBoxAlign.add(self.MsgHBox)
		self.VBox.pack_start(MsgHBoxAlign, True, True, 8)

		self.ButtonHBox = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

		self.VBox.pack_start(self.ButtonHBox, True, True, 8)

		SnoozeAlign = Gtk.Alignment.new(0.0, 1.0, 0.0, 0.0)
		DismissAlign = Gtk.Alignment.new(1.0, 1.0, 0.0, 0.0)

		self.SnoozeButton = Gtk.Button.new_with_mnemonic("_Snooze")
		self.SnoozeButton.set_sensitive(False) #Snooze not yet implemented
		self.DismissButton = Gtk.Button.new_with_mnemonic("_Dismiss")
		self.DismissButton.connect('clicked', self.DismissClicked)
		SnoozeAlign.add(self.SnoozeButton)
		DismissAlign.add(self.DismissButton)

		self.ButtonHBox.pack_start(SnoozeAlign, True, True, 8)
		self.ButtonHBox.pack_start(DismissAlign, True, True, 8)
		self.connect('delete-event', self.DismissClicked)
		
		if AudioFile:
			self.Noisemaker = Audio.AudioEvent(AudioFile)
			self.Noisemaker.Play(Loop)
		else:
			self.Noisemaker = None

	def DismissClicked(self, Button = None):
		try:
			self.Noisemaker.Stop()
			del self.Noisemaker
		except:
			pass
		
		self.destroy()

		if self.Callback:
			self.Callback(*self.CallbackArgs)

class BacktraceDialog(Gtk.Window):
	def __init__(self, BacktraceString):
		Gtk.Window.__init__(self, title='Error occurred in Lament Calendar GTK+')
		
		self.VBox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=16)
		self.MsgHBox = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
		
		self.Icon = Gtk.Image.new_from_stock('gtk-dialog-error', Gtk.IconSize.DIALOG)
		self.Label = Gtk.Label.new('An error has occurred in Lament Calendar. This is likely a bug.\n\n' + BacktraceString)
		
		self.MsgHBox.pack_start(self.Icon, False, True, 8)
		self.MsgHBox.pack_start(self.Label, False, True, 8)
		
		
		self.DismissAlign = Gtk.Alignment.new(1.0, 1.0, 0.0, 0.0)
		self.DismissButton = Gtk.Button.new_with_mnemonic('_Exit')
		self.DismissAlign.add(self.DismissButton)
		
		self.VBox.pack_start(self.MsgHBox, True, True, 8)
		self.VBox.pack_start(self.DismissAlign, True, True, 8)
		
		self.DismissButton.connect('clicked', lambda *Discarded : os._exit(1))
		
		self.add(self.VBox)
		
				
class TrayIconObject(Gtk.StatusIcon):
	def __init__(self, MainObj = None):
		Gtk.StatusIcon.__init__(self)
		self.MainObj = MainObj

		NameString = 'Lament Calendar'
		self.set_name(NameString)
		self.set_title(NameString)
		self.set_tooltip_text(NameString)
		
		self.set_from_file('lament.png')
		self.set_visible(True)
		self.set_has_tooltip(True)

		self.connect('activate', self.OnClick)
		
	def OnClick(self, *Unused):
		if not self.MainObj:
			return
		if self.MainObj.is_visible():
			self.MainObj.hide()
		else:
			self.MainObj.show_all()

