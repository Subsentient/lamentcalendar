#!/usr/bin/env python3
import sys, time
sys.path.append('core')
import GtkGUI, DB, Audio, DateCalc
import signal

class PrimaryLoopObj(GtkGUI.MainWindow):
	DB_FILEPATH = 'events.db'
	
	def __init__(self):
		GtkGUI.MainWindow.__init__(self, {'monthchanged' : (self.OnMonthChange,),
										'dayclick': (self.OnDayClick,),
										'newitem' : (self.NewItemClicked,),
										'listallclicked' : (self.OnListAllClick,),
										'sendtotrayclicked' : (self.OnSendToTrayClick,),
										'reloaddbclicked' : (self.OnReloadDBClick,) }
								)
		Dates = [*self.Calendar.get_date()]
		Dates[1] += 1
		
		self.DB = DB.DBObject(PrimaryLoopObj.DB_FILEPATH)

		self.OnMonthChange(*Dates)
		self.Notifications = {}

		signal.signal(signal.SIGUSR1, self.SilenceSignalHandler)
		signal.signal(signal.SIGUSR2, self.DismissAllSignalHandler)
		signal.signal(signal.SIGTERM, lambda dis, carded : sys.exit(0))
		signal.signal(signal.SIGINT, lambda dis, carded : sys.exit(0))

if '--silence' in sys.argv:
	Audio.SetSilenced(True)
		
MainObj = PrimaryLoopObj()

if '--tray' not in sys.argv:
	MainObj.show_all()

TrayIcon = GtkGUI.TrayIconObject(MainObj)

GtkGUI.GLib.timeout_add(200, MainObj.DB.CheckTriggers, MainObj.SpawnNotification)

GtkGUI.Gtk.main()