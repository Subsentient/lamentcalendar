import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import sys, os

class MainWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title='Lament Calendar')
		
		self.set_default_size(640, 480)
		self.connect('destroy', self.TerminateApp)
		
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
		
		self.Calendar = Gtk.Calendar()
		self.Calendar.connect('day-selected-double-click', self.DayClicked)
		
		self.VBox.pack_start(self.MenuBarAlign, False, True, 0)
		self.VBox.pack_start(self.Calendar, True, True, 0)
		
	def TerminateApp(self, Widget):
		sys.exit(0)
	def DayClicked(self, Calendar):
		Year, Month, Day = Calendar.get_date()
		Month += 1
		ViewWindow = DayView(Month, Day, Year)
		ViewWindow.show_all()

class DayView(Gtk.Window):
	def __init__(self, Month, Day, Year):
		Gtk.Window.__init__(self, title='Lamentations of ' + str(Year) + '-' + str(Month) + '-' + str(Day))
	
