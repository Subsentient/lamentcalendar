import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst as gst
gst.init(None)

class AudioEvent(object):

	def __init__(self, AudioFile):
		self.Player = gst.ElementFactory.make('playbin', None)
		self.Player.set_property('uri', gst.filename_to_uri(AudioFile))

	def __del__(self):
		self.Stop()

	def Play(self, Loop = False):
		self.Player.set_state(gst.State.PLAYING)

	def Stop(self):
		self.Player.set_state(gst.State.READY)

	def Pause(self):
		self.Player.set_state(gst.State.PAUSED)

	def Unpause(self):
		self.Play()

