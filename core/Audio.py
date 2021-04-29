import GStreamerAudio

Silenced = False

class AudioEvent(GStreamerAudio.AudioEvent):
	def Play(self, Loop = False):
		if GetSilenced():
			return
		
		for _ in range(0, 3):
			try:
				super().Play(Loop)
				break
			except:
				time.sleep(0.5)
				continue


def GetSilenced():
	return Silenced
	
def SetSilenced(State):
	global Silenced
	Silenced = State

