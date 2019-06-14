import pygame

pygame.init()
pygame.mixer.init()

class AudioEvent(object):
	CurChannel = -1
	AllocatedChannels = pygame.mixer.get_num_channels()
	NumActive = 0
	
	@classmethod
	def __CheckChannelAlloc(cls):
		if cls.CurChannel > cls.AllocatedChannels:
			pygame.mixer.set_num_channels(cls.AllocatedChannels * 2)

	def __init__(self, AudioFile):
		cls = self.__class__
		
		cls.NumActive += 1
		cls.CurChannel += 1

		cls.__CheckChannelAlloc()
		
		self.ChannelNum = cls.CurChannel
		self.SoundObj = pygame.mixer.Sound(AudioFile)
		self.ChannelDesc = pygame.mixer.Channel(self.ChannelNum)

	def __del__(self):
		self.Stop()
		cls = self.__class__
		
		cls.NumActive -= 1

		if not cls.NumActive:
			pygame.mixer.set_num_channels(8)
			cls.CurChannel = -1
			cls.AllocatedChannels = 8
			
	def Play(self, Loop = False):
		self.ChannelDesc.play(self.SoundObj, -1 if Loop else 0)
		
	def Stop(self):
		if self.ChannelDesc.get_busy():
			self.ChannelDesc.stop()
			
	def Pause(self):
		self.ChannelDesc.pause()

	def Unpause(self):
		self.ChannelDesc.unpause()
