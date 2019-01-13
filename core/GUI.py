import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
import sys, os

Weekdays = { 0 : 'Sun', 1 : 'Mon', 2 : 'Tue', 3 : 'Wed', 4 : 'Thu', 5 : 'Fri', 6 : 'Sat' }

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

		self.FileMenu.append(self.NewEventItem)
		self.FileMenu.append(self.QuitItem)


		#Configure calendar display.
		self.Calendar = Gtk.Calendar()
		self.Calendar.connect('day-selected-double-click', self.DayClicked)

		#Add it all in
		self.VBox.pack_start(self.MenuBarAlign, False, True, 0)
		self.VBox.pack_start(self.Calendar, True, True, 0)

	def TerminateApp(self, Widget):
		sys.exit(0)
	def NewClicked(self, Widget):
		if 'newitem' in self.Callbacks:
			self.Callbacks['newitem'][0](*self.Callbacks['newitem'][1:])

	def DayClicked(self, Calendar):
		assert Calendar is self.Calendar
		Year, Month, Day = Calendar.get_date()
		Month += 1

		if 'dayclick' in self.Callbacks:
			self.Callbacks['dayclick'][0](Year, Month, Day, *self.Callbacks['dayclick'][1:])
			
	def MarkDay(self, Day):
		self.Calendar.mark_day(Day)

	def UnmarkDay(self, Day):
		self.Calendar.unmark_day(Day)

class DayView(Gtk.Window):
	def __init__(self, Year, Month, Day, DayList, Callbacks={}):
		self.Callbacks = Callbacks

		self.Year, self.Month, self.Day = Year, Month, Day
		
		Gtk.Window.__init__(self, title='Lamentations of ' + str(Year) + '-' +\
		DoubleDigitFormat(str(Month)) + '-' + \
		DoubleDigitFormat(str(Day)))
		SetWindowIcon(self)

		self.set_default_size(500, 300)
		self.VBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
		self.add(self.VBox)
		
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

		DateString = '<span foreground="#00cccc">Y: </span>' + DoubleDigitFormat(Value['year']) + ' ' + \
					'<span foreground="#00cc00">M: </span>' + DoubleDigitFormat(Value['month']) + ' ' +\
					'<span foreground="#cccc00">D: </span>' + DoubleDigitFormat(Value['day']) + '   ' + \
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
		self.show_all()
		
class EventView(Gtk.Window):
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

		self.Data = EventDict
		#Populate fields
		for k in EventDict:
			self.ItemLabels[k] = Gtk.Label.new(k.capitalize())
			self.Fields[k] = Gtk.Entry.new_with_buffer(Gtk.EntryBuffer.new(EventDict[k], -1))
			self.HBoxes[k] = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
			self.HBoxes[k].pack_start(self.ItemLabels[k], True, False, 8)

			IsNameField = k == 'name'
			
			self.HBoxes[k].pack_start(self.Fields[k], IsNameField, IsNameField, 8)

			self.VBox.pack_start(self.HBoxes[k], True, True, 8)

			if IsNameField:
				self.VBox.pack_start(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), True, True, 8)
				continue
	
			self.Checkboxes[k] = Gtk.CheckButton().new_with_label("All")
			
			if EventDict[k] == '*':
				self.Checkboxes[k].set_active(True)
				self.AnyBoxClicked(self.Checkboxes[k], k)
			
			self.HBoxes[k].pack_start(self.Checkboxes[k], False, False, 0)
			self.Checkboxes[k].connect('toggled', self.AnyBoxClicked, k)
			
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
			Value = self.Fields[k].get_buffer().get_text()

			if k != 'name':
				if self.Checkboxes[k].get_active(): Value = '*'
				
			Dict[k] = Value

		Callback[0](Dict, self.OriginalName, *Callback[1:])


		self.destroy()

