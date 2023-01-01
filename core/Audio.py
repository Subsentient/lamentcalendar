import GStreamerAudio
import time, traceback, os
from __main__ import __file__ as MainDir
Silenced = False
AlarmSound = f'{os.path.dirname(os.path.realpath(MainDir))}{os.sep}alarm.ogg'

class AudioEvent(GStreamerAudio.AudioEvent):
	def Play(self, Loop = False):
		if GetSilenced():
			return
		
		for _ in range(0, 3):
			try:
				super().Play(Loop)
				break
			except:
				traceback.print_exc()
				time.sleep(0.5)
				continue


def GetSilenced():
	return Silenced
	
def SetSilenced(State):
	global Silenced
	Silenced = State

