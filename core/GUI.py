import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
import sys, os

def SetWindowIcon(Window):
	Window.set_icon(GdkPixbuf.Pixbuf.new_from_file('lament.png'))
	
def DoubleDigitFormat(String):
	List = String.split(',')

	for Inc, Item in enumerate(List):
		List[Inc] = '0' + Item if len(Item) == 1 and Item != '*' else Item

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

	def DayClicked(self, Calendar):
		assert Calendar is self.Calendar
		Year, Month, Day = Calendar.get_date()
		Month += 1

		if 'dayclick' in self.Callbacks:
			self.Callbacks['dayclick'](Year, Month, Day)
			
	def MarkDay(self, Day):
		self.Calendar.mark_day(Day)

	def UnmarkDay(self, Day):
		self.Calendar.unmark_day(Day)

class DayView(Gtk.Window):
	def __init__(self, Year, Month, Day, DayList, Callbacks={}):
		
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
			Label = Gtk.Label(Value['name'])
			
			HBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
			
			HBox.pack_start(Label, False, False, 4)
			HBox.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 4)

			TimeString = DoubleDigitFormat(Value['hours']) + ':' + DoubleDigitFormat(Value['minutes'])
			
			HBox.pack_start(Gtk.Label(TimeString), False, False, 0)
			HBox.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, 8)
			
			Button = Gtk.Button.new_with_label("Edit/View")
			ButtonAlign = Gtk.Alignment.new(1.0, 1.0, 0.0, 1.0)
			ButtonAlign.add(Button)
			
			if 'editclicked' in Callbacks:
				Button.connect('clicked', Callbacks['editclicked'][0], Callbacks['editclicked'][1], Value['name'])
			
			HBox.pack_start(ButtonAlign, True, True, 0)

			
			self.WindowViewBox.pack_start(HBox, True, False, 0)
			self.WindowViewBox.pack_start(Gtk.Separator(), False, True, 0)


		
		

class EventView(Gtk.Window):
	def __init__(self, EventDict, OnCompleteFunc=None, OnCompleteData=None):
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
		self.AcceptButton = Gtk.Button.new_with_mnemonic('_Accept')
		self.CancelButton = Gtk.Button.new_with_mnemonic('_Cancel')
		self.AcceptButton.connect('clicked', self.StateClicked, OnCompleteFunc, OnCompleteData)
		self.CancelButton.connect('clicked', self.StateClicked, OnCompleteFunc, OnCompleteData)

		self.ButtonAlign = Gtk.Alignment.new(1.0, 1.0, 0.1, 1.0)
		self.ButtonHBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
		self.ButtonHBox.add(self.CancelButton)
		self.ButtonHBox.add(self.AcceptButton)
		self.ButtonAlign.add(self.ButtonHBox)
		self.ButtonSpacer = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
		self.VBox.pack_start(self.ButtonSpacer, True, False, 8)
		self.VBox.pack_start(self.ButtonAlign, True, False, 8)

	def AnyBoxClicked(self, Checkbox, Key):
		self.Fields[Key].set_sensitive(not Checkbox.get_active())
		
	def StateClicked(self, Button, OnCompleteFunc, OnCompleteData):
		NeedUserFunc = Button is self.AcceptButton

		Dict = self.Data

		if not NeedUserFunc or not OnCompleteFunc:
			self.destroy()
			return

		for k in self.Fields:
			Value = self.Fields[k].get_buffer().get_text()

			if k != 'name':
				if self.Checkboxes[k].get_active(): Value = '*'
				
			Dict[k] = Value

		if OnCompleteData:
			OnCompleteFunc(Dict, OnCompleteData)
		else:
			OnCompleteFunc(Dict)

		self.destroy()

if __name__ == '__main__': #For debugging
	EventView({'name':'wibble derp', 'derp':'4444'}, sys.exit).show_all()
	Gtk.main()
