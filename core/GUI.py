import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gtk, GdkPixbuf, GLib
import sys, os

from DB import Fields, FieldType

import Alert
from datetime import date

Weekdays = { 0 : 'Sun', 1 : 'Mon', 2 : 'Tue', 3 : 'Wed', 4 : 'Thu', 5 : 'Fri', 6 : 'Sat' }

def GetWeekdayFromDate(Year, Month, Day):
	WDay = date(Year, Month, Day).weekday()
	
	WeekdayCalc = WDay + 1 if WDay < 6 else 0

	return WeekdayCalc
	
def SetWindowIcon(Window):
	Window.set_icon(GdkPixbuf.Pixbuf.new_from_file('lament.png'))
	
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

class MainWindow(Gtk.Window):
	def __init__(self, Callbacks={}): #Yes, the same static-initialized list is indeed what we want.
		self.Callbacks = Callbacks
		
		Gtk.Window.__init__(self, title='Lament Calendar')

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

		#Populate file menu
		self.QuitItem = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_QUIT)
		self.QuitItem.connect('activate', self.TerminateApp)
		self.NewEventItem = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_NEW)
		self.NewEventItem.set_label("New Event")
		self.NewEventItem.connect('activate', self.NewClicked)
		
		self.AllEventsItem = Gtk.MenuItem.new_with_mnemonic('List _all events')
		self.AllEventsItem.connect('activate', self.ListAllClicked)
		self.FileMenu.append(self.NewEventItem)
		self.FileMenu.append(self.AllEventsItem)
		self.FileMenu.append(self.QuitItem)


		#Configure calendar display.
		self.Calendar = Gtk.Calendar()
		self.Calendar.connect('day-selected-double-click', self.DayClicked)
		self.Calendar.connect('month-changed', self.MonthChanged)
		
		#Add it all in
		self.VBox.pack_start(self.MenuBarAlign, False, True, 0)
		self.VBox.pack_start(self.Calendar, True, True, 0)

	def TerminateApp(self, Widget):
		sys.exit(0)
		
	def ListAllClicked(self, Widget):
		if 'listallclicked' in self.Callbacks:
			self.Callbacks['listallclicked'][0]('*', '*', '*', *self.Callbacks['listallclicked'][1:])
			
	def NewClicked(self, Widget):
		if 'newitem' in self.Callbacks:
			self.Callbacks['newitem'][0](*self.Callbacks['newitem'][1:])

	def DayClicked(self, Calendar):
		assert Calendar is self.Calendar
		Year, Month, Day = Calendar.get_date()
		Month += 1

		if 'dayclick' in self.Callbacks:
			self.Callbacks['dayclick'][0](Year, Month, Day, *self.Callbacks['dayclick'][1:])

	def MonthChanged(self, Calendar):
		assert Calendar is self.Calendar
		
		if 'monthchanged' in self.Callbacks:
			
			Dates = [*self.Calendar.get_date()]
			Dates[1] += 1 #Change month to 1 to 12 instead of 0 to 11
			
			self.Callbacks['monthchanged'][0](*Dates, *self.Callbacks['monthchanged'][1:])
		
	def MarkDay(self, Day):
		self.Calendar.mark_day(Day)

	def UnmarkDay(self, Day):
		self.Calendar.unmark_day(Day)

