import PygameAudio

Silenced = False

class AudioEvent(PygameAudio.AudioEvent):
	def Play(self, Loop = False):
		if not GetSilenced():
			PygameAudio.AudioEvent.Play(self, Loop)


def GetSilenced():
	return Silenced
	
def SetSilenced(State):
	global Silenced
	Silenced = State

