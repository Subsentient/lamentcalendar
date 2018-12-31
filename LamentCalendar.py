#!/usr/bin/env python3
import sys
sys.path.append('core')
import GUI, DB

Obj = GUI.MainWindow()
Obj.show_all()
DB = DB.DBObject('events.db')
GUI.Gtk.main()
