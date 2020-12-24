import PygameAudio

Silenced = False

class AudioEvent(PygameAudio.AudioEvent):
	def Play(self, Loop = False):
		if GetSilenced():
			return
		
		for _ in range(0, 3):
			try:
				PygameAudio.AudioEvent.Play(self, Loop)
				break
			except:
				time.sleep(0.5)
				continue


def GetSilenced():
	return Silenced
	
def SetSilenced(State):
	global Silenced
	Silenced = State

