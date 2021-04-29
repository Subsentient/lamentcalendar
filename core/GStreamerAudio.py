import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst as gst
gst.init(None)
import threading

class AudioEvent(object):

	def __WatchForLoop(self):
		Bus = self.Player.get_bus()
		
		while not self.ShouldDie:
			Msg = Bus.timed_pop(50)
			
			if not Msg:
				continue
			
			if Msg.type in (gst.MessageType.EOS, gst.MessageType.SEGMENT_DONE):
				self.Player.seek_simple(gst.Format.TIME, gst.SeekFlags.ACCURATE | gst.SeekFlags.FLUSH, 0)
			
	def __init__(self, AudioFile):
		self.Player = gst.ElementFactory.make('playbin', None)
		self.Player.set_property('uri', gst.filename_to_uri(AudioFile))
		self.ShouldDie = False
		self.Thread = None

	def __del__(self):
		self.Player.set_state(gst.State.NULL)
		
		if self.Thread:
			self.ShouldDie = True
			self.Thread.join()

	def Play(self, Loop = False):
		self.Player.set_state(gst.State.PLAYING)

		if not Loop:
			return
			
		if not self.Thread:
			self.Thread = threading.Thread(target=self.__WatchForLoop)
			
			self.Thread.start()

	def Stop(self):
		self.Player.set_state(gst.State.READY)
		
		if self.Thread:
			self.ShouldDie = True
			self.Thread.join()
			self.Thread = None

	def Pause(self):
		self.Player.set_state(gst.State.PAUSED)

	def Unpause(self):
		self.Player.set_state(gst.State.PLAYING)