class DayView(Gtk.Window):
	def __init__(self, Year, Month, Day, DayList, Callbacks={}):
		self.Callbacks = Callbacks

		self.Year, self.Month, self.Day = Year, Month, Day
		
		Gtk.Window.__init__(self, title='Events for ' + str(Year) + '-' +\
		DoubleDigitFormat(str(Month)) + '-' + \
		DoubleDigitFormat(str(Day)))
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
		
		WindowViewAlign = Gtk.Alignment.new(0.0, 0.0, 1.0, 1.0)
		WindowViewAlign.add(self.WindowView)
		self.VBox.pack_start(WindowViewAlign, True, True, 8)
		
		self.WindowViewBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		
		self.WindowView.add(self.WindowViewBox)
		
		for Value in DayList:
			self.AddItem(Value)

	def AddItem(self, Value):
		Label = Gtk.Label.new()

		Label.set_markup('<i>' + Value['name'] + '</i>')
		
		HBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
		
		HBox.pack_start(Label, False, False, 4)
		HBox.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 4)
	
		TimeString = DoubleDigitFormat(Value['hours']) + ':' + DoubleDigitFormat(Value['minutes'])
		
		HBox.pack_start(Gtk.Label(TimeString), False, False, 0)
		HBox.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 8)

		DateString = '<span foreground="#00cccc">' + DoubleDigitFormat(Value['year']) + '</span>-' + \
					'<span foreground="#00cc00">' + DoubleDigitFormat(Value['month']) + '</span>-' +\
					'<span foreground="#cccc00">' + DoubleDigitFormat(Value['day']) + '</span>   ' + \
					'<b>' + WeekdayFormat(Value['weekday']) + '</b>'

		DateLabel = Gtk.Label.new()
		DateLabel.set_markup(DateString)
		
		HBox.pack_start(DateLabel, False, False, 0)
		HBox.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 8)
		
		Button = Gtk.Button.new_with_label("Edit/View")
		ButtonAlign = Gtk.Alignment.new(1.0, 1.0, 0.0, 1.0)
		ButtonAlign.add(Button)
		
		if 'editclicked' in self.Callbacks:
			Button.connect('clicked', self.Callbacks['editclicked'][0], Value['name'], self, *self.Callbacks['editclicked'][1:])

		HBox.pack_start(ButtonAlign, True, True, 0)
	
		
		self.WindowViewBox.pack_start(HBox, True, False, 0)
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
		
		if Fields[k] == FieldType.TEXT or Fields[k] == FieldType.TIMEFORMAT:
			self.Fields[k] = Gtk.Entry.new_with_buffer(Gtk.EntryBuffer.new(self.Data[k], -1))

			IsText = Fields[k] == FieldType.TEXT
			
			self.HBoxes[k].pack_start(self.Fields[k], IsText, IsText, 8)
			
		elif Fields[k] == FieldType.FILEPATH:
			Filename = self.Data[k] if self.Data[k] != 'null' else 'null'
			self.Fields[k] = Gtk.Button.new_with_label(Filename if len(Filename) < 25 else Filename[:20] + '...')
			self.Fields[k].connect('clicked', self.RunChooser, k)
			self.Extra[k] = Filename
			self.HBoxes[k].pack_start(self.Fields[k], True, False, 8)

		elif Fields[k] == FieldType.BOOLEAN:
			self.Fields[k] = Gtk.CheckButton.new()

			self.HBoxes[k].pack_start(self.Fields[k], True, False, 8)
			
		#Time formats also have a checkbox.
		if Fields[k] == FieldType.TIMEFORMAT:
			self.Checkboxes[k] = Gtk.CheckButton().new_with_label("All")
			
			self.HBoxes[k].pack_start(self.Checkboxes[k], False, False, 8)


	def __init__(self, EventDict, Callbacks={}):
		assert 'name' in EventDict
		
		self.OriginalName = EventDict['name']
		self.Callbacks = Callbacks
		
		Gtk.Window.__init__(self, title='Event "' + EventDict['name'] + '"')
		
		SetWindowIcon(self)

		self.set_resizable(False)
		self.VBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		self.add(self.VBox)

		self.MainLabel = Gtk.Label.new('Configuration for event "' + EventDict['name'] + '":')

		self.VBox.pack_start(self.MainLabel, False, True, 8)

		self.HBoxes = {}
		self.Fields = {}
		self.Checkboxes = {}
		self.ItemLabels = {}
		self.Extra = {}
		
		self.Data = EventDict
		#Populate fields
		for k in EventDict:
			self.ItemLabels[k] = Gtk.Label.new(k.replace('_', ' ').capitalize())
			self.HBoxes[k] = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

			LabelAlign = Gtk.Alignment.new(0.0, 0.0, 0.1, 1.0)
			LabelAlign.add(self.ItemLabels[k])
			
			self.HBoxes[k].pack_start(LabelAlign, True, True, 8)

			self.__CreateField(k)

			self.VBox.pack_start(self.HBoxes[k], True, True, 8)

			#Name field needs a separator
			if Fields[k] == FieldType.TEXT:
				self.VBox.pack_start(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), True, True, 8)
				continue
				
			#Time fields need a checkbox
			if Fields[k] == FieldType.TIMEFORMAT:
				if EventDict[k] == '*':
					self.Checkboxes[k].set_active(True)
					self.AnyBoxClicked(self.Checkboxes[k], k)
			
				self.HBoxes[k].pack_start(self.Checkboxes[k], False, False, 0)
				self.Checkboxes[k].connect('toggled', self.AnyBoxClicked, k)

			if Fields[k] == FieldType.BOOLEAN:
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
			if Fields[k] == FieldType.TIMEFORMAT:

				if self.Checkboxes[k].get_active():
					Value = '*'
				else:
					Value = self.Fields[k].get_buffer().get_text()

			elif Fields[k] == FieldType.TEXT:
				Value = self.Fields[k].get_buffer().get_text()
			elif Fields[k] == FieldType.FILEPATH:
				Value = self.Extra[k]
			elif Fields[k] == FieldType.BOOLEAN:
				Value = str(int(self.Fields[k].get_active()))
				
			Dict[k] = Value

		Callback[0](Dict, self.OriginalName, *Callback[1:])


		self.destroy()

class Notification(Gtk.Window):
	def __init__(self, Title, Message, AudioFile = None, Loop = False, **Extra):
		Gtk.Window.__init__(self, title=Title)
		SetWindowIcon(self)
		
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
		self.DismissButton.connect('clicked', self.__class__.DismissClicked, self, Extra)
		SnoozeAlign.add(self.SnoozeButton)
		DismissAlign.add(self.DismissButton)

		self.ButtonHBox.pack_start(SnoozeAlign, True, True, 8)
		self.ButtonHBox.pack_start(DismissAlign, True, True, 8)

		if AudioFile:
			self.AlertObject = Alert.AudioEvent(AudioFile, Loop)
		else:
			self.AlertObject = None

	@staticmethod
	def DismissClicked(Button, ForcedSelf, Extra):
		del ForcedSelf.AlertObject
		
		ForcedSelf.destroy()

		if 'callback' in Extra:
			Extra['callback'](**Extra)


