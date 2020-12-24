#!/usr/bin/env python3
import sys, time
sys.path.append('core')
import GtkGUI, DB, Audio, DateCalc
import signal, traceback

def ExceptionDialogSpawner(Type, Value, Traceback):
	TracebackString = ''.join(traceback.format_exception(Type, Value, Traceback))
	
	print(TracebackString)
	
	BTDialog = GtkGUI.BacktraceDialog(TracebackString)
	BTDialog.show_all()
	
	GtkGUI.Gtk.main()
	
def RunGTKApp():
	sys.excepthook = ExceptionDialogSpawner
	
	if '--silence' in sys.argv:
		Audio.SetSilenced(True)
	
	MainObj = GtkGUI.MainWindow()
	
	if '--tray' not in sys.argv:
		MainObj.show_all()
	
	TrayIcon = GtkGUI.TrayIconObject(MainObj)
	
	signal.signal(signal.SIGUSR1, MainObj.SilenceSignalHandler)
	signal.signal(signal.SIGUSR2, MainObj.DismissAllSignalHandler)
	signal.signal(signal.SIGTERM, lambda *Discarded : sys.exit(0))
	signal.signal(signal.SIGINT, lambda *Discarded : sys.exit(0))

	GtkGUI.GLib.timeout_add(200, lambda *Discarded : MainObj.DB.CheckTriggers(MainObj.SpawnNotification) or True)
	GtkGUI.GLib.timeout_add(10000, lambda *Discarded : MainObj.DB.CheckReload() or True)
	
	GtkGUI.Gtk.main()

RunGTKApp()
