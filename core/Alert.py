import pygame

pygame.init()
pygame.mixer.init()

Silenced = False

class AudioEvent(object):
	CurChannel = -1
	AllocatedChannels = pygame.mixer.get_num_channels()
	NumActive = 0
	
	@classmethod
	def CheckChannelAlloc(cls):
		if cls.CurChannel > cls.AllocatedChannels:
			pygame.mixer.set_num_channels(cls.AllocatedChannels * 2)

	def __init__(self, AudioFile, Loop):
		cls = self.__class__
		
		cls.NumActive += 1
		cls.CurChannel += 1

		cls.CheckChannelAlloc()
		
		self.ChannelNum = cls.CurChannel

		self.SoundObj = pygame.mixer.Sound(AudioFile)
		self.ChannelDesc = pygame.mixer.Channel(self.ChannelNum)
		
		if not Silenced:
			self.ChannelDesc.play(self.SoundObj, -1 if Loop else 0)

	def __del__(self):
		if self.ChannelDesc.get_busy():
			self.ChannelDesc.stop()
		
		cls = self.__class__
		
		cls.NumActive -= 1

		if not cls.NumActive:
			pygame.mixer.set_num_channels(8)
			cls.CurChannel = -1
			cls.AllocatedChannels = 8
	def Pause(self):
		self.ChannelDesc.pause()
	def Unpause(self):
		self.ChannelDesc.unpause()
		

def GetSilenced():
	return Silenced
	
def SetSilenced(State):
	global Silenced
	Silenced = State
